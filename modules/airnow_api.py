
import requests
import pandas as pd
from datetime import datetime

def get_airnow_data(api_key, latitude, longitude, distance=25):
    url = "https://www.airnowapi.org/aq/observation/latLong/current/"
    params = {
        "format": "application/json",
        "latitude": latitude,
        "longitude": longitude,
        "distance": distance,
        "API_KEY": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise ValueError(f"AirNow API error: {response.status_code}")
    data = response.json()
    df = pd.DataFrame(data)
    df["DateObserved"] = pd.to_datetime(df["DateObserved"])
    return df[["DateObserved", "ReportingArea", "StateCode", "ParameterName", "AQI", "Category"]]
