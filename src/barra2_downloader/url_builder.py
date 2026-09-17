try:
    from . import model_domains
except:
    import model_domains
from enum import Enum
from datetime import datetime, timezone, timedelta

class BARRA2OutputFormat(Enum):
    CSV = "csv"
    XML = "xml"
    NETCDF = "netCDF"
    NETCDF3 = "netCDF3"
    NETCDF4 = "netCDF4"
    NETCDF4_CLASSIC = "netCDF4-classic"
    NETCDF4_EXT = "netCDF4ext"

class BBox(object):
    def __init__(self, east, west, north, south):
        if (type(east) not in (float, int)) or \
            (type(west) not in (float, int)) or \
            (type(north) not in (float, int)) or \
            (type(south) not in (float, int)):
            raise ValueError("Invalid value given for inputs to BBox. Please ensure all values are floats or ints")

        # Check order
        if north < south:
            raise ValueError("south must be less than or equal to north")
        if east < west:
            raise ValueError("west must be less than or equal to east")

        # Check values
        if (south < -90) or (north > 90):
            raise ValueError("south/north coordinates must be between -90 and 90")
        
        self._east = east
        self._west = west
        self._north = north
        self._south = south

    def get_coords(self):
        return (self._east, self._west, self._north, self._south)

def _base_url_builder(
        model: model_domains.BARRAModel, 
        domain: model_domains.BARRADomain, 
        frequency: model_domains.BARRAFrequency, 
        var: str,
        month: int,
        year: int
    ):
    return f"https://thredds.nci.org.au/thredds/ncss/grid/ob53/output/reanalysis/{domain.value}/BOM/ERA5/historical/hres/{model.value}/v1/{frequency.value}/{var}/latest/{var}_{domain.value}_ERA5_historical_hres_BOM_{model.value}_v1_{frequency.value}_{year}{month:02d}-{year}{month:02d}.nc"

def _coordinate_builder(
        latitude: float | None = None,
        longitude: float | None = None,
        bbox: BBox | None = None
    ):

    vals = {}
    if (latitude is not None) and (longitude is not None):
        vals = {
            "latitude": latitude,
            "longitude": longitude
        }
    elif (bbox is not None):
        east, west, north, south = bbox.get_coords()
        vals = {
            "east": east,
            "west": west,
            "north": north,
            "south": south
        }
    
    return vals

def _time_builder(
        time_start: int | float | datetime | None = None,
        time_end: int | float | datetime | None = None
    ):
    vals = {}

    if (time_start is not None) and (time_end is not None):
        # Need both a start and end
        if type(time_start) not in (int, float, datetime):
            return {}
        if type(time_end) not in (int, float, datetime):
            return {}

        if type(time_start) != datetime:
            # Convert timestamp to datetime (assume to be UTC)
            time_start = datetime.fromtimestamp(time_start, tz=timezone.utc)
            pass
        if type(time_end) != datetime:
            # Convert timestamp to datetime (assume to be UTC)
            time_end = datetime.fromtimestamp(time_end, tz=timezone.utc)

        vals = {
            "time_start": time_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "time_end": time_end.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    return vals

def get_url(
        model: model_domains.BARRAModel, 
        domain: model_domains.BARRADomain, 
        frequency: model_domains.BARRAFrequency, 
        var: str,
        month: int,
        year: int,
        latitude: float | None = None,
        longitude: float | None = None,
        bbox: BBox | None = None,
        time_start: int | float | datetime | None = None,
        time_end: int | float | datetime | None = None,
        out_format: BARRA2OutputFormat | None = None
    ):

    base_url = _base_url_builder(model, domain, frequency, var, month, year)

    var_params = {"var": var}
    var_params = var_params | _coordinate_builder(latitude=latitude, longitude=longitude, bbox=bbox)
    var_params = var_params | _time_builder(time_start=time_start, time_end=time_end)
    if out_format is not None:
        var_params["accept"] = out_format.value

    var_str = "&".join(map(lambda a: f"{a}={var_params[a]}", var_params))

    if len(var_str) > 0:
        base_url += "?" + var_str

    return base_url