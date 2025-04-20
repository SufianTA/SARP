
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from data_utils import fetch_air_quality_data
from folium.plugins import HeatMap

# --- Page setup ---
st.set_page_config(page_title="NASA Air Quality Dashboard", layout="wide")
st.title("🌍 NASA-Inspired Air Quality Dashboard")
st.markdown("""
This dashboard showcases real-time air quality monitoring using simulated EPA AirNow data. 
It demonstrates how ozone, PM2.5, and NO2 levels vary across major U.S. cities. The goal is to mimic real-world airborne or satellite data collection and present it in an accessible format for both researchers and the public.
""")
st.markdown("---")

# --- Load data ---
df = fetch_air_quality_data()

# --- Sidebar filters ---
st.sidebar.header("🔎 Filters")
pollutant = st.sidebar.selectbox("Select Pollutant", ["Ozone", "PM2.5", "NO2"])
selected_states = st.sidebar.multiselect("Filter by State", options=df["State"].unique(), default=df["State"].unique())
filtered_df = df[df["State"].isin(selected_states)]

# --- Time Series Plot ---
st.subheader(f"{pollutant} Levels by City")
fig = px.bar(filtered_df, x="City", y=pollutant, color="State",
             title=f"{pollutant} Levels on {filtered_df['DateObserved'].dt.date.iloc[0]}",
             labels={pollutant: f"{pollutant} (ppb or µg/m³)"})
st.plotly_chart(fig, use_container_width=True)

# --- Heatmap ---
st.subheader(f"Geographic Distribution of {pollutant}")
m = folium.Map(location=[filtered_df["Latitude"].mean(), filtered_df["Longitude"].mean()], zoom_start=4)
heat_data = [[row['Latitude'], row['Longitude'], row[pollutant]] for index, row in filtered_df.iterrows()]
HeatMap(heat_data, radius=15).add_to(m)
folium_static(m)

# --- Explanation Section ---
st.markdown("### 🌐 About the Pollutants")
st.markdown("""
- **Ozone (O₃)**: Formed when sunlight reacts with pollutants like NOx. High levels can irritate lungs.
- **PM2.5**: Fine inhalable particles with diameters generally 2.5 micrometers or smaller. Harmful when inhaled deeply.
- **NO₂**: Produced from burning fuel. Affects respiratory systems and contributes to smog formation.
""")
