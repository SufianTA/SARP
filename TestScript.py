import requests
import pandas as pd
from datetime import datetime, timedelta

OPENAQ_KEY = "Your OPENAQ_KEY"
USER_AGENT = "your@email.com"

def test_noaa_station(station_id="KSFO", user_agent=USER_AGENT):
    print("=== NOAA Debug via Station:", station_id, "===")
    url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
    headers = {"User-Agent": user_agent, "Accept": "application/ld+json"}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        props = resp.json().get("properties", {})
        if not props:
            print("❌ No weather data available.")
        else:
            print("✅ NOAA Weather Fetch Successful")
            print("Temp (°C):", props.get("temperature", {}).get("value"))
            print("Humidity (%):", props.get("relativeHumidity", {}).get("value"))
    except Exception as e:
        print("❌ NOAA Error:", e)

def list_openaq_locations(country="US", limit=20):
    print("\n=== OpenAQ Valid Locations ===")
    url = f"https://api.openaq.org/v3/locations?country={country}&limit={limit}"
    headers = {
        "accept": "application/json",
        "X-API-Key": OPENAQ_KEY
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    for loc in results:
        print("📍", loc["name"], "-", loc.get("city", "N/A"))


def test_openaq_timeseries(location="Phoenix Supersite", parameter="pm25", days=3):
    print(f"\n=== OpenAQ Trend for {location} ===")
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    url = "https://api.openaq.org/v3/measurements"
    params = {
        "location": location,
        "parameter": parameter,
        "date_from": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "date_to": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": 1000,
        "sort": "desc",
        "order_by": "datetime"
    }
    headers = {
        "accept": "application/json",
        "X-API-Key": OPENAQ_KEY
    }
    resp = requests.get(url, headers=headers, params=params)
    print("URL:", resp.url)
    if resp.status_code == 404:
        print("❌ 404 - Location not found or deprecated.")
        return
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        print("❌ No data returned.")
    else:
        df = pd.DataFrame(results)
        print(f"✅ {len(df)} rows returned. Sample:")
        print(df[["date", "value", "unit"]].head())

# === RUN ===
if __name__ == "__main__":
    test_noaa_station()
    list_openaq_locations()
    test_openaq_timeseries()
