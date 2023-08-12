import streamlit as st
from streamlit.components.v1 import html
import geopandas as gpd
import pandas as pd 
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import folium
import branca.colormap as cm
from streamlit_folium import folium_static



def set_page():
    st.set_page_config(page_title="Cumulative access", 
    layout="wide", 
    initial_sidebar_state="expanded")

    st.markdown('''
    ### **Cumulative access** 🚌

    <span style="font-size: 18px;">This tool allows you to explore and compare the cumulative number of opportunities accessible by public transport or bicycle in different municipalities across Finland. Start by selecting your area of interest and the type of opportunity you want to investigate. The tool will then display a map showing the distribution of access to the selected opportunity. You can also choose to view access at different travel time cut-offs and compare the results. <b style="color: #845EB8;">For more consistent comparisons across different travel times, you can opt to use the same 60-minute class intervals for each cut-off</b>.</span> 
                
    <span style="color: #845EB8; font-size: 18px;"><i>Please note that selecting ‘Finland’ as a whole may result in considerable longer loading times.</i></span>

    ''', unsafe_allow_html=True)

def read_data():
    # Read in unique_mncplty.csv
    municipalities = pd.read_csv('streamlit/data/unique_mncplty.csv')

    # Get unique values from the 'municipality' column
    municipalities = municipalities['mncplty'].unique()

    # Add an "Finland" option to the municipalities list so that data can be looked at nationally
    municipalities = np.insert(municipalities, 0, 'Finland')

    # Add an empty option to the municipalities list
    municipalities = np.insert(municipalities, 0, '')

    return municipalities


def filter_and_create_charts(municipalities):

    col1, col2 = st.columns([1, 1])

    with col1:
        selected_municipality = st.selectbox('Select area of interest', municipalities)
        selected_mode = st.selectbox('Select mode', ('', 'Public transport', 'Bicycle'))

    with col2:
        opportunity_type = st.selectbox("Select opportunity types:", ("", "Pharmacy", "Grocery store", "Library", "Public sports facility", "School", "Healthcare", "Jobs"))
        travel_time = st.radio("Select travel time cut-off:", ("30 min", "45 min", "60 min"), horizontal = True)
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

        zoom_level, bins, mode_column, filtered_grid = select_columns(travel_time, mode_abbreviation, opportunity_type_abbreviation, selected_municipality, use_same_intervals)

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

        m = create_map(m, bins, filtered_grid, opportunity_type, mode_column)
        return m
    else:
        return None

    

def select_columns(travel_time, mode_abbreviation, opportunity_type_abbreviation, selected_municipality, use_same_intervals):
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

                # Set the zoom level based on the selection
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

            return zoom_level, bins, mode_column, filtered_grid

def create_map(m, bins, filtered_grid, opportunity_type, mode_column):
    # Create a custom color map using a built-in color map from the branca library
    fill_color = cm.LinearColormap(
    ["#F3E79A", "#F9B282", "#ED7C97", "#D868A3", "#704D9E", "#573980"],  # Colors
    vmin=0, vmax=max(bins),  # Range of values
    index=[0, max(bins) / 5, 2 * max(bins) / 5, 3 * max(bins) / 5, 4 * max(bins) / 5, max(bins)]  # Class intervals
    )
    
    # Add a choropleth layer to the map with fixed bins
    choropleth = folium.GeoJson(
        filtered_grid,
        style_function=lambda feature: {
            'fillColor': fill_color(feature['properties'][mode_column]),
            'fillOpacity': 0.7,
            'weight': 0,
        }
    ).add_to(m)

    # Add a tooltip to the choropleth layer
    choropleth.add_child(
        folium.features.GeoJsonTooltip(
            fields=[mode_column],
            aliases=[f'Number of accessible {opportunity_type.lower()}'],
            localize=True
        )
    )

    # Add a color scale legend to the map
    fill_color.caption = f'Number of accessible {opportunity_type.lower()}'
    m.add_child(fill_color)

    return m

def responsive_to_window_width():
    making_map_responsive = """
    <style>
    [title~="st.iframe"] { width: 100%}
    </style>
    """
    st.markdown(making_map_responsive, unsafe_allow_html=True)

def add_description():
    st.markdown('''
    ### **Methodology**

    <span style="font-size: 18px;"> The data on this page has been created by using the accessibility function of [R5R](https://github.com/ipeaGIT/r5r) to generate cumulative accessibility metrics between the central coordinates of the
    [Finnish population grid](https://www.stat.fi/tup/ruututietokanta/index_en.html) and coordinates of different opportunity types. 
    Cumulative metrics have been calculated for three different travel time thresholds (30, 45 and 60 minutes). For more info about the distribution of opportunities, see page <b>1. Opportunity choice set</b> 🌍.
    </span>
    <br><br>
    <b style="font-size: 18px;">For cycling the following parameters were used:</b><br>
    <ul>
        <li>Level of traffic stress (LTS) tolerated by cyclist: 2 <i>(more info on LTS-values: https://docs.conveyal.com/learn-more/traffic-stress)</i></li>
        <li>Cycling speed: 15 km/h</li>
        <li>Cycling speed for network sections that exceed the set LTS-value: 3.6 km/h (walking speed)</li>
    </ul>

    <b style="font-size: 18px;">For public transport the following parameters were used:</b><br> 
    <ul>
        <li>Departure time window: 7-7:30 am  <i>(more info on departure time window: https://ipeagit.github.io/r5r/articles/time_window.html)</i></li>
        <li>Maximum number of transfers per public transport trip: 1</li>
        <li>Maximum distance one can walk to access, egress or transfer on a public transport trip: 1 km (for each leg of the journey)</li>
    </ul>



    ''', unsafe_allow_html=True)

def main():
    set_page()
    municipalities = read_data()
    m = filter_and_create_charts(municipalities)
    if m is not None:
        responsive_to_window_width()
        folium_static(m, height=800)
    else:
        st.warning('Please select area of interest, mode of transportation, and opportunity type')
    add_description()


if __name__ == "__main__":
    main()