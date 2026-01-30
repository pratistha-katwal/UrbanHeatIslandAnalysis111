
import rasterio
import numpy as np
import geopandas as gpd
from rasterio.features import geometry_mask
import matplotlib.pyplot as plt
import os


def plot_threhold_and_masked_modis(
    raster_path="src/lst_study/Outputs/Data/modis_image/modis_lst_mean_2025.tif", 
    aoi_shp="src/lst_study/Outputs/Data/ams_boundary/amsterdam_boundary.shp",
    threshold=25, 
    output_path="Outputs/Maps/Threshold.png", 
    cmap="hot"
):

    # -------------------------
    # Load raster
    # -------------------------
    with rasterio.open(raster_path) as src:
        modis_data = src.read(1).astype(float)  # ensure float for NaN
        transform = src.transform
        crs=src.crs
        height, width = src.height, src.width

    # -------------------------
    # Mask by threshold and nodata
    # -------------------------
    modis_masked = np.where(modis_data > threshold, np.nan, modis_data)
    modis_masked = np.where(modis_masked == 0, np.nan, modis_masked)

    # -------------------------
    # Load AOI polygon
    # -------------------------
    mask_gdf = gpd.read_file(aoi_shp)
    mask_gdf = mask_gdf.to_crs(crs)

    # -------------------------
    # Create AOI mask
    # -------------------------
    mask = geometry_mask(
        [geom for geom in mask_gdf.geometry],
        transform=transform,
        invert=True,
        out_shape=(height, width)
    )

    # Apply AOI mask
    modis_masked_aoi = np.where(mask, modis_masked, np.nan)
    print("MODIS masked shape:", modis_masked_aoi.shape)

    # -------------------------
    # Plot raster + AOI shape
    # -------------------------

    fig, ax = plt.subplots(figsize=(8,6))
    xmin, ymin = transform * (0, height)
    xmax, ymax = transform * (width, 0)
    extent = [xmin, xmax, ymin, ymax]
    # Plot raster
    raster_img = ax.imshow(modis_masked_aoi, cmap=cmap, extent=extent, origin="upper")
    # Plot AOI polygon on top
    mask_gdf.boundary.plot(ax=ax, edgecolor="blue", linewidth=1.0)

    # Add colorbar
    cbar = plt.colorbar(raster_img, ax=ax, fraction=0.036, pad=0.04)
    cbar.set_label("LST (°C)")

    ax.set_title(f"MODIS LST (masked > {threshold}°C and clipped to AOI in Year 2025)")
    ax.axis("off")

    # Save if requested
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')

    plt.show()

    return modis_masked_aoi



import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import matplotlib.pyplot as plt

def st_ndvi_plot(lst_path="src/lst_study/Outputs/Data/modis_image/modis_lst_mean_2025.tif",
                 sentinel_path="src/lst_study/Outputs/Data/ndvi/sentinel2_mosaic.tif"):

    # --- Load MODIS ---
    with rasterio.open(lst_path) as src_modis:
        lst = src_modis.read(1).astype(float)
        lst[lst == 0] = np.nan
        modis_meta = src_modis.meta.copy()

    # --- Load Sentinel bands ---
    with rasterio.open(sentinel_path) as src_sen:
        RED = src_sen.read(1).astype(float)
        NIR = src_sen.read(2).astype(float)
        RED[RED == 0] = np.nan
        NIR[NIR == 0] = np.nan
        sen_meta = src_sen.meta.copy()

    # --- Resample Sentinel2 to MODIS resolution ---
    shape = lst.shape  
    RED_resampled = np.empty(shape, dtype=float)
    NIR_resampled = np.empty(shape, dtype=float)

    reproject(
        source=RED,
        destination=RED_resampled,
        src_transform=src_sen.transform,
        src_crs=src_sen.crs,
        dst_transform=modis_meta['transform'],
        dst_crs=modis_meta['crs'],
        resampling=Resampling.bilinear
    )

    reproject(
        source=NIR,
        destination=NIR_resampled,
        src_transform=src_sen.transform,
        src_crs=src_sen.crs,
        dst_transform=modis_meta['transform'],
        dst_crs=modis_meta['crs'],
        resampling=Resampling.bilinear
    )

    # --- Calculate NDVI ---
    ndvi = (NIR_resampled - RED_resampled) / (NIR_resampled + RED_resampled + 1e-10)

    # --- Flatten and remove NaNs ---
    valid = ~np.isnan(lst) & ~np.isnan(ndvi)
    lst_flat = lst[valid]
    ndvi_flat = ndvi[valid]

    # --- Correlation ---
    corr = np.corrcoef(lst_flat, ndvi_flat)[0,1]
    print(f"LST-NDVI correlation: {corr:.3f}")

    # --- Scatter plot ---
    plt.figure(figsize=(6,5))
    plt.scatter(ndvi_flat, lst_flat, s=1, alpha=0.3, c=lst_flat, cmap="hot")
    plt.xlabel("NDVI")
    plt.ylabel("LST (°C)")
    plt.title(f"LST vs NDVI (r={corr:.3f}) for Year 2025")
    plt.colorbar(label="LST (°C)")
    plt.savefig("Outputs/Maps/LSTandNDVI.png", dpi=300, bbox_inches='tight')
    plt.show()

    return lst, ndvi


# Exploring different cappabilities of NumpyArrays

if __name__ == "__main__":
    # Load MODIS raster
    with rasterio.open("Outputs/Data/modis_image/modis_lst_mean_2025.tif") as src_modis:
        modis_data = src_modis.read(1).astype(float)  
        modis_transform = src_modis.transform
        modis_shape = (src_modis.height, src_modis.width)

    # Load Sentinel bands (
    with rasterio.open("Outputs/Data/sentinel_image/sentinel2_mosaic.tif") as src_sen:
        NIR = src_sen.read(2).astype(float)  # band 2
        RED = src_sen.read(1).astype(float)  # band 1

    # Handle nodata values (replace 0 with NaN)
    NIR[NIR == 0] = float('nan')
    RED[RED == 0] = float('nan')

    # NDVI calculation
    ndvi = (NIR - RED) / (NIR + RED + 1e-10)  

    print("NDVI calculated. Shape:", ndvi.shape)


