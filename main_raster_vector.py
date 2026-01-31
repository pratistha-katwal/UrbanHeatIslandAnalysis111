import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
import pandas as pd
import matplotlib.pyplot as plt


def main():
    # ------------------------------
    # Input paths
    # ------------------------------
    lu_path = "src/lst_study/Outputs/Data/land_use_polygon/amsterdam_landuse.shp"
    lst_tif = r"C:\Users\anupr\Downloads\Outputs\Outputs\Data\modis_image\modis_lst_mean_2025.tif"

    if not os.path.exists(lu_path):
        raise FileNotFoundError(f"Missing landuse shapefile: {lu_path}")
    if not os.path.exists(lst_tif):
        raise FileNotFoundError(f"Missing LST raster: {lst_tif}")

    os.makedirs("Outputs/Maps", exist_ok=True)
    os.makedirs("Outputs/Tables", exist_ok=True)

    # ------------------------------
    # Load vector
    # ------------------------------
    gdf = gpd.read_file(lu_path)
    gdf = gdf[~gdf["landuse"].isna()].copy()  # keep only polygons with landuse class
    print("Landuse polygons loaded:", gdf.shape)
    print("Vector CRS:", gdf.crs)

    # ------------------------------
    # Load raster
    # ------------------------------
    with rasterio.open(lst_tif) as src:
        raster_crs = src.crs
        transform = src.transform
        nodata = src.nodata
        lst_arr = src.read(1).astype(np.float32)

    print("Raster CRS:", raster_crs)
    print("Raster shape:", lst_arr.shape, "nodata:", nodata)

    # Replace nodata with NaN (helps stats)
    if nodata is not None:
        lst_arr[lst_arr == nodata] = np.nan

    # ------------------------------
    # CRS alignment (vector -> raster CRS)
    # ------------------------------
    if gdf.crs != raster_crs:
        gdf = gdf.to_crs(raster_crs)
        print("Reprojected vector to raster CRS:", gdf.crs)
    else:
        print("Vector CRS already matches raster CRS")

    # ------------------------------
    # Zonal statistics (Raster–Vector integration)
    # mean LST for each polygon
    # ------------------------------
    stats = zonal_stats(
        gdf,
        lst_arr,
        affine=transform,
        stats=["mean"],
        nodata=np.nan,
        all_touched=True  # counts edge pixels too (better for coarse rasters)
    )

    # Add mean LST to gdf
    gdf["mean_lst"] = [s["mean"] for s in stats]

    # Drop polygons with no raster pixels intersecting
    gdf = gdf[~gdf["mean_lst"].isna()].copy()

    print("Polygons with valid mean LST:", gdf.shape[0])

    # ------------------------------
    # Aggregate by landuse class
    # ------------------------------
    by_class = (
        gdf.groupby("landuse")["mean_lst"]
        .mean()
        .sort_values(ascending=False)
    )

    print("\nTop 10 hottest landuse classes (mean LST):")
    print(by_class.head(10))

    # Save table
    out_csv = "Outputs/Tables/mean_lst_by_landuse_2025.csv"
    by_class.reset_index().to_csv(out_csv, index=False)
    print("\nSaved table:", out_csv)

    # ------------------------------
    # Plot Top 10 hottest classes
    # ------------------------------
    top10 = by_class.head(10).sort_values()

    plt.figure(figsize=(10, 6))
    ax = top10.plot(kind="barh")
    ax.set_xlabel("Mean LST (°C)")
    ax.set_ylabel("Landuse class")
    ax.set_title("Amsterdam: Top 10 Hottest Landuse Classes (Mean LST, 2025)")
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    # add labels
    for i, v in enumerate(top10.values):
        ax.text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=9)

    plt.tight_layout()

    out_png = "Outputs/Maps/Top10_Hottest_Landuse_MeanLST_2025.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.show()

    print("Saved plot:", out_png)


if __name__ == "__main__":
    main()
