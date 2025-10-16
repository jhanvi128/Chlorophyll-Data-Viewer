import os
import requests
from requests.auth import HTTPBasicAuth

# GeoServer configurations
GEOSERVER_URL = "http://localhost:8080/geoserver"
GEOSERVER_USER = "admin"
GEOSERVER_PASSWORD = "geoserver"
GEOSERVER_WORKSPACE = "netcdf_project"
NC_FILES_DIRECTORY = "D:/JANU/ISRO/December 2023 data"

# Function to check if a store exists
def check_store_exists(store_name):
    url = f"{GEOSERVER_URL}/rest/workspaces/{GEOSERVER_WORKSPACE}/coveragestores/{store_name}"
    response = requests.get(url, auth=HTTPBasicAuth(GEOSERVER_USER, GEOSERVER_PASSWORD))
    
    if response.status_code == 200:
        print(f"Store '{store_name}' already exists.")
        return True
    elif response.status_code == 404:
        print(f"Store '{store_name}' not found.")
        return False
    else:
        print(f"Error checking store existence. Status: {response.status_code}, Message: {response.text}")
        return False

# Function to create a store if it doesn't exist
def create_store(store_name, file_path):
    url = f"{GEOSERVER_URL}/rest/workspaces/{GEOSERVER_WORKSPACE}/coveragestores"
    headers = {"Content-type": "application/xml"}
    xml_data = f"""
    <coverageStore>
        <name>{store_name}</name>
        <workspace>{GEOSERVER_WORKSPACE}</workspace>
        <enabled>true</enabled>
        <type>NetCDF</type>
        <url>{file_path}</url>
    </coverageStore>
    """
    response = requests.post(url, data=xml_data, headers=headers, auth=HTTPBasicAuth(GEOSERVER_USER, GEOSERVER_PASSWORD))
    if response.status_code in [200, 201]:
        print(f"Store '{store_name}' created successfully.")
    else:
        print(f"Failed to create store '{store_name}'. Status: {response.status_code}, Message: {response.text}")

# Function to publish a single .nc file
def publish_nc_file(file_path):
    try:
        # Extract file name (without extension) to use as store name
        file_name = os.path.basename(file_path).split(".")[0]
        store_name = file_name

        # Check if the store already exists or create it
        if not check_store_exists(store_name):
            create_store(store_name, file_path)
        
        # Prepare the request URL and headers
        url = f"{GEOSERVER_URL}/rest/workspaces/{GEOSERVER_WORKSPACE}/coveragestores/{store_name}/file.netcdf"
        headers = {"Content-type": "application/octet-stream"}
        params = {
            "configure": "all",
            "coverageName": file_name  # Use file name as coverage name
        }

        # Open the file and send the request
        with open(file_path, "rb") as f:
            response = requests.put(
                url,
                params=params,
                headers=headers,
                data=f,
                auth=HTTPBasicAuth(GEOSERVER_USER, GEOSERVER_PASSWORD)
            )

        # Check the response
        if response.status_code in [200, 201]:
            print(f"Successfully published: {file_path}")
        else:
            print(f"Failed to publish {file_path}. Status: {response.status_code}, Message: {response.text}")

    except Exception as e:
        print(f"Error publishing {file_path}: {str(e)}")

# Main function to loop through all .nc files in the directory
def main():
    if not os.path.exists(NC_FILES_DIRECTORY):
        print(f"Directory not found: {NC_FILES_DIRECTORY}")
        return

    nc_files = [os.path.join(NC_FILES_DIRECTORY, f) for f in os.listdir(NC_FILES_DIRECTORY) if f.endswith(".nc")]
    if not nc_files:
        print(f"No .nc files found in directory: {NC_FILES_DIRECTORY}")
        return

    print(f"Found {len(nc_files)} .nc files. Starting publishing process...")
    for nc_file in nc_files:
        try:
            publish_nc_file(nc_file)
        except Exception as e:
            print(f"Error publishing {nc_file}: {str(e)}")
            continue

    print("Publishing process completed.")

# Entry point
if __name__ == "__main__":
    main()
	