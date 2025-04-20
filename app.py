
import streamlit as st
import pandas as pd
from modules.airnow_api import get_airnow_data
from modules.noaa_api import get_noaa_weather
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap

st.set_page_config(page_title="NASA SARP Live US Dashboard", layout="wide")
st.title("🌍 NASA SARP - Live US Air Quality & Weather Dashboard")

# Default popular cities
common_cities = [
    {"name": "Los Angeles", "lat": 34.05, "lon": -118.25},
    {"name": "New York", "lat": 40.71, "lon": -74.01},
    {"name": "Chicago", "lat": 41.88, "lon": -87.63},
    {"name": "Houston", "lat": 29.76, "lon": -95.36},
    {"name": "Phoenix", "lat": 33.45, "lon": -112.07},
    {"name": "San Francisco", "lat": 37.77, "lon": -122.42}
]

# --- Sidebar ---
st.sidebar.header("🔧 Configuration")
api_key = st.sidebar.text_input("🔑 EPA AirNow API Key", type="password")
user_agent = st.sidebar.text_input("📧 NOAA User-Agent (email recommended)")

city_names = [c["name"] for c in common_cities]
selected_city = st.sidebar.selectbox("📍 Choose City", city_names)
city_info = next(city for city in common_cities if city["name"] == selected_city)

lat = st.sidebar.number_input("Latitude", value=city_info["lat"])
lon = st.sidebar.number_input("Longitude", value=city_info["lon"])
run = st.sidebar.button("📡 Fetch Live Data")

if run:
    try:
        st.subheader("Live Air Quality Data")
        aq_df = get_airnow_data(api_key, lat, lon)
        aq_df["CategoryName"] = aq_df["Category"].apply(lambda c: c["Name"])
        st.dataframe(aq_df)

        fig = px.bar(aq_df, x="ParameterName", y="AQI", color="CategoryName",
                     title="AQI by Pollutant", labels={"ParameterName": "Pollutant", "CategoryName": "Category"})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Live Weather Conditions")
        weather = get_noaa_weather(lat, lon, user_agent=user_agent)
        st.json(weather)

        st.subheader("📍 Location Heatmap")
        m = folium.Map(location=[lat, lon], zoom_start=8)
        heat_data = [[lat, lon, row['AQI']] for _, row in aq_df.iterrows()]
        HeatMap(heat_data).add_to(m)
        folium_static(m)

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
