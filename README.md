# Chlorophyll Web App Setup

This guide explains how to set up and run the **Chlorophyll Data Visualization Web Application** using **Flask** and **Apache**.

---

## Folder Structure (Inside Apache `htdocs` Directory)

```
htdocs/
│
├── app.py                     --> Main Flask backend application
│
├── templates/
│   └── change.html            --> Frontend HTML file (UI for map and interaction)
│
├── static/                    --> Static assets like JS and CSS
│   ├── js/
│   │   └── chart.min.js       --> JavaScript library for rendering charts
│   │
│   └── css/
│       ├── ol.js              --> OpenLayers JS file for map functionality
│       └── ol.css             --> CSS styling for OpenLayers map
```

---

## System Requirements and Installation

Install the following in your `C:` drive:

* ✔ **Apache 2.4**
* ✔ **GeoServer 2.26.1**
* ✔ **Python 3.13.1**

### Install Required Python Packages

Use `.whl` files if needed:

* Download `.whl` files for:
  `Flask`, `requests`, `netCDF4`, `h5netcdf`, `numpy`, etc.
* Then install them using:

  ```bash
  pip install filename.whl
  ```

---

## Longitude Shift using NCO (NetCDF Operators)

To shift longitude by a fixed value (e.g., +100°):

1. **Open Anaconda3-2024 Prompt:**

   ```bash
   conda create -n nco_env -c conda-forge nco
   conda activate nco_env
   ```

2. **Check version:**

   ```bash
   ncap2 --version
   ```

3. **Run shift command:**

   ```bash
   ncap2 -s "lon=lon+100" E06OCML4AC_2023-12-01.nc shifted_E06OCML4AC_2023-12-01.nc
   ```

This creates a new NetCDF file with longitudes shifted by **+100°**.

---

## Running the Application

1. Ensure **Python 3** and **pip** are installed.
2. Open your terminal or command prompt and navigate to the Apache `htdocs` folder:

   ```bash
   cd /path/to/apache/htdocs
   ```
3. Install required Python libraries:

   ```bash
   pip install flask requests
   ```
4. Make sure your **GeoServer** is running at:
   `http://localhost:8080/geoserver`
   (If hosted elsewhere, update `GEOSERVER_URL` in `app.py` or set it as an environment variable.)
5. Run the Flask app:

   ```bash
   python app.py
   ```
6. Open your browser and go to:
   👉 **[http://localhost:5000/](http://localhost:5000/)**

You should see:

* A map (powered by OpenLayers)
* Options to select a date range
* Ability to click a point or draw a rectangular region
* Table and chart displaying average chlorophyll data for the selected region and dates

---

## Configuration Notes

* `app.py` → must be placed directly inside `htdocs/`
* `change.html` → inside `htdocs/templates/`
* JavaScript & CSS files → inside `htdocs/static/`:

  ```
  chart.min.js  → static/js/
  ol.js, ol.css → static/css/
  ```
* GeoServer must be configured with NetCDF data under the workspace `netcdf_project`.
* NetCDF layers should follow this format:

  ```
  netcdf_project:E06OCML4AC_YYYY-MM-DD
  Example: netcdf_project:E06OCML4AC_2023-12-01
  ```
* Flask app fetches chlorophyll data using **GeoServer WMS GetFeatureInfo** requests and supports both **point** and **region-based analysis**.

---

**Author:** Jhanvi Miteshbhai Modi
**Project:** *Chlorophyll Data Viewer*
