
import requests

def get_noaa_weather(lat, lon, user_agent="YourEmail@example.com"):
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/ld+json"
    }

    # Step 1: Get station info from lat/lon
    point_url = f"https://api.weather.gov/points/{lat},{lon}"
    point_response = requests.get(point_url, headers=headers)
    if point_response.status_code != 200:
        raise ValueError("Failed to get point metadata from NOAA.")
    point_data = point_response.json()
    obs_url = point_data["properties"]["observationStations"]

    # Step 2: Get list of stations
    stations_response = requests.get(obs_url, headers=headers)
    if stations_response.status_code != 200:
        raise ValueError("Failed to get station list from NOAA.")
    stations = stations_response.json()["observationStations"]
    if not stations:
        raise ValueError("No stations found.")
    latest_obs_url = f"{stations[0]}/observations/latest"

    # Step 3: Get latest observation
    obs_response = requests.get(latest_obs_url, headers=headers)
    if obs_response.status_code != 200:
        raise ValueError("Failed to fetch latest observation.")
    obs_data = obs_response.json()["properties"]

    return {
        "Temperature (°C)": obs_data["temperature"]["value"],
        "Wind Speed (m/s)": obs_data["windSpeed"]["value"],
        "Wind Direction (°)": obs_data["windDirection"]["value"],
        "Relative Humidity (%)": obs_data.get("relativeHumidity", {}).get("value")
    }
