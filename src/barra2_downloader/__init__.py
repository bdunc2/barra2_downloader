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

"""
    rate_limiter_delay: The time (seconds) to wait between data downloads (for rate limiting)
    verbose: Whether or not to print out status updates
"""
def get_df_for_data(
        model: model_domains.BARRAModel, 
        domain: model_domains.BARRADomain, 
        frequency: model_domains.BARRAFrequency, 
        var: str,
        time_start: int | float | datetime,
        time_end: int | float | datetime,
        latitude: float | None = None,
        longitude: float | None = None,
        bbox: url_builder.BBox | None = None,
        rate_limiter_delay: float = 0.25,
        verbose: bool = False
    ):
    if ((latitude is None) or (longitude is None)) and (bbox is None):
        raise ValueError("Require one of latitude/longitude or bbox")

    if (bbox is not None):
        raise NotImplementedError("BBox is currently not implemented -> GeoPandas df / netcdf stuff will be done soon. Currently single point")

    mdf = (model, domain, frequency)
    if not params.check_valid_pairing(var, mdf):
        raise ValueError(f"parameter {var} is not available for {model.value}/{domain.value}/{frequency.value}")

    data_times = get_months_spanning(time_start, time_end)
    if verbose:
        print (f"Have to make {len(data_times)} requests to get requested data")

    # Start iterating the data
    df = None
    for idx, (month, year) in enumerate(data_times):
        s_dt, e_dt = data_times[month, year]

        url = url_builder.get_url(
            model, 
            domain, 
            frequency, 
            var, 
            month, 
            year, 
            latitude=latitude, 
            longitude=longitude, 
            bbox=bbox, 
            time_start=s_dt, 
            time_end=e_dt, 
            out_format=url_builder.BARRA2OutputFormat.CSV
        )

        if verbose:
            print (f"Downloading #{idx: 03d} [{(idx / len(data_times)) * 100:03.1f} %] from {url}")

        with requests.get(url, stream=True) as resp:
            resp.raise_for_status()
            c_df = pd.read_csv(resp.raw)

        if df is None:
            df = c_df
        else:
            df = pd.concat((df, c_df))

        if idx != len(data_times) - 1:
            print (f"Sleeping {rate_limiter_delay:.2f} seconds to avoid rate limiter")
            time.sleep(rate_limiter_delay)

    df.reset_index(drop=True, inplace=True)
    return df


if __name__ == "__main__":
    print (get_df_for_data(
        model_domains.BARRAModel.BARRA_C2,
        model_domains.BARRADomain.AUST_04,
        model_domains.BARRAFrequency.hour,
        "tasmax",
        datetime(2026, 3, 4, 13, 45, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 25, 0, 0, 0, tzinfo=timezone.utc),
        latitude=-26.52267239,
        longitude=152.573373,
        verbose=True
    ))