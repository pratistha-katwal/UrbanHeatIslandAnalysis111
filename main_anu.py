import numpy as np
import rasterio

from src.lst_study.Tensors import run_tensor_benchmark


def main():
    # --------------------------------------------------
    # Path to existing MODIS LST file (2025)
    # --------------------------------------------------
    lst_tif = r"C:\Users\anupr\Downloads\Outputs\Outputs\Data\modis_image\modis_lst_mean_2025.tif"

    # --------------------------------------------------
    # Read raster into NumPy array
    # --------------------------------------------------
    with rasterio.open(lst_tif) as src:
        lst_array = src.read(1).astype(np.float32)
        nodata = src.nodata

    if nodata is not None:
        lst_array[lst_array == nodata] = np.nan

    print("LST array loaded with shape:", lst_array.shape)

    # --------------------------------------------------
    # PART A: Tensor benchmark (Gaussian blur)
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


if __name__ == "__main__":
    main()
