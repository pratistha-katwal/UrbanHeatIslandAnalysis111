

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
# Load multi-year rasters as Xarray cube
# ------------------------------

def datacube_lst_timeseries(raster_folder, output_path="Outputs/Maps/TimeSeriesPlot.png"):
    # Get all raster files
    files = sorted(glob.glob(os.path.join(raster_folder, "modis_lst_mean_*.tif")))
    if not files:
        print("No raster files found in the folder.")
        return

    # Load rasters as Xarray cube
    ds_time = xr.concat([rioxarray.open_rasterio(f) for f in files], dim="time")
    # Assign time from filename
    ds_time["time"] = [f.split("_")[-1].split(".")[0] for f in files]
    ds_time = ds_time.where(ds_time != 0)

    # Compute statistics over spatial dimensions
    mean_lst = ds_time.mean(dim=("x", "y"), skipna=True)
    max_lst = ds_time.max(dim=("x", "y"), skipna=True)
    min_lst = ds_time.min(dim=("x", "y"), skipna=True)

    # Compute y-axis limits with padding
    ymin = float(min_lst.min()) - 2
    ymax = float(max_lst.max()) + 2

    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(ds_time["time"], mean_lst, marker="o", label="Mean LST")
    plt.plot(ds_time["time"], max_lst, alpha=0.5, linestyle="--", label="Max LST")
    plt.plot(ds_time["time"], min_lst, alpha=0.5, linestyle="--", label="Min LST")
    plt.xlabel("Year")
    plt.ylabel("LST (°C)")
    plt.title("Land Surface Temperature Time Series")
    plt.grid(True)
    plt.legend()
    plt.ylim(ymin, ymax)

    # Save plot
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"Time series plot saved to: {output_path}")



# Exploring different cappabilities of Raster and Vector togeter like band-wise statistics, slicing
if __name__ == "__main__":
    # Load single raster
    ds = rioxarray.open_rasterio("Outputs/Data/modis_image/modis_lst_mean_2020.tif")
    print(ds)

    # Band-wise statistics
    band_mean = ds.mean(dim=["x", "y"])
    print("Band-wise mean values:")
    print(band_mean)

    # Load multi-year rasters
    files = sorted(glob.glob("Outputs/Data/modis_image/modis_lst_mean_*.tif")) 
    ds_time = xr.concat([rioxarray.open_rasterio(f) for f in files], dim="time") 
    ds_time["time"] = [f.split("_")[-1].split(".")[0] for f in files]
    print(ds_time)

    # Spatio-temporal slicing
    spatial_slice = ds_time.sel(y=slice(52.6, 52.4), x=slice(4.8, 5.0))
    print("Spatial slice:", spatial_slice)

    temporal_slice = ds_time.sel(time="2020")
    print("Temporal slice:", temporal_slice)

    spatio_temporal_slice = ds_time.sel(time="2020", y=slice(52.6, 52.4), x=slice(4.8, 5.0))
    print("Spatio-temporal slice:", spatio_temporal_slice)

    # Vector AOI
    gdf = gpd.read_file("Outputs/Data/ams_boundary/amsterdam_boundary.shp")
    gdf = gdf.to_crs("EPSG:4326")  

    # Zonal statistics
    results = []
    for f in files:
        with rasterio.open(f) as src:
            arr = src.read(1)
            nodata= src.nodata
            transform = src.transform
            zs = zonal_stats(gdf, arr, affine=transform, stats=["mean","max", "min"], nodata=nodata )
            zs[0]["time"] = f.split("_")[-1].split(".")[0]
            results.append(zs[0])

    df = pd.DataFrame(results)
    print(df)
