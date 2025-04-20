
import pandas as pd
import requests
from datetime import datetime, timedelta

# Mock function to simulate EPA AirNow API data
def fetch_air_quality_data():
    # Simulated real-time air quality data
    data = [
        {"City": "Los Angeles", "State": "CA", "Latitude": 34.05, "Longitude": -118.24,
         "DateObserved": "2024-06-01", "Ozone": 72, "PM2.5": 33, "NO2": 25},
        {"City": "Houston", "State": "TX", "Latitude": 29.76, "Longitude": -95.36,
         "DateObserved": "2024-06-01", "Ozone": 65, "PM2.5": 41, "NO2": 30},
        {"City": "New York", "State": "NY", "Latitude": 40.71, "Longitude": -74.01,
         "DateObserved": "2024-06-01", "Ozone": 68, "PM2.5": 29, "NO2": 28},
        {"City": "Denver", "State": "CO", "Latitude": 39.74, "Longitude": -104.99,
         "DateObserved": "2024-06-01", "Ozone": 70, "PM2.5": 32, "NO2": 22},
        {"City": "Phoenix", "State": "AZ", "Latitude": 33.45, "Longitude": -112.07,
         "DateObserved": "2024-06-01", "Ozone": 78, "PM2.5": 45, "NO2": 35},
    ]
    df = pd.DataFrame(data)
    df["DateObserved"] = pd.to_datetime(df["DateObserved"])
    return df
