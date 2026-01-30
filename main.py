import os
import glob
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterstats import zonal_stats
import pandas as pd
import geemap
import ee
import xarray as xr, rioxarray
from src.lst_study.data_collection import VectorDataCollection ,RasterDataCollection
from src.lst_study.RasterandVectorDC import datacube_lst_timeseries
from src.lst_study.NumpyArrays import plot_threhold_and_masked_modis
from src.lst_study.NumpyArrays import st_ndvi_plot




# Authenticate & initialize Earth Engine
ee.Authenticate()
ee.Initialize(project='pratistha111') 


# # ------------------------------
# # Define all output folders
# # ------------------------------
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

# ------------------------------
# Export Sentinel-2 NDVI
# ------------------------------
ndvi_path = raster_data.export_ndvi()
print(f"Sentinel-2 NDVI saved at: {ndvi_path}")


# -------------------
# Landuse and LST Analysis
# # ------------------
from src.lst_study.RasterVectorIntegration import RasterVectorIntegration
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
# Time series with Data cube
# # ------------------

datacube_lst_timeseries("src/lst_study/Outputs/Data/modis_image", "Outputs/Maps/TimeSeriesPlot_from_datacube.png")

# -------------------
# Thresholding and Clipping to Ams
# ------------------

masked_array = plot_threhold_and_masked_modis(
    threshold=25,
    output_path="Outputs/Maps/MODIS_masked_2025.png"
)

# -------------------
# LST AND NDVI
# ------------------
lst, ndvi = st_ndvi_plot()
