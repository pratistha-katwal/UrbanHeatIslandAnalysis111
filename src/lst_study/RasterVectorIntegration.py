

import geopandas as gpd
import rasterio
import rasterio.mask
from rasterio.features import geometry_mask
from rasterstats import zonal_stats
import numpy as np
import matplotlib.pyplot as plt

#Pipeline

class RasterVectorIntegration:
    def __init__(self, raster_path, ams_vector_path, lu_vector_path):
        self.raster_path = raster_path
        self.vector_path = ams_vector_path
        self.lu_vector_path = lu_vector_path
        self.landuse = None
        self.amsboundary = None
        self.nodata = None
        self.lst_array = None
        self.lst_transform = None
        self.dominant_classes = None
        self.hottest_classes = None

    def load_data(self):
        self.amsboundary = gpd.read_file(self.vector_path)
        self.landuse = gpd.read_file(self.lu_vector_path)
        print("Vector data loaded.")

    def read_and_clip_raster(self):
        with rasterio.open(self.raster_path) as src:
            self.amsboundary = self.amsboundary.to_crs(src.crs)
            self.landuse = self.landuse.to_crs(src.crs)
            self.nodata = src.nodata

            lst_clipped, self.lst_transform = rasterio.mask.mask(
                src, self.amsboundary.geometry, crop=True
            )
            self.lst_array = lst_clipped[0]
            self.lst_array = np.ma.masked_equal(self.lst_array, self.nodata)

        print("Raster data read and clipped.")

    def zonal_statistics(self):
        stats = zonal_stats(
            self.landuse,
            self.lst_array,
            affine=self.lst_transform,
            nodata=self.nodata,
            stats=['mean', 'min', 'max']
        )

        self.landuse['mean_lst'] = [s['mean'] for s in stats]
        self.landuse['min_lst'] = [s['min'] for s in stats]
        self.landuse['max_lst'] = [s['max'] for s in stats]
        print("Zonal statistics computed.")

    def select_top_classes(self, top_n=10):
        self.landuse['area_m2'] = self.landuse.geometry.area

        self.dominant_classes = (
            self.landuse.groupby("landuse")
            .agg(total_area_m2=("area_m2","sum"),
                 avg_LST_mean=("mean_lst","mean"))
            .sort_values("total_area_m2", ascending=False)
            .head(top_n)
            .reset_index()
        )

        self.hottest_classes = (
            self.landuse.groupby("landuse")
            .agg(total_area_m2=("area_m2","sum"),
                 avg_LST_mean=("mean_lst","mean"))
            .sort_values("avg_LST_mean", ascending=False)
            .head(top_n)
            .reset_index()
        )

        top_types = list(set(self.dominant_classes["landuse"].tolist() + 
                             self.hottest_classes["landuse"].tolist()))
        self.landuse['Classes_of_interest'] = self.landuse['landuse'].apply(
            lambda x: x if x in top_types else 'Other'
        )
        print("Top classes selected and categorized.")

    def plot_result(self,output_path):
        fig, ax = plt.subplots(2,2,figsize=(16,12))

        # Land-use map
        self.landuse.plot(column="Classes_of_interest", cmap="tab20",
                          legend=True, ax=ax[0,0], edgecolor="black", linewidth=0.2)
        self.amsboundary.boundary.plot(ax=ax[0,0], color="black", linewidth=1)
        ax[0,0].set_title("Land-Use Map of Amsterdam")
        ax[0,0].axis("off")

        # Mean LST map
        self.landuse.plot(column="mean_lst", cmap="YlGnBu",
                          legend=True, ax=ax[0,1], edgecolor="black", linewidth=0.2,
                          missing_kwds={"color":"lightgrey","label":"No Data"})
        self.amsboundary.boundary.plot(ax=ax[0,1], color="black", linewidth=1)
        ax[0,1].set_title("Mean LST per Land-Use Polygon on Year 2025")
        ax[0,1].axis("off")

        # Bar chart: dominant
        ax[1,0].bar(self.dominant_classes["landuse"], self.dominant_classes["avg_LST_mean"], color="skyblue")
        ax[1,0].set_ylabel("Mean LST (°C)")
        ax[1,0].set_title("Top 10 Dominant Land Uses (by Area)")
        ax[1,0].tick_params(axis="x", rotation=45)

        # Bar chart: hottest
        ax[1,1].bar(self.hottest_classes["landuse"], self.hottest_classes["avg_LST_mean"], color="salmon")
        ax[1,1].set_ylabel("Mean LST (°C)")
        ax[1,1].set_title("Top 10 Hottest Land Uses (by Mean LST)")
        ax[1,1].tick_params(axis="x", rotation=45)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()


