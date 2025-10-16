from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

GEOSERVER_URL = "http://localhost:8080/geoserver"
LAYER_PREFIX = "netcdf_project:E06OCML4AC_"

@app.route('/')
def home():
    return render_template('change.html')

@app.route('/get_chlorophyll_data', methods=['POST'])
def get_chlorophyll_data():
    data = request.json
    start_date, end_date = data['start_date'], data['end_date']
    analysis_type = data['analysis_type']
    
    results = []
    dates = get_date_range(start_date, end_date)

    if analysis_type == 'point':
        lon, lat = data['point']
        for date in dates:
            layer_name = f"{LAYER_PREFIX}{date}"
            value = fetch_point_chlorophyll(layer_name, lon, lat)
            results.append({'date': date, 'value': value})
    elif analysis_type == 'region':
        region = data['region']  # [minX, minY, maxX, maxY]
        for date in dates:
            layer_name = f"{LAYER_PREFIX}{date}"
            avg_value = fetch_region_chlorophyll(layer_name, region)
            results.append({'date': date, 'value': avg_value})

    return jsonify(results)

def get_date_range(start, end):
    date_array = []
    current_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    while current_date <= end_date:
        date_array.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    return date_array

def fetch_point_chlorophyll(layer_name, lon, lat):
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetFeatureInfo",
        "LAYERS": layer_name,
        "QUERY_LAYERS": layer_name,
        "INFO_FORMAT": "application/json",
        "BBOX": f"{lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}",  # Small bbox around point
        "WIDTH": 200,
        "HEIGHT": 200,
        "X": 100,  # Center of the image
        "Y": 100,
        "SRS": "EPSG:4326"
    }

    try:
        response = requests.get(f"{GEOSERVER_URL}/wms", params=params)
        if response.ok:
            data = response.json()
            features = data.get('features', [])
            if features:
                value = features[0]['properties'].get('Analysed_Chlorophyll_field')
                if value not in [None, 'No data']:
                    return round(float(value), 2)
        return 'No data'
    except Exception as e:
        print(f"Error fetching point data for {layer_name} at ({lon}, {lat}): {e}")
        return 'No data'

def fetch_region_chlorophyll(layer_name, region):
    GRID_SIZE = 5  # 5x5 grid for region
    min_x, min_y, max_x, max_y = region
    unique_values = set()

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = min_x + (max_x - min_x) * i / (GRID_SIZE - 1 if GRID_SIZE > 1 else 1)
            y = min_y + (max_y - min_y) * j / (GRID_SIZE - 1 if GRID_SIZE > 1 else 1)
            pixel_x = int(200 * i / (GRID_SIZE - 1 if GRID_SIZE > 1 else 1))
            pixel_y = int(200 * j / (GRID_SIZE - 1 if GRID_SIZE > 1 else 1))

            params = {
                "SERVICE": "WMS",
                "VERSION": "1.1.1",
                "REQUEST": "GetFeatureInfo",
                "LAYERS": layer_name,
                "QUERY_LAYERS": layer_name,
                "INFO_FORMAT": "application/json",
                "BBOX": f"{min_x},{min_y},{max_x},{max_y}",
                "WIDTH": 200,
                "HEIGHT": 200,
                "X": pixel_x,
                "Y": pixel_y,
                "SRS": "EPSG:4326"
            }

            try:
                response = requests.get(f"{GEOSERVER_URL}/wms", params=params)
                if response.ok:
                    data = response.json()
                    features = data.get('features', [])
                    if features:
                        value = features[0]['properties'].get('Analysed_Chlorophyll_field')
                        if value not in [None, 'No data']:
                            unique_values.add(float(value))
            except Exception as e:
                print(f"Error fetching region data for {layer_name} at ({x}, {y}): {e}")

    if unique_values:
        values_list = list(unique_values)
        avg = round(sum(values_list) / len(values_list), 2)
        print(f"Layer: {layer_name}, Unique Values: {values_list}, Average: {avg}")
        return avg
    return 'No data'

if __name__ == "__main__":
    app.run(debug=True)