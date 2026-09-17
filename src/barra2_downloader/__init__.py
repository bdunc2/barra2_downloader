try:
    from . import model_domains
    from . import params
    from . import url_builder
except:
    import model_domains
    import params
    import url_builder

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import requests
import time
import traceback
import concurrent.futures

"""
    Returns a dictionary with keys being a tuple of (month [int], year [int]) and value being a tuple of (s_dt, e_dt) being the start and end datetimes within that month. All sections joined together should consistute a continuous block from time_start to time_end

    If time_start (or time_end) are given as int or float they are assumed to be UTC UNIX timestamps (seconds since 00:00:00 1 Jan 1970 UTC)
"""
def get_months_spanning(
        time_start: int | float | datetime,
        time_end: int | float | datetime
    ):

    # Convert to datetime objects
    if type(time_start) != datetime:
        # Convert timestamp to datetime (assume to be UTC)
        time_start = datetime.fromtimestamp(time_start, tz=timezone.utc)
    if type(time_end) != datetime:
        # Convert timestamp to datetime (assume to be UTC)
        time_end = datetime.fromtimestamp(time_end, tz=timezone.utc)

    if time_end < time_start:
        raise ValueError("time_end should be equal to or after time_start")

    c_period = (time_start.month, time_start.year)
    e_period = (time_end.month, time_end.year)

    c_dt = time_start

    times = {}

    while True:
        if c_period == e_period:
            # Good, all done now
            times[c_period] = (c_dt, time_end)
            break
        # Ok, get to the end of the current month
        n_year = c_period[1]
        n_month = c_period[0] + 1
        if n_month > 12:
            n_month = 1
            n_year += 1
        end_dt = datetime(n_year, n_month, 1, 0, 0, 0, tzinfo=timezone.utc)

        times[c_period] = (c_dt, end_dt)
        c_period = (n_month, n_year)
        c_dt = end_dt

    return times

def _download_df(url):
    try:
        with requests.get(url, stream=True) as resp:
            resp.raise_for_status()
            c_df = pd.read_csv(resp.raw)
    except:
        print (f"Failed to download from url: {url}")
        traceback.print_exc()
        return None
    return c_df

"""
    rate_limiter_delay: The time (seconds) to wait between data downloads (for rate limiting)
    verbose: Whether or not to print out status updates
"""
def get_df_for_data(
        model: model_domains.BARRAModel, 
        domain: model_domains.BARRADomain, 
        frequency: model_domains.BARRAFrequency, 
        var: str | list[str],
        time_start: int | float | datetime,
        time_end: int | float | datetime,
        latitude: float | None = None,
        longitude: float | None = None,
        bbox: url_builder.BBox | None = None,
        rate_limiter_delay: float = 0.25,
        verbose: bool = False,
        threaded_download: bool = False,
        max_threads: int = 3
    ):
    if ((latitude is None) or (longitude is None)) and (bbox is None):
        raise ValueError("Require one of latitude/longitude or bbox")

    if (bbox is not None):
        raise NotImplementedError("BBox is currently not implemented -> GeoPandas df / netcdf stuff will be done soon. Currently single point")

    if type(var) == str:
        var = [var] # Just make it a list

    mdf = (model, domain, frequency)
    for v in var:
        if not params.check_valid_pairing(v, mdf):
            raise ValueError(f"parameter {v} is not available for {model.value}/{domain.value}/{frequency.value}")

    data_times = get_months_spanning(time_start, time_end)
    if verbose:
        print (f"Have to make {len(data_times)} requests to get requested data")

    # Build the urls
    urls = []
    for v in var:
        for month, year in data_times:
            s_dt, e_dt = data_times[month, year]

            urls.append(
                url_builder.get_url(
                    model, 
                    domain, 
                    frequency, 
                    v, 
                    month, 
                    year, 
                    latitude=latitude, 
                    longitude=longitude, 
                    bbox=bbox, 
                    time_start=s_dt, 
                    time_end=e_dt, 
                    out_format=url_builder.BARRA2OutputFormat.CSV
                )
            )

    dfs = []
    if threaded_download:
        if verbose:
            print (f"Starting threaded download with {max_threads} threads")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            dfs = list(executor.map(_download_df, urls))
    else:
        if verbose:
            print (f"Starting serial download (with sleeping for rate limiter avoidance)")
        
        for idx, url in enumerate(urls):
            if verbose:
                print (f"Downloading #{idx: 03d} [{(idx / len(urls)) * 100:03.1f} %] from {url}")
    
            dfs.append(_download_df(url))

            if idx != len(urls) - 1:
                print (f"Sleeping {rate_limiter_delay:.2f} seconds to avoid rate limiter")
                time.sleep(rate_limiter_delay)

    if verbose:
        print (f"Concatenating {len(dfs)} files into 1 df")

    # TODO: Make it so that with multiple variables, we join it into single lines
    var_dfs = {}
    for c_df in dfs:
        if c_df is None:
            continue # Failed to download it!!!

        # Get the variable (i.e. the header)
        var_header = c_df.columns[-1]
        if var_header not in var_dfs:
            var_dfs[var_header] = c_df # Done
        else:
            var_dfs[var_header] = pd.concat((var_dfs[var_header], c_df))

    if verbose:
        print ("Joining all the variable dataframes together, whilst converting the time string to timestamp type")
    df = None
    for var_name in var_dfs:
        var_dfs[var_name]["time"] = pd.to_datetime(var_dfs[var_name]["time"])
        if df is None:
            df = var_dfs[var_name]
        else:
            col_sel = ["time", var_dfs[var_name].columns[-1]] # Should just be time and the actual variable (don't need to repeat station / lat / lon)
            df = pd.merge(df, var_dfs[var_name][col_sel], on='time', how='outer') # Join in everything (allow new times such as temp as they are halfway points)

    df.reset_index(drop=True, inplace=True)
    if verbose:
        print ("Ordering the dataframe based on the time")
    
    df.sort_values(by='time', inplace=True)
    df.reset_index(drop=True, inplace=True)

    if verbose:
        print (f"Retrieved a dataframe of shape {df.shape}")

    return df