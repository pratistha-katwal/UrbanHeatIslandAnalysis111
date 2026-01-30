

import glob
import xarray as xr
import rasterio
import geopandas as gpd
from rasterstats import zonal_stats
import pandas as pd
import rioxarray
import matplotlib.pyplot as plt
import os

# ------------------------------
# Load single raster as Xarray
# ------------------------------
ds = rioxarray.open_rasterio("Outputs/Data/modis_image/modis_lst_mean_2020.tif")
print(ds)

# ------------------------------
# Load multi-year rasters as Xarray cube
# ------------------------------
files = sorted(glob.glob("Outputs/Data/modis_image/modis_lst_mean_*.tif"))
ds_time = xr.concat([rioxarray.open_rasterio(f) for f in files], dim="time")
ds_time["time"] = [f.split("_")[-1].split(".")[0] for f in files]
print(ds_time)

# ------------------------------
# Band-wise statistics
# ------------------------------
band_mean = ds.mean(dim=["x", "y"])
print("Band-wise mean values:")
print(band_mean)

# ------------------------------
# Spatio-temporal slicing
# ------------------------------
spatial_slice = ds_time.sel(y=slice(52.6, 52.4), x=slice(4.8, 5.0))
print("Spatial slice:")
print(spatial_slice)

temporal_slice = ds_time.sel(time="2020")
print("Temporal slice:")
print(temporal_slice)

spatio_temporal_slice = ds_time.sel(time="2020", y=slice(52.6, 52.4), x=slice(4.8, 5.0))
print("Spatio-temporal slice:")
print(spatio_temporal_slice)

# ------------------------------
# Vector AOI
# ------------------------------
gdf = gpd.read_file("Outputs/Data/ams_boundary/amsterdam_boundary.shp")
gdf = gdf.to_crs("EPSG:4326")  
# ------------------------------
# Zonal statistics per polygon
# ------------------------------
results = []
for f in files:
    with rasterio.open(f) as src:
        arr = src.read(1)
        nodata= src.nodata
        transform = src.transform
        zs = zonal_stats(gdf, arr, affine=transform, stats=["mean","max", "min"],nodata=nodata )
        zs[0]["time"] = f.split("_")[-1].split(".")[0]
        results.append(zs[0])

df = pd.DataFrame(results)
print(df)
