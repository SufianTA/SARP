import requests
import pandas as pd

def get_airnow_data(api_key, lat, lon):
    url = "https://www.airnowapi.org/aq/observation/latLong/current/"
    params = {
        "format": "application/json",
        "latitude": lat,
        "longitude": lon,
        "distance": 25,
        "API_KEY": api_key
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return pd.DataFrame(response.json())
