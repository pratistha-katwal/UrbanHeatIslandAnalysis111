import os
import geopandas as gpd
import matplotlib.pyplot as plt


def main():
    lu_path = "src/lst_study/Outputs/Data/land_use_polygon/amsterdam_landuse.shp"
    gdf = gpd.read_file(lu_path)

    # Keep only rows that have a landuse value
    gdf = gdf[~gdf["landuse"].isna()].copy()

    # IMPORTANT: area must be in meters, not degrees -> reproject to EPSG:28992 (Netherlands RD New)
    gdf = gdf.to_crs(epsg=28992)

    # Area in square meters and hectares
    gdf["area_m2"] = gdf.geometry.area
    gdf["area_ha"] = gdf["area_m2"] / 10000.0

    # Total area per landuse class
    area_by_class = (
        gdf.groupby("landuse")["area_ha"]
        .sum()
        .sort_values(ascending=False)
    )

    print("\nTop 10 landuse classes by area (hectares):")
    print(area_by_class.head(10))
        # ------------------------------
    # Plot Top 10 landuse classes
    # ------------------------------
    top10 = area_by_class.head(10)

    os.makedirs("Outputs/Maps", exist_ok=True)

    plt.figure(figsize=(10, 5))
    top10.sort_values().plot(kind="barh")  # horizontal bars, easier to read
    plt.xlabel("Area (hectares)")
    plt.ylabel("Landuse class")
    plt.title("Top 10 Landuse Classes by Area in Amsterdam")
    plt.tight_layout()

    out_path = "Outputs/Maps/Top10_Landuse_Area.png"
    plt.savefig(out_path, dpi=300)
    plt.show()

    print("\nSaved plot to:", out_path)


    print("\nNumber of unique landuse classes:", area_by_class.shape[0])


if __name__ == "__main__":
    main()
