import pytest
import numpy as np
from src.lst_study.NumpyArrays import plot_threhold_and_masked_modis, st_ndvi_plot

def test_plot_threshold_and_masked_modis_shape():
    modis_masked = plot_threhold_and_masked_modis(
        raster_path="src/lst_study/Outputs/Data/modis_image/modis_lst_mean_2025.tif",
        aoi_shp="src/lst_study/Outputs/Data/ams_boundary/amsterdam_boundary.shp",
        threshold=25,
        output_path=None
    )
    assert isinstance(modis_masked, np.ndarray)
    assert np.count_nonzero(~np.isnan(modis_masked)) > 0

def test_st_ndvi_plot_shapes():
    lst, ndvi = st_ndvi_plot(
        lst_path="src/lst_study/Outputs/Data/modis_image/modis_lst_mean_2025.tif",
        sentinel_path="src/lst_study/Outputs/Data/ndvi/sentinel2_mosaic.tif"
    )
    assert isinstance(lst, np.ndarray)
    assert isinstance(ndvi, np.ndarray)
    assert lst.shape == ndvi.shape
    assert np.nanmin(ndvi) >= -1.0
    assert np.nanmax(ndvi) <= 1.0
