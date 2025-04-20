import streamlit as st
import pandas as pd
from modules.airnow_api import get_airnow_data
from modules.openaq_api import fetch_openaq_timeseries
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap
import datetime
import requests

st.set_page_config(page_title="NASA SARP - Complete Dashboard", layout="wide")
st.title("🌍 NASA SARP - U.S. Air Quality & Satellite Dashboard")

with st.expander("📘 What this dashboard does"):
    st.markdown("""
    This dashboard integrates live environmental data from:
    - **EPA AirNow**: real-time AQI for pollutants like O₃, PM2.5, NO₂, CO, SO₂
    - **OpenAQ**: time-series data of air quality parameters over the past days
    - **NASA GIBS**: satellite overlays (e.g., MODIS AOD) for atmospheric visualization

    ✅ Compare multiple cities  
    ✅ Visualize air quality on maps and charts  
    ✅ Explore time-series pollutant trends  
    ✅ Toggle satellite imagery overlays
    """)

# Default Cities
common_cities = [
    {"name": "Los Angeles", "lat": 34.05, "lon": -118.25},
    {"name": "New York", "lat": 40.71, "lon": -74.01},
    {"name": "Chicago", "lat": 41.88, "lon": -87.63},
    {"name": "Houston", "lat": 29.76, "lon": -95.36},
    {"name": "Phoenix", "lat": 33.45, "lon": -112.07},
    {"name": "San Francisco", "lat": 37.77, "lon": -122.42}
]

# Sidebar Inputs
st.sidebar.header("🔧 Configuration")
api_key = st.sidebar.text_input("🔑 EPA AirNow API Key", type="password")
openaq_key = st.sidebar.text_input("🧪 OpenAQ API Key (optional)", type="password")

default_city_names = [c["name"] for c in common_cities]
selected_cities = st.sidebar.multiselect("📍 Select Cities", default_city_names, default=default_city_names)

# Add Custom City
st.sidebar.markdown("### ➕ Add Custom City")
custom_name = st.sidebar.text_input("City Name")
custom_lat = st.sidebar.text_input("Latitude")
custom_lon = st.sidebar.text_input("Longitude")
if custom_name and custom_lat and custom_lon:
    try:
        custom_city = {"name": custom_name, "lat": float(custom_lat), "lon": float(custom_lon)}
        common_cities.append(custom_city)
        selected_cities.append(custom_name)
    except:
        st.sidebar.warning("Invalid lat/lon for custom city.")

# Chart Config
chart_type = st.sidebar.radio("📊 Time-Series Chart Type", ["Line", "Bar", "Area"])
run = st.sidebar.button("🚀 Run Dashboard")

# Hardcoded fallback values
ts_location = "Los Angeles-North Main Street"
ts_param = "pm25"
ts_days = 7

# --- RUN DASHBOARD ---
if not api_key:
    st.warning("❗ Please enter a valid EPA AirNow API key.")
elif run:
    full_aq_data = []
    heatmap_points = []

    for city_name in selected_cities:
        city = next((c for c in common_cities if c["name"] == city_name), None)
        if not city:
            continue
        try:
            aq_df = get_airnow_data(api_key, city["lat"], city["lon"])
            aq_df["City"] = city_name
            aq_df["Lat"] = city["lat"]
            aq_df["Lon"] = city["lon"]
            aq_df["CategoryName"] = aq_df["Category"].apply(lambda c: c["Name"] if isinstance(c, dict) else str(c))
            full_aq_data.append(aq_df)
            for _, row in aq_df.iterrows():
                heatmap_points.append([city["lat"], city["lon"], row["AQI"]])
        except Exception as e:
            st.warning(f"⚠️ {city_name}: {e}")

    if full_aq_data:
        combined_df = pd.concat(full_aq_data, ignore_index=True)
        st.subheader("📊 Multi-City AQI Comparison")
        st.dataframe(combined_df)

        fig = px.bar(combined_df, x="City", y="AQI", color="ParameterName", barmode="group",
                     title="Air Quality Index (AQI) by City and Pollutant")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📍 Air Quality Heatmap")
        m = folium.Map(location=[37, -95], zoom_start=4, width='100%', height='100%')
        HeatMap(heatmap_points).add_to(m)
        folium_static(m)
    else:
        st.error("No data returned from EPA AirNow for selected cities.")

    # --- Time-Series Section ---
    st.subheader("📈 Historical Time-Series (OpenAQ)")
    st.markdown("""
    **How to Read This Chart:**  
    - This graph shows pollutant trends (like PM2.5) over recent days  
    - Spikes may indicate pollution events such as wildfires, traffic, or industry  
    """)

    st.text(f"[DEBUG] Attempting to fetch: Location='{ts_location}', Parameter='{ts_param}', Days={ts_days}")
    try:
        ts_df = fetch_openaq_timeseries(ts_location, ts_param, ts_days, api_key=openaq_key)
    except Exception:
        st.warning("⚠️ No data for PM2.5 at primary location. Trying Long Beach-Wintersburg...")
        try:
            ts_location = "Long Beach-Wintersburg"
            ts_df = fetch_openaq_timeseries(ts_location, ts_param, ts_days, api_key=openaq_key)
        except Exception:
            st.warning("⚠️ Still no data. Showing sample fallback data.")
            now = datetime.datetime.utcnow()
            ts_df = pd.DataFrame({
                "datetime": [now - datetime.timedelta(days=i) for i in range(ts_days)][::-1],
                "value": [12, 18, 20, 16, 15, 17, 13],
                "unit": ["µg/m³"] * ts_days
            })

    st.text(f"[DEBUG] Returned dataframe shape: {ts_df.shape}")
    st.text("[DEBUG] Sample rows:")
    st.text(ts_df.head().to_string())

    ts_df.set_index("datetime", inplace=True)
    if chart_type == "Line":
        st.line_chart(ts_df["value"])
    elif chart_type == "Bar":
        st.bar_chart(ts_df["value"])
    elif chart_type == "Area":
        st.area_chart(ts_df["value"])

    st.caption(f"Data shown in {ts_df['unit'].iloc[0]} from OpenAQ or fallback.")

    param_info = {
        "pm25": "Fine particles (≤2.5μm) from smoke, vehicles, and industry. Affects lungs and heart.",
        "pm10": "Larger particles (≤10μm) like dust and construction debris. May affect breathing.",
        "no2":  "Nitrogen dioxide from vehicles and power plants. Causes inflammation in airways.",
        "o3":   "Ground-level ozone formed from emissions + sunlight. Can trigger asthma and smog.",
        "co":   "Carbon monoxide from incomplete combustion. Dangerous at high levels.",
        "so2":  "Sulfur dioxide from burning fossil fuels. Can irritate lungs and contribute to acid rain."
    }
    st.markdown(f"**About {ts_param.upper()}:** {param_info.get(ts_param, 'No description available.')}")

    # --- Satellite Overlay ---
    st.subheader("🛰️ NASA Satellite Overlay (MODIS AOD Example)")
    st.markdown("""
    **What Is MODIS AOD?**  
    - MODIS = NASA satellite imagery  
    - AOD = Aerosol Optical Depth (dust, smoke, particles in air)  
    """)
    add_overlay = st.checkbox("🌫️ Show MODIS Aerosol Optical Depth (AOD)")
    if add_overlay:
        try:
            today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            gibs_url = (
                f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
                f"MODIS_Terra_Aerosol/default/{today}/GoogleMapsCompatible_Level9/"
                "{z}/{y}/{x}.png"
            )
            m_overlay = folium.Map(location=[37, -95], zoom_start=4, width='100%', height='100%')
            folium.raster_layers.TileLayer(
                tiles=gibs_url,
                attr="MODIS AOD - NASA GIBS",
                name="MODIS AOD",
                overlay=True,
                control=True,
                opacity=0.5
            ).add_to(m_overlay)
            folium.LayerControl().add_to(m_overlay)
            folium_static(m_overlay)
        except Exception as e:
            st.error(f"Could not load satellite overlay: {e}")
