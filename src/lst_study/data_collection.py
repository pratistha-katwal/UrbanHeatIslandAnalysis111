# ------------------------------
# Imports
# ------------------------------
import ee
import geemap
import requests
import osmnx as ox
import geopandas as gpd
import os
import xarray as xr
import numpy as np
import rasterio

# ------------------------------
# Create required folders
# ------------------------------
# os.makedirs("Outputs/Data/modis_image", exist_ok=True)
# os.makedirs("Outputs/Data/sentinel_image", exist_ok=True)
# os.makedirs("Outputs/Data/ams_boundary", exist_ok=True)
# os.makedirs("Outputs/Data/land_use_polygon", exist_ok=True)

# ------------------------------
# Vector Data Class
# ------------------------------
class VectorDataCollection:
    def __init__(self):
        self.url = "https://service.pdok.nl/kadaster/bestuurlijkegebieden/wfs/v1_0"
        self.params = {
            "service": "WFS",
            "request": "GetFeature",
            "version": "2.0.0",
            "typeNames": "bg:Gemeentegebied",
            "outputFormat": "application/json",
        }
        self.gemeente_gdf = None
        self.ams_boundary = None

    def fetch_gemeente(self):
        response = requests.get(self.url, params=self.params)
        data = response.json()
        self.gemeente_gdf = gpd.GeoDataFrame.from_features(
            data["features"], crs="EPSG:28992"
        ).to_crs(epsg=4326)
        return self.gemeente_gdf

    def filter_amsterdam(self):
        if self.gemeente_gdf is None:
            raise RuntimeError("Run fetch_gemeente() first")
        ams = self.gemeente_gdf[self.gemeente_gdf["naam"] == "Amsterdam"]
        self.ams_boundary = ams.dissolve()
        return self.ams_boundary

    def land_use(self):
        tags = {"landuse": True}
        landuse = ox.features_from_place(
            "Amsterdam, Netherlands", tags=tags
        )
        landuse = landuse[landuse.geometry.type.isin(["Polygon", "MultiPolygon"])]
        landuse = landuse.to_crs(epsg=4326)
        return landuse

# ------------------------------
# Raster Data Class
# ------------------------------
class RasterDataCollection:
    def __init__(self, AOI_ee, start_year=2020, end_year=2024):
        self.AOI_ee = AOI_ee
        self.start_year = start_year
        self.end_year = end_year
        self.annual_means = {}  # ee.Image per year
        self.arrays = {}        # NumPy arrays per year

        # AOI attributes for Sentinel / NDVI
        self.AOI = AOI_ee
        self.start_date = f"{self.start_year}-06-01"
        self.end_date = f"{self.end_year}-08-31"
        self.max_cloud = 20
        
        

        # Export MODIS LST per year
        for year in range(self.start_year, self.end_year + 1):
            start_date = f"{year}-06-01"
            end_date = f"{year}-08-31"

            # MODIS LST collection
            summer_collection = (
                ee.ImageCollection("MODIS/061/MOD11A2")
                .filterBounds(self.AOI_ee)
                .filterDate(start_date, end_date)
                .select("LST_Day_1km")
            )
            annual_mean = summer_collection.mean().multiply(0.02).subtract(273.15)
            self.annual_means[year] = annual_mean

            # Export to GeoTIFF
            out_path = os.path.join("src/lst_study/Outputs/Data/modis_image", f"modis_lst_mean_{year}.tif")
            geemap.ee_export_image(
                annual_mean,
                filename=out_path,
                scale=1000,
                region=self.AOI_ee.geometry(),
            )

            # Read back as NumPy array
            with rasterio.open(out_path) as src:
                self.arrays[year] = src.read(1)


    # ------------------------------
    # Sentinel-2 NDVI
    # ------------------------------
    def get_sentinel2_mosaic(self):
        self.ndvi_out_dir="src/lst_study/Outputs/Data/ndvi"
        collection = (
            ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
            .filterBounds(self.AOI)
            .filterDate(f"{self.end_year}-06-01", f"{self.end_year}-08-31")
            .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", self.max_cloud))
            .select(["B4", "B8"])
        )
        mosaic = collection.mosaic()
        return mosaic

    def export_ndvi(self, filename="sentinel2_mosaic.tif", scale=10):
        mosaic = self.get_sentinel2_mosaic()
        out_path = os.path.join(self.ndvi_out_dir, filename)
        geemap.ee_export_image(
            mosaic,
            filename=out_path,
            scale=scale,
            region=self.AOI.geometry(),
            file_per_band=False
        )
        return out_path

# # ------------------------------
# # USAGE EXAMPLE
# # ------------------------------

# # Authenticate & initialize Earth Engine
# ee.Authenticate()
# ee.Initialize(project='pratistha111')

# # ------------------------------
# # Vector AOI
# # ------------------------------
# vector_data = VectorDataCollection()
# vector_data.fetch_gemeente()
# AOI_gdf = vector_data.filter_amsterdam()
# AOI_gdf.to_file("Outputs/Data/ams_boundary/amsterdam_boundary.shp")

# land_use_gdf = vector_data.land_use()
# land_use_gdf.to_file("Outputs/Data/land_use_polygon/amsterdam_landuse.shp")

# # Convert GeoDataFrame to ee.FeatureCollection
# AOI_ee = geemap.geopandas_to_ee(AOI_gdf)

# # ------------------------------
# # Raster Collection
# # ------------------------------
# raster_data = RasterDataCollection(AOI_ee, start_year=2020, end_year=2025)

# # Access annual NumPy arrays
# arr_2020 = raster_data.arrays[2020]


# # ------------------------------
# # Export Sentinel-2 NDVI
# # ------------------------------
# ndvi_path = raster_data.export_ndvi()
# print(f"Sentinel-2 NDVI saved at: {ndvi_path}")
