import streamlit as st
from streamlit.components.v1 import html
import geopandas as gpd
import pandas as pd 
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
from functions.markdown_functions import responsive_to_window_width




## _____________ OPPORTUNITY CHOICE-SET __________________ 

# page
st.set_page_config(page_title="Access metrics", 
 layout="wide", 
 initial_sidebar_state="expanded")

st.markdown("""
 ### 🚏**Accessibility data**

 *Here is an example where you can compare 30 minute accessibility to schools either with public transport or bicycle*
 
 """)

with st.spinner(text="Loading data..."):

    # Read in shapefile
    grid = gpd.read_file('streamlit/data/grid_access.shp')

    # Reproject the data to Web Mercator
    grid = grid.to_crs('EPSG:4326')

    # Get unique values from the 'municipality' column
    municipalities = grid['mncplty'].unique()

    # Add an "All" option to the municipalities list so that data can be looked at nationally
    municipalities = np.insert(municipalities, 0, 'Finland')

# Create a selectbox for different municipalities
selected_municipality = st.selectbox('Select a municipality', municipalities)

# Filter the grid data based on the selected municipality
if selected_municipality != 'Finland':
    filtered_grid = grid[grid['mncplty'] == selected_municipality]
    zoom_level = 10
else:
    filtered_grid = grid
    zoom_level = 7

# Create a selectbox for different modes of transportation
selected_mode = st.selectbox('Select mode', ['Public transport', 'Bicycle'])

# Map the selected mode to the corresponding column in the data
mode_column = 'JL_kl30' if selected_mode == 'Public transport' else 'PP_kl30'

# Filter the grid data based on the selected mode
filtered_grid = filtered_grid[filtered_grid[mode_column] > 0]

# Select only the necessary columns
filtered_grid = filtered_grid[[mode_column, 'mncplty', 'geometry']]

# Calculate the centroid of the selected municipality's geometry so that map gets to the location of the points
centroid = filtered_grid.geometry.unary_union.centroid

with st.spinner(text="Loading map..."):
    # Create a new Folium map centered on the centroid of the selected municipality's geometry
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles = "cartodbpositron")

    # Reset the index of the filtered_grid DataFrame
    filtered_grid = filtered_grid.reset_index()

    # Add a choropleth layer to the map
    folium.Choropleth(
        geo_data=filtered_grid,
        name='choropleth',
        data=filtered_grid,
        columns=['index', mode_column],
        key_on='feature.properties.index',
        fill_color='YlGn',
        fill_opacity=0.6,
        line_opacity=0,
        legend_name='Number of accessible schools'
    ).add_to(m)

    responsive_to_window_width()

    folium_static(m)
