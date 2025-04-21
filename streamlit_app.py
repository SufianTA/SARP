import streamlit as st
import pandas as pd
import datetime
import requests
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap

from modules.airnow_api import get_airnow_data
from modules.openaq_api import fetch_openaq_timeseries, list_openaq_locations_and_parameters

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

# --- Default Cities ---
common_cities = [
    {"name": "Los Angeles", "lat": 34.05, "lon": -118.25},
    {"name": "New York", "lat": 40.71, "lon": -74.01},
    {"name": "Chicago", "lat": 41.88, "lon": -87.63},
    {"name": "Houston", "lat": 29.76, "lon": -95.36},
    {"name": "Phoenix", "lat": 33.45, "lon": -112.07},
    {"name": "San Francisco", "lat": 37.77, "lon": -122.42}
]

# --- Sidebar Configuration ---
st.sidebar.header("🔧 Configuration")
api_key = st.sidebar.text_input("🔑 EPA AirNow API Key", type="password")
openaq_key = st.sidebar.text_input("🧪 OpenAQ API Key", type="password")

default_city_names = [c["name"] for c in common_cities]
selected_cities = st.sidebar.multiselect("📍 Select Cities", default_city_names, default=default_city_names)

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

chart_type = st.sidebar.radio("📊 Chart Type", ["Line", "Bar", "Area"])

# --- Dynamically list OpenAQ locations and sensors ---
st.sidebar.markdown("### 📈 Time-Series Configuration")
ts_locations = []
ts_parameters = []

if openaq_key:
    try:
        loc_map = list_openaq_locations_and_parameters(api_key=openaq_key)
        ts_locations = sorted(loc_map.keys())
    except Exception as e:
        st.sidebar.warning(f"Failed to fetch OpenAQ locations: {e}")

if not ts_locations:
    ts_locations = ["Long Beach-Wintersburg"]

selected_location = st.sidebar.selectbox("OpenAQ Location", ts_locations)

try:
    loc_map = list_openaq_locations_and_parameters(api_key=openaq_key)
    ts_parameters = loc_map.get(selected_location, ["pm25"])
except:
    ts_parameters = ["pm25"]

ts_days = st.sidebar.slider("📆 Days Back", 1, 14, 7)

run = st.sidebar.button("🚀 Run Dashboard")

# --- Main Run Block ---
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

    # --- Time-Series All Parameters ---
    st.subheader("📈 Historical Time-Series (OpenAQ)")
    st.markdown("""
    **How to Read This Chart:**  
    This graph shows pollutant trends over recent days.  
    Spikes may indicate pollution events such as wildfires, traffic, or industry.
    """)

    all_data = []
    for ts_param in ts_parameters:
        try:
            #st.text(f"[DEBUG] Fetching: Location='{selected_location}', Parameter='{ts_param}', Days={ts_days}")
            ts_df = fetch_openaq_timeseries(selected_location, ts_param, ts_days, api_key=openaq_key)
            if not ts_df.empty:
                ts_df["parameter"] = ts_param
                all_data.append(ts_df)
        except Exception as e:
            test = e
            #st.warning(f"❗ {ts_param.upper()} failed: {e}")
    if all_data:
        combined_ts = pd.concat(all_data)
        fig = px.line(combined_ts, x="datetime", y="value", color="parameter",
                      title=f"Pollution Trend at {selected_location}")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Data shown from OpenAQ for {selected_location}")
    else:
        # If no real data is found, show sample fallback with multiple pollutants
        st.warning("⚠️ No valid historical data found. Showing fallback sample.")
        now = datetime.datetime.utcnow()
        dates = [now - datetime.timedelta(days=i) for i in range(ts_days)][::-1]
        
        # Create sample values for multiple pollutants
        fallback_df = pd.DataFrame({
            "datetime": dates * 3,
            "value": [12, 18, 20, 16, 15, 17, 13] + [8, 9, 12, 11, 10, 9, 8] + [25, 22, 24, 21, 23, 22, 20],
            "parameter": ["pm25"] * ts_days + ["no2"] * ts_days + ["o3"] * ts_days
        })
        
        # Draw a multi-line chart for the fallback data
        fig = px.line(fallback_df, x="datetime", y="value", color="parameter",
                    title="Fallback Sample Trend for PM2.5, NO₂, and O₃")
        fig.update_layout(xaxis_title="Date", yaxis_title="Concentration (µg/m³)")
        st.plotly_chart(fig, use_container_width=True)

    # --- NASA MODIS GIBS Multi-Layer Overlay ---
    st.subheader("🛰️ NASA Satellite Overlays (MODIS + More)")
    st.markdown("""
    **What Is MODIS AOD?**  
    - AOD = Aerosol Optical Depth, showing smoke, haze, and particles  
    - Fire layers = thermal anomalies from wildfires and industrial heat  
    - True Color = visible-light satellite photo (useful for visual reference)  
    """)
    
    add_overlay = st.checkbox("🌫️ Show Enhanced MODIS Layers", value=True)
    if add_overlay:
        try:
            today = "2024-07-15"  # Use a past date with known data
            center_lat, center_lon = 36.6, -119.5  # San Joaquin Valley (dust/haze hotspot)
            m_overlay = folium.Map(location=[center_lat, center_lon], zoom_start=6, width='100%', height='100%')
    
            # Define GIBS layers to add
            layers = {
                "MODIS AOD": f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_Aerosol/default/{today}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.png",
                "Fires (MODIS)": f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/FIRMS_MODIS_All/default/{today}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.png",
                "Cloud Optical Thickness": f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Cloud_Optical_Thickness/default/{today}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.png",
                "True Color (Day)": f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{today}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.png"
            }
    
            # Add layers
            for name, url in layers.items():
                folium.raster_layers.TileLayer(
                    tiles=url,
                    name=name,
                    attr="NASA GIBS",
                    overlay=True,
                    control=True,
                    opacity=0.6
                ).add_to(m_overlay)
    
            # Marker and layer control
            folium.Marker([center_lat, center_lon], popup="San Joaquin Valley, CA").add_to(m_overlay)
            folium.LayerControl().add_to(m_overlay)
    
            # Debug info
            st.markdown("🛰️ **Debug Info:**")
            for name, url in layers.items():
                st.code(f"{name}:\n{url}")
            st.text(f"Center: lat={center_lat}, lon={center_lon}, Date={today}")
    
            folium_static(m_overlay)
        except Exception as e:
            st.error(f"Could not load satellite overlays: {e}")
    
        
            
    
        
    