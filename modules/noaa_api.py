
import requests

def get_noaa_weather_from_station(station_id="KLAX", user_agent="youremail@example.com"):
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/ld+json"
    }
    url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError("NOAA API failed.")
    obs_data = response.json().get("properties", {})
    if not obs_data:
        raise ValueError("No weather data found.")
    return {
        "Temperature (°C)": obs_data.get("temperature", {}).get("value"),
        "Wind Speed (m/s)": obs_data.get("windSpeed", {}).get("value"),
        "Wind Direction (°)": obs_data.get("windDirection", {}).get("value"),
        "Relative Humidity (%)": obs_data.get("relativeHumidity", {}).get("value")
    }
