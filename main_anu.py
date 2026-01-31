import numpy as np
import rasterio
import matplotlib.pyplot as plt

from src.lst_study.Tensors import run_tensor_benchmark


def main():
    # --------------------------------------------------
    # Path to existing MODIS LST file
    # --------------------------------------------------
    lst_tif = r"C:\Users\anupr\Downloads\Outputs\Outputs\Data\modis_image\modis_lst_mean_2025.tif"

    # --------------------------------------------------
    # Read raster
    # --------------------------------------------------
    with rasterio.open(lst_tif) as src:
        lst_array = src.read(1).astype(np.float32)
        nodata = src.nodata

    if nodata is not None:
        lst_array[lst_array == nodata] = np.nan

    print("LST array loaded with shape:", lst_array.shape)

    # --------------------------------------------------
    # PART A: Tensor benchmark
    # --------------------------------------------------
    results = run_tensor_benchmark(
        lst_array,
        size=11,
        sigma=2.0
    )

    print("\nTensor benchmark (Gaussian blur):")
    print(" NumPy time (s):", results["numpy_time_sec"])
    print(" Torch time (s):", results["torch_time_sec"])
    print(" Torch device:", results["torch_device"])

    # --------------------------------------------------
    # Visualization (INSIDE main)
    # --------------------------------------------------
    lst_blurred = results["torch_blur"]

    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    plt.imshow(lst_array, cmap="hot")
    plt.title("Original LST")
    plt.colorbar(fraction=0.046)

    plt.subplot(1, 2, 2)
    plt.imshow(lst_blurred, cmap="hot")
    plt.title("Gaussian Blurred LST")
    plt.colorbar(fraction=0.046)

    plt.tight_layout()

# Save figure for report
    plt.savefig("Outputs/Maps/Tensor_Gaussian_Blur.png", dpi=300)

    plt.show()



# --------------------------------------------------
# This MUST be last
# --------------------------------------------------
if __name__ == "__main__":
    main()
