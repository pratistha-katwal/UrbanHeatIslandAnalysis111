# **Urban Heat Island Analysis in Amsterdam**

## 📋 **Project Overview**
This project analyzes Urban Heat Islands (UHI) in Amsterdam using satellite data and geospatial analysis. It calculates how different land uses affect surface temperatures and tracks temperature changes over 5 years.

## 🎯 **What This Project Does**
- Downloads MODIS satellite temperature data for Amsterdam (2020-2025)
- Fetches Amsterdam boundaries and land use data
- Calculates average temperatures for different land uses (parks, residential areas, etc.)
- Shows which land use areas are hottest 
- Tracks temperature changes over time (2020-2025)

## 📁 **Project Structure**
```
LST_study/
LST_study/
├── main.py                    
├── src/lst_study/
│   ├── data_collection.py     ← Earth Engine + downloads
│   ├── NumpyArrays.py         ← 3.1 NumPy / array ops
│   ├── Tensors.py             ← 3.2 TensorFlow / PyTorch
│   ├── VectorProcessing.py    ← 3.3 vector ops
│   ├── RasterandVectorDC.py   ← 3.4 xarray / data cube
│   ├── RasterVectorIntegration.py ← 3.5 zonal stats etc.
│   └── __init__.py
├── Outputs/                       
│   └── Maps/                       ←Outputs Map
        └── LSTandLandUse.png
        └── TimeSeriesPlot.png
└── pyproject.toml
```

## 🚀 **Quick Start**

### **Step 1: Install Requirements**
```bash
poetry install
```

### **Step 2: Set Up Google Earth Engine**
1. Go to [earthengine.google.com](https://earthengine.google.com/)
2. Sign up for an account
3. Create a project (any name works)

### **Step 3: Run the Analysis**
```bash
python main.py
```

The script will:
1. Authenticate with Google Earth Engine (opens browser)
2. Download Amsterdam boundaries and land use data
3. Download temperature data from MODIS satellite (2020-2025)
4. Create maps showing hottest areas
5. Generate temperature time series chart

## 📊 **What You'll Get**

### **Output Files:**
1. **`Outputs/Maps/LSTandLandUse.png`** - Map showing temperatures by land use
2. **`Outputs/Maps/TimeSeriesPlot.png`** - Chart of temperature changes (2020-2025)


### **Key Findings:**
Residential areas dominate Amsterdam's urban landscape, followed by industrial zones, commercial districts, and fragmented green spaces, including forests, meadows, and grasslands. A clear Urban Heat Island (UHI) signature emerges from our analysis, with built-up land uses consistently exhibiting higher temperatures, while vegetated and low-density areas remain notably cooler. Temperature hotspots cluster prominently in:

**`High-temperature zones: Dense urban cores, industrial corridors, and transportation networks

**`Cooler zones: Forested areas, meadows, and allotment gardens

Transportation infrastructure, particularly highways, emerges as the hottest land use category, followed closely by commercial and retail zones. Residential areas rank high in temperature but are not at the very top. The coolest categories are consistently vegetated: grass, forests, allotments, and meadows. The five-year analysis reveals clear climate signals:

**`2022 stands out as the hottest year across all metrics (mean, maximum, and minimum temperatures).

## 🛠️ **Technical Requirements**

### **Python Packages:**
- `earthengine-api` - Google Earth Engine access
- `geemap` - Map visualization
- `geopandas` - Geographic data handling
- `rasterio` - Satellite image processing
- `matplotlib` - Plotting and charts

### **Data Sources:**
- **Temperature**: NASA MODIS satellite (1km resolution)
- **Boundaries**: PDOK Dutch government service
- **Land Use**: OpenStreetMap


## ❓ **Common Issues & Solutions**

### **"Authentication Error"**
- Make sure you've signed up for Google Earth Engine
- Run `earthengine authenticate` in terminal
- Check your internet connection


## 🔧 **Customization Options**

### **Change Study Area:**
Edit `"Amsterdam, Netherlands"` to your city in `data_collection.py`

### **Change Years:**
Modify `start_year=2020` and `end_year=2025` in `main.py`


## 📚 **Learn More**
- [Google Earth Engine Documentation](https://developers.google.com/earth-engine)
- [MODIS Satellite Data](https://modis.gsfc.nasa.gov/)
- [Urban Heat Island Basics](https://www.epa.gov/heatislands)



