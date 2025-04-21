import requests
import pandas as pd
import datetime

def list_openaq_locations_and_parameters(api_key=None):
    """Return a dictionary of {location_name: [parameters]}"""
    url = "https://api.openaq.org/v3/locations"
    headers = {"accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    params = {"country": "US", "limit": 1000}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    loc_map = {}
    for loc in response.json().get("results", []):
        name = loc["name"]
        sensors = loc.get("sensors", [])
        parameters = list({s["parameter"]["name"] for s in sensors if "parameter" in s})
        loc_map[name] = parameters
    return loc_map

def fetch_openaq_timeseries(location, parameter="pm25", days=7, api_key=None):
    """Fetch recent time-series pollution data from OpenAQ for a given location and parameter."""
    date_to = datetime.datetime.utcnow()
    date_from = date_to - datetime.timedelta(days=days)

    headers = {"accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    params = {
        "location": location,
        "parameter": parameter,
        "date_from": date_from.isoformat() + "Z",
        "date_to": date_to.isoformat() + "Z",
        "limit": 1000,
        "sort": "desc",
        "order_by": "datetime"
    }

    url = "https://api.openaq.org/v3/measurements"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json().get("results", [])

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime([d["utc"] for d in df["date"]])
    df["value"] = df["value"]
    df["unit"] = df["unit"]
    return df[["datetime", "value", "unit"]]
