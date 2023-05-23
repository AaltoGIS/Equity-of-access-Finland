import streamlit as st
from streamlit.components.v1 import html
import geopandas as gpd
import pandas as pd 
import pydeck as pdk
import numpy as np
import plotly.express as px

## _____________ OPPORTUNITY CHOICE-SET __________________ 

# page
st.set_page_config(page_title="Access metrics", 
 layout="wide", 
 initial_sidebar_state="expanded")

st.markdown("""
 ### 🚏**Accessibility data**

 *description of the accessibility metrics here*
 
 """)

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
    point_size = 80
else:
    filtered_grid = grid
    zoom_level = 5
    point_size = 120


# Calculate the centroid of the selected municipality's geometry so that map gets to the location of the points
centroid = filtered_grid.geometry.unary_union.centroid

map_style = 'mapbox://styles/mapbox/light-v10'

# Create a PyDeck map and add the filtered grid data as a layer
view_state = pdk.ViewState(
 latitude=centroid.y,
 longitude=centroid.x,
 zoom=zoom_level,
 pitch=0
)

layer = pdk.Layer(
    'GeoJsonLayer',
    data=filtered_grid,
    get_position='[lon, lat]',
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(latitude=60.192059, longitude=24.945831, zoom=10)
map = pdk.Deck(layers=[layer],
               map_style=map_style,
               initial_view_state=view_state)
st.pydeck_chart(map)

# print("here")

# # Read in shapefile
# grid = gpd.read_file('streamlit/data/grid_access.shp')

# print("here again")

# # Reproject the data to Web Mercator
# grid = grid.to_crs('EPSG:4326')

# # Get unique values from the 'municipality' column
# municipalities = grid['mncplty'].unique()

# # Add an "All" option to the municipalities list so that data can be looked at nationally
# municipalities = np.insert(municipalities, 0, 'Finland')

# # Create a selectbox for different municipalities
# selected_municipality = st.selectbox('Select a municipality', municipalities)

# # Filter the data based on the selected values
# filtered_data = grid[grid['mncplty'] == selected_municipality]

# # Calculate the centroid of the selected municipality's geometry so that map gets to the location of the points
# centroid = filtered_data.geometry.unary_union.centroid

# # Set the map style
# map_style = 'mapbox://styles/mapbox/light-v10'

# # Set the initial viewport for the map
# view_state = pdk.ViewState(
#  latitude=centroid.y,
#  longitude=centroid.x,
#  zoom=zoom_level,
#  pitch=0
# )

# # Create a layer for the selected municipality
# municipality_layer = pdk.Layer(
#  'GeoJsonLayer',
#  data=filtered_data,
#  get_radius = point_size,
#  get_fill_color=[18, 84, 199, 140],
#  get_line_color=[0, 0, 0],
#  pickable=True,
# )

# # Create a deck.gl map
# map = pdk.Deck(
#  map_style=map_style,
#  initial_view_state=view_state,
#  layers=[municipality_layer],
#  tooltip={
#  'html': '<b>Name:</b> {name}',
#  'style': {'backgroundColor': 'steelblue', 'color': 'white'}
#  }
# )

# col1, col2 = st.columns([1, 1])
# col2.pydeck_chart(map, use_container_width=True)



# # Define the path to the HTML file
# html_file = 'streamlit/data/accessibility.html'

# # Read the contents of the HTML file into a string
# with open(html_file, 'r') as f:
#     map_html = f.read()

# # Embed the HTML map in the Streamlit page
# html(map_html, height=800)