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

 TODO: scales need to be on same level for each travel time cut-off
 
 """)

# Read in unique_mncplty.csv
municipalities = pd.read_csv('streamlit/data/unique_mncplty.csv')

# Get unique values from the 'municipality' column
municipalities = municipalities['mncplty'].unique()

# Add an "Finland" option to the municipalities list so that data can be looked at nationally
municipalities = np.insert(municipalities, 0, 'Finland')

# Add an empty option to the municipalities list
municipalities = np.insert(municipalities, 0, '')

col1, col2 = st.columns([1, 1])

with col1:
    # Create a selectbox for different municipalities with an empty option
    selected_municipality = st.selectbox('Select area of interest', municipalities)

    # Create a selectbox for different modes of transportation with an empty option
    selected_mode = st.selectbox('Select mode', ('', 'Public transport', 'Bicycle'))

with col2:
    # Create a selectbox for different opportunity types with an empty option
    opportunity_type = st.selectbox("Select opportunity types:", ("", "Pharmacy", "Grocery store", "Library", "Public sports facility", "School", "Healthcare", "Jobs"))

    travel_time = st.radio("Select travel time cut-off:", ("30 min", "45 min", "60 min"), horizontal = True)

    # Add a checkbox to the Streamlit app
    use_same_intervals = st.checkbox('Use the 60 minute class intervals for all cut-offs')

# Map the selected mode to the corresponding abbreviation in the field name
mode_abbreviation = 'JL' if selected_mode == 'Public transport' else 'PP'

if selected_municipality and selected_mode and opportunity_type:
    # Map the selected opportunity type to the corresponding abbreviation in the field name
    opportunity_type_abbreviation = {
        'Pharmacy': 'aptk',
        'Grocery store': 'ruok',
        'Library': 'kirja',
        'Public sports facility': 'lahi',
        'School': 'koul',
        'Healthcare': 'sair',
        'Jobs': 'tyo'
    }[opportunity_type]

    with st.spinner(text="Loading map..."):
        # Map the selected travel time cut-off to the corresponding value in the field name
        travel_time_value = travel_time.split()[0]

        # Construct the field name based on the selected values
        mode_column = f'{mode_abbreviation}_{opportunity_type_abbreviation}{travel_time_value}'

        # Check if data for the selected municipality has already been loaded to session state
        if f'data_{selected_municipality}' not in st.session_state:
            # Define the columns to read in
            columns = ['mncplty', 'geometry'] + [f'{mode_abbreviation}_{opp}{time}' for opp in ['aptk', 'ruok', 'kirja', 'lahi', 'koul', 'sair', 'tyo'] for time in ['30', '45', '60']]

            grid = gpd.read_file('streamlit/data/accessibility.shp', columns=columns)
            grid = grid.to_crs('EPSG:4326')

            # Filter the grid data based on the selected municipality
            if selected_municipality != 'Finland':
                filtered_grid = grid[grid['mncplty'] == selected_municipality]
                zoom_level = 10
            else:
                filtered_grid = grid
                zoom_level = 7

            # Store the loaded data in session state for reuse
            st.session_state[f'data_{selected_municipality}'] = filtered_grid

        else:
            # Retrieve the loaded data from session state
            filtered_grid = st.session_state[f'data_{selected_municipality}']

            # Set the zoom level based on the selected municipality
            zoom_level = 10 if selected_municipality != 'Finland' else 7

        if use_same_intervals:
            # Calculate the maximum value of the 60-minute column for appropriate class bins
            max_value = filtered_grid[f'{mode_abbreviation}_{opportunity_type_abbreviation}60'].max()

            # Define the bins based on the maximum value
            bins = [0, max_value / 6, max_value / 3, max_value / 2, 2 * max_value / 3, 5 * max_value / 6, max_value]
        else:
            # Calculate the maximum value of the selected travel time cut-off column for appropriate class bins
            max_value = filtered_grid[mode_column].max()

            # Define the bins based on the maximum value
            bins = [0, max_value / 6, max_value / 3, max_value / 2, 2 * max_value / 3, 5 * max_value / 6, max_value]


        # Filter the grid data based on the selected mode, opportunity type, and travel time cut-off
        filtered_grid = filtered_grid[filtered_grid[mode_column] > 0]

        # Select only the necessary columns
        filtered_grid = filtered_grid[[mode_column, 'mncplty', 'geometry']]

        # Calculate the centroid of the selected municipality's geometry so that map gets to the location of the points
        centroid = filtered_grid.geometry.unary_union.centroid

        # Create a new Folium map centered on the centroid of the selected municipality's geometry
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles="cartodbpositron")

        # Reset the index of the filtered_grid DataFrame
        filtered_grid = filtered_grid.reset_index()

        responsive_to_window_width()

        # Add a choropleth layer to the map with fixed bins
        choropleth = folium.Choropleth(
            geo_data=filtered_grid,
            name='choropleth',
            data=filtered_grid,
            columns=['index', mode_column],
            key_on='feature.properties.index',
            fill_color='YlGn',
            fill_opacity=0.6,
            line_opacity=0,
            legend_name=f'Number of accessible {opportunity_type.lower()}',
            bins=bins
        ).add_to(m)


        # Add a tooltip to the choropleth layer
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(
                fields=[mode_column],
                aliases=[f'Number of accessible {opportunity_type.lower()}'],
                localize=True
            )
        )

        folium_static(m, height=800)

else:
    st.warning('Please select area of interest, mode of transportation, and opportunity type')