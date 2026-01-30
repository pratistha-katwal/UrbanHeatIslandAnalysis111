import os
import glob
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterstats import zonal_stats
import pandas as pd
from src.lst_study.RasterVectorIntegration import RasterVectorIntegration
import geemap
import ee
from src.lst_study.data_collection import VectorDataCollection ,RasterDataCollection


# Authenticate & initialize Earth Engine
ee.Authenticate()
ee.Initialize(project='pratistha111') 


# ------------------------------
# Define all output folders
# ------------------------------
output_folders = [
     "Outputs/Maps",
    "src/lst_study/Outputs/Data/ams_boundary",
    "src/lst_study/Outputs/Data/land_use_polygon",
    "src/lst_study/Outputs/Data/modis_image",
    "src/lst_study/Outputs/Data/ndvi"  
]

# Create folders if they don't exist
for folder in output_folders:
    os.makedirs(folder, exist_ok=True)


# ------------------------------
# Vector AOI
# ------------------------------
vector_data = VectorDataCollection()
vector_data.fetch_gemeente()
AOI_gdf = vector_data.filter_amsterdam()
AOI_gdf.to_file("src/lst_study/Outputs/Data/ams_boundary/amsterdam_boundary.shp")

land_use_gdf = vector_data.land_use()
land_use_gdf.to_file("src/lst_study/Outputs/Data/land_use_polygon/amsterdam_landuse.shp")

# Convert GeoDataFrame to ee.FeatureCollection
AOI_ee = geemap.geopandas_to_ee(AOI_gdf)

# ------------------------------
# Raster Collection
# ------------------------------
raster_data = RasterDataCollection(AOI_ee, start_year=2020, end_year=2025)

# Access annual NumPy arrays
arr_2020 = raster_data.arrays[2020]


# ------------------------------
# Export Sentinel-2 NDVI
# ------------------------------
ndvi_path = raster_data.export_ndvi()
print(f"Sentinel-2 NDVI saved at: {ndvi_path}")



# Initialize raster-vector pipeline
pipeline = RasterVectorIntegration(
    ams_vector_path="src/lst_study/Outputs/Data/ams_boundary/amsterdam_boundary.shp",
    lu_vector_path="src/lst_study/Outputs/Data/land_use_polygon/amsterdam_landuse.shp",
    raster_path="src/lst_study/Outputs/Data/modis_image/modis_lst_mean_2025.tif"
)
pipeline.load_data()
pipeline.read_and_clip_raster()
pipeline.zonal_statistics()
pipeline.select_top_classes(top_n=10)
pipeline.plot_result(output_path="Outputs/Maps/LSTandLandUse.png") 

# -------------------
# Time series per polygon
# -------------------


def create_zonal_stats_dataframe(files, vector_gdf, stats=["mean","max","min"], save_path=None):
    results = []
    for f in files:
        if not os.path.exists(f):
            print(f"Warning: {f} does not exist. Skipping.")
            continue
        with rasterio.open(f) as src:
            arr = src.read(1)
            nodata = src.nodata
            transform = src.transform
            zs = zonal_stats(vector_gdf, arr, affine=transform, stats=stats, nodata=nodata)
            zs[0]["time"] = f.split("_")[-1].split(".")[0]
            results.append(zs[0])
    df = pd.DataFrame(results)
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"DataFrame saved to {save_path}")
    return df

gdf = gpd.read_file("src/lst_study/Outputs/Data/ams_boundary/amsterdam_boundary.shp")
gdf = gdf.to_crs("EPSG:4326")

files = sorted(glob.glob("src/lst_study/Outputs/Data/modis_image/modis_lst_mean_*.tif"))
print("Raster files found:", files)

df = create_zonal_stats_dataframe(
    files=files,
    vector_gdf=gdf,
    stats=["mean","max","min"],
    save_path="src/lst_study/Outputs/Data/Dataframe.csv"
)
print(df)

# Plot
ymin = df[["min","max"]].min().min() - 2
ymax = df[["min","max"]].max().max() + 2
plt.figure(figsize=(8,5))
plt.plot(df["time"], df["mean"], marker="o", label="Mean LST")
plt.plot(df["time"], df["max"], alpha=0.5, linestyle="--", label="Max LST")
plt.plot(df["time"], df["min"], alpha=0.5, linestyle="--", label="Min LST")
plt.xlabel("Year")
plt.ylabel("LST (°C)")
plt.title("Land Surface Temperature Time Series")
plt.grid(True)
plt.legend()
plt.ylim(ymin, ymax)
plt.savefig("Outputs/Maps/TimeSeriesPlot.png", dpi=300, bbox_inches='tight')
plt.show()
