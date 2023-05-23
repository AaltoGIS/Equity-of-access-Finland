import streamlit as st
import geopandas as gpd
import pandas as pd 
import pydeck as pdk
import numpy as np
import plotly.express as px

## _____________ OPPORTUNITY CHOICE-SET __________________ 

# page
st.set_page_config(page_title="Opportunity choice-set", 
                   layout="wide", 
                   initial_sidebar_state="expanded")

st.markdown("""
            ### 📍**Opportunity choice-set**

            *description of opportunities here*
            
            """)

# Read in merged shapefile
merged_opportunities = gpd.read_file('streamlit/data/merged_opportunities.shp')

# Reproject the data to Web Mercator
merged_opportunities = merged_opportunities.to_crs('EPSG:4326')

# Get unique values from the 'municipality' column
municipalities = merged_opportunities['mncplty'].unique()

# Add an "All" option to the municipalities list so that data can be looked at nationally
municipalities = np.insert(municipalities, 0, 'Finland')

# Create a selectbox for different municipalities
selected_municipality = st.selectbox('Select a municipality', municipalities)

# Filter the data based on the selected municipality or All
if selected_municipality == 'Finland':
    filtered_data = merged_opportunities
    zoom_level = 5
    point_size = 120
else:
    filtered_data = merged_opportunities[merged_opportunities['mncplty'] == selected_municipality]
    zoom_level = 10
    point_size = 80

#----- CREATING A CHART -----

# Summarize the number of each opportunity type for the selected municipality or all
opportunities = filtered_data.groupby(['opprtnt', 'color']).size().reset_index(name='count')

# Rename the opportunity column
opportunities = opportunities.rename(columns={'opprtnt': 'Opportunity type'})

# Create a bar chart
fig = px.bar(opportunities, x='Opportunity type', y='count', color='color', text='count')

# Update the layout of the chart
fig.update_layout(
 title=f'Number of opportunities in {selected_municipality}',
 title_font_size=24,
 xaxis_title=None,
 yaxis_title=None,
 showlegend=False
)

# Update the traces of the chart
fig.update_traces(textposition='outside')

#----- CREATING A MAP ALONGSIDE CHART -----

# Calculate the centroid of the selected municipality's geometry so that map gets to the location of the points
centroid = filtered_data.geometry.unary_union.centroid

# Set the map style
map_style = 'mapbox://styles/mapbox/light-v10'

# Set the initial viewport for the map
view_state = pdk.ViewState(
 latitude=centroid.y,
 longitude=centroid.x,
 zoom=zoom_level,
 pitch=0
)
# XXXXXX Need to figure out how to get separate colors for different opportunity points XXXXX
# Create a layer for the selected municipality
municipality_layer = pdk.Layer(
 'GeoJsonLayer',
 data=filtered_data,
 get_radius = point_size,
 get_fill_color=[18, 84, 199, 140],
 get_line_color=[0, 0, 0],
 pickable=True,
)

# Create a deck.gl map
map = pdk.Deck(
    map_style=map_style,
    initial_view_state=view_state,
    layers=[municipality_layer],
     tooltip={
         'html': '<b>Name:</b> {name}',
         'style': {'backgroundColor': 'steelblue', 'color': 'white'}
         }
)

# Display the chart and map in Streamlit using columns
col1, col2 = st.columns([1, 1])
col1.plotly_chart(fig, use_container_width=True)
col2.pydeck_chart(map, use_container_width=True)


