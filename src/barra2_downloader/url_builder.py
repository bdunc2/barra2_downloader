import model_domains

def _base_url_builder(
        model: model_domains.BARRAModel, 
        domain: model_domains.BARRADomain, 
        frequency: model_domains.BARRAFrequency, 
        var: str,
        month: int,
        year: int):
    return f"https://thredds.nci.org.au/thredds/ncss/grid/ob53/output/reanalysis/{domain.value}/BOM/ERA5/historical/hres/{model.value}/v1/{frequency.value}/{var}/latest/{var}_{domain.value}_ERA5_historical_hres_BOM_{model.value}_v1_{frequency.value}_{year}{month:02d}-{year}{month:02d}.nc"

"""
    Additional URL params:
        DOCUMENTATION: https://docs.unidata.ucar.edu/tds/current/userguide/netcdf_subset_service_ref.html
        SOURCE: '?var={var}&latitude={latitude}&longitude={longitude}'
                '&time_start={time_start_str}&time_end={time_end_str}'
                '&timeStride=&vertCoord='
                '&accept={fileout_type}'
        
        - var: The variable
        - latitude: Degrees of latitude to instigate
        - longitude: Degrees of longitude to instigate
        - time_start: ISO format string (+Z at end) -> e.g. 2007-03-29T12:00:00Z
        - time_end: ISO format string (+Z at end) -> e.g. 2007-03-29T12:00:00Z
        - timeStride: ???
        - vertCoord: ??? Assume its the vertical coordinate
        - accept: The type of file output ('csv' gives it as csv)
                  Accepted values for these are:
                    - csv
                    - xml
                    - netCDF (or netCDF3)
                    - netCDF4 (or netCDF4-classic)
                    - netCDF4ext
                    - WaterML2
"""