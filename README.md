
# NASA SARP - Live U.S. Air Quality & Weather Dashboard

This dashboard uses **live EPA AirNow and NOAA APIs** to provide:
- Real-time AQI and pollutant levels (O₃, PM2.5, NO₂, CO, SO₂)
- Real-time weather data (temperature, humidity, wind speed/direction)
- Interactive maps and charts using Plotly and Folium

## 🚀 How to Run Locally

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the app:
```
streamlit run app.py
```

3. Enter your API credentials:
- **EPA API Key:** [Get it here](https://docs.airnowapi.org/)
- **NOAA User-Agent:** Use your email (e.g. youremail@example.com)

## 🗂 Folder Structure
- `app.py` — Streamlit dashboard
- `modules/airnow_api.py` — pulls EPA AQI data
- `modules/noaa_api.py` — pulls NOAA weather data

## 🔒 No fallback or mock data. This is 100% live.
