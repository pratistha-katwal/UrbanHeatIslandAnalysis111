
import rasterio
import numpy as np
import geopandas as gpd
from rasterio.features import geometry_mask

# Load MODIS raster
with rasterio.open("Outputs/Data/modis_image/modis_lst_mean_2025.tif") as src_modis:
    modis_data = src_modis.read(1)  # single band
    modis_transform = src_modis.transform
    modis_shape = (src_modis.height, src_modis.width)

# Load Sentinel bands (use integer band indices!)
with rasterio.open("Outputs/Data/sentinel_image/sentinel2_mosaic.tif") as src_sen:
    NIR = src_sen.read(2).astype(float)
    RED = src_sen.read(1).astype(float)

# Threshold example
modis_masked = np.where(modis_data > 25, np.nan, modis_data)

# NDVI calculation
ndvi = (NIR - RED) / (NIR + RED + 1e-10)

# Apply vector mask
mask_gdf = gpd.read_file("Outputs/Data/ams_boundary/amsterdam_boundary.shp")
mask = geometry_mask([geom for geom in mask_gdf.geometry],
                     transform=src_modis.transform,  # align with MODIS raster
                     invert=True,
                     out_shape=modis_shape)

modis_masked_aoi = np.where(mask, modis_masked, np.nan)


print("MODIS masked shape:", modis_masked_aoi.shape)

