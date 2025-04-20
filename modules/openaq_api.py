
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_openaq_timeseries(location, parameter="pm25", days=7, api_key=None):
    headers = {"accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

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

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"OpenAQ error: {response.status_code}")

    data = response.json().get("results", [])
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["date"].apply(lambda x: x["utc"]))
    return df[["datetime", "value", "unit"]]
