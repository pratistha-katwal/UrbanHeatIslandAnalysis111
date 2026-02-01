# **Urban Heat Island Analysis in Amsterdam**

## 📋 Project Overview

This project analyzes **Urban Heat Islands (UHI)** in Amsterdam by integrating **satellite raster data** and **vector land use information**. It quantifies how different land uses affect surface temperatures and tracks changes over a **5-year period (2020–2025)**.

**Key Objectives:**

* Calculate average surface temperatures per land use type
* Identify temperature hotspots and cooler zones
* Analyze temporal trends to detect high-temperature years
* Demonstrate raster–vector integration, NumPy/Tensor operations, and data cube analysis

---

## 🎯 Features & Workflow

1. **Download Data:**

   * MODIS Land Surface Temperature (LST) 2020–2025
   * Amsterdam boundaries & land use polygons from OpenStreetMap & PDOK
2. **Process Data:**

   * Apply masks to raster data using vector geometries
   * Compute zonal statistics per land use
   * Convert rasters to **NumPy arrays** and **TensorFlow/PyTorch tensors** for analysis
   * Handle multi-year data in **Xarray data cubes**
3. **Visualize Results:**

   * Maps showing land use vs temperature
   * Time series charts tracking UHI trends
   * Top 10 hottest/coolest land uses

---

## 🏗️ Project Structure

```
LST_study/
├── main.py                        # Main pipeline execution
├── src/lst_study/
│   ├── data_collection.py         # Earth Engine downloads
│   ├── NumpyArrays.py             # NumPy array operations
│   ├── Tensors.py                 # TensorFlow/PyTorch operations
│   ├── VectorProcessing.py        # GeoPandas/Shapely vector operations
│   ├── RasterandVectorDC.py       # Xarray raster/vector data cubes
│   ├── RasterVectorIntegration.py # Zonal statistics & raster–vector interaction
│   └── __init__.py
├── Outputs/
│   ├── Maps/
│   │   ├── LSTandLandUse.png
│   │   ├── LSTandNDVI.png
│   │   ├── MODIS_masked_2025.png
│   │   ├── Tensor_Gaussian_Blur.png
│   │   ├── TimeSeriesPlot_from_datacube.png
│   │   ├── Top10_Hottest_Landuse_MeanLST_2025.png
│   │   └── Top10_Landuse_Area.png
│   └── Tables/
│       └── mean_lst_by_landuse_2025.csv
├── tests/test.py                  # Unit testing
├── main_anu.py
├── main_raster_vector.py
├── main_vector.py  
└── pyproject.toml                 # Poetry environment config
```

---

## 🚀 Quick Start

### 1️⃣ Clone Repository

```bash
git clone https://github.com/pratistha-katwal/UrbanHeatIslandAnalysis111
cd UrbanHeatIslandAnalysis111
poetry install
```

### 2️⃣ Set Up Google Earth Engine

1. Sign up at [Earth Engine](https://earthengine.google.com/)
2. Create a project (any name works)
3. Authenticate:

```python
import ee
ee.Authenticate()
ee.Initialize(project='pratistha111')  # replace with your project name in 'main.py'
```

### 3️⃣ Run the Analysis

```bash
python main.py
```

**Outputs Generated:**

* Zonal temperature maps by land use
* Time series plots (2020–2025)
* Top 10 hottest and coolest land use categories
* Masked MODIS raster images and tensor-processed visualizations

---

## 📊 Key Findings

* **Hottest zones:** Dense urban cores, industrial corridors, major transportation networks
* **Coolest zones:** Forests, meadows, grasslands, allotment gardens
* **Top Land Use by Temperature:** Highways > Commercial/retail > Residential
* **Lowest Temperature Land Use:** Vegetated areas consistently cooler
* **Temporal Insight:** 2022 recorded the highest mean, max, and min temperatures

---

## 🛠️ Technical Components

| Component                 | Tools / Methods                                                                      |
| ------------------------- | ------------------------------------------------------------------------------------ |
| Raster Data Handling      | `rasterio`, `NumPy`, masking & thresholding                                          |
| Vector Processing         | `GeoPandas`, `Fiona`, `Shapely`, geometry & attribute operations                     |
| Tensor Operations         | `TensorFlow` / `PyTorch` for convolution, aggregation, regression; GPU/CPU awareness |
| Data Cube Analysis        | `Xarray` for multi-year raster time series; temporal aggregation per polygon         |
| Raster–Vector Integration | Zonal statistics, raster sampling, bidirectional raster ↔ vector operations          |
| Visualization             | `Matplotlib` for maps, charts, and temporal plots                                    |

---

## 🔧 Customization Options

* **Study Area:** Change `"Amsterdam, Netherlands"` in `data_collection.py`
* **Years:** Modify `start_year` and `end_year` in `data_collection.py`
* **Raster Source:** Replace MODIS with ECOSTRESS or Sentinel LST products if desired

---

## ❓ Common Issues

* **Authentication Error:** Ensure Earth Engine account is active and run `earthengine authenticate`
* **Slow Downloads:** Check network and server limits on MODIS data

---

## 📚 References & Resources

* [Google Earth Engine Documentation](https://developers.google.com/earth-engine)
* [MODIS Satellite Data](https://modis.gsfc.nasa.gov/)
* [Urban Heat Island Basics](https://www.epa.gov/heatislands)
* [OpenStreetMap Data](https://www.openstreetmap.org)
* [PDOK Dutch Mapping Services](https://www.pdok.nl/)


