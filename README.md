# BARRA2 downloader
By B.Duncan (2026)  
Inspired by the work of Richard Gledhill (https://github.com/richard-gledhill/barra2-dl), just decided wanted to make it more abstracted and load to RAM. 

*NOTE:* This library is still under development and will likely have some bugs in it. Please let me know of any issues.

## Dependencies
- numpy >= 2.0.0 (no reason for this version other than it's a major version, should break if go a few versions earlier)
- pandas >= 2.2.0 (same)
- requests >= 2.30.0 (same)

## Build
Clone the repo, and then run build_and_install.bat, or the equivalent commands below. I would suggest doing this in a virtual environment as to not muddle up your global space.

```
python -m build
pip install dist/barra2_downloader-<VERSION>-py3-none-any.whl
```

A precompiled whl is available under the Releases tab, which should work for py3.

## Example
Please see the examples folder for two examples, one for downloading a single variable, and one for downloading multiple variables (with time joining).

## Features
Current features are:
- Downloading of data from BARRA2 model/domain/frequency runs
- Listing variable available in each of the models available
- Multiple variable download into a single pandas df, with time-synced rows
- Threaded download, with an adjustable number of workers
- Serial download, with sleep for rate limiter avoidance

Planned features are:
- Downloading of a netCDF file from server which has been constrained to a bounding box
  - Possibly loading into a geopandas df or other raster format for RAM processing
- Offline caching abilities (i.e. set a cache directory and if anything is requested if gets saved there -> reduces need to download)
- Still thinking of more things to do slowly