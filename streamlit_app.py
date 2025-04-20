
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

# --- Sidebar ---
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("🔑 EPA AirNow API Key", type="password")
user_agent = st.sidebar.text_input("📧 NOAA User-Agent (email recommended)")
lat = st.sidebar.number_input("Latitude", value=34.05)
lon = st.sidebar.number_input("Longitude", value=-118.25)
run = st.sidebar.button("📡 Fetch Live Data")

if run:
    try:
        st.subheader("Live Air Quality Data")
        aq_df = get_airnow_data(api_key, lat, lon)
        st.dataframe(aq_df)

        fig = px.bar(aq_df, x="ParameterName", y="AQI", color="Category",
                     title="AQI by Pollutant", labels={"ParameterName": "Pollutant"})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Live Weather Conditions")
        weather = get_noaa_weather(lat, lon, user_agent=user_agent)
        st.json(weather)

        st.subheader("📍 Location Heatmap")
        m = folium.Map(location=[lat, lon], zoom_start=8)
        heat_data = [[lat, lon, row['AQI']] for i, row in aq_df.iterrows()]
        HeatMap(heat_data).add_to(m)
        folium_static(m)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
