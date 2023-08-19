import streamlit as st
from streamlit.components.v1 import html
import geopandas as gpd
import pandas as pd 
import pydeck as pdk
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import folium_static
import branca.colormap as cm



st.set_page_config(page_title="Equity of access", 
 layout="wide", 
 initial_sidebar_state="expanded")

def set_page():
    st.markdown('''
    ### **Measuring equity of access** 📏

    <span style="font-size: 18px;">This tool allows you to compare palma-ratios of the different municipalities in Finland. Palma-ratios have been calculated for each municipality, using the national cumulative accessibility distribution of grocery shops (see page <b>3. Cumulative access</b>🚌). In this context Palma-ratio is the measure of average accessibility of the richest 10 % divided by the average accessibility of the poorest 40 %. The higher the number, bigger the equity differences</b></span><br><br>A more detailed description of what the metric actually means.

    ''', unsafe_allow_html=True)


def read_data():
    data = gpd.read_file('streamlit/data/palma.gpkg')
    palma = data.to_crs('EPSG:4326')
    return palma

def filter_and_create_charts(palma):
    col1, col2 = st.columns([1, 1])

    with col1:
        selected_mode = st.selectbox('Select mode', ('', 'Public transport', 'Bicycle'))

    with col2:
        opportunity_type = st.selectbox("Select opportunity types:", ("", "Pharmacy", "Grocery store", "Library", "School", "Healthcare"))
        travel_time = st.radio("Select travel time cut-off:", ("30 min", "45 min", "60 min"), horizontal = True)

    # Map the selected mode to the corresponding abbreviation in the field name
    mode_abbreviation = 'jl' if selected_mode == 'Public transport' else 'pp'

    if selected_mode and opportunity_type:
        # Map the selected opportunity type to the corresponding abbreviation in the field name
        opportunity_type_abbreviation = {
            'Pharmacy': 'aptk',
            'Grocery store': 'ruok',
            'Library': 'kirja',
            'School': 'koul',
            'Healthcare': 'sair',
        }[opportunity_type]

        # Map the selected travel time cut-off to the corresponding value in the field name
        travel_time_value = travel_time.split()[0]
        # Construct the field name based on the selected values
        mode_column = f'{mode_abbreviation}_{opportunity_type_abbreviation}_{travel_time_value}'

        # Filter the palma data based on the selected mode, opportunity type, and travel time cut-off
        filtered_palma = palma[palma[mode_column] >= 0]

        # # Select only the necessary columns
        # filtered_palma = filtered_palma[[mode_column, 'mncplty', 'geometry']]

        # Calculate the centroid of Finland's geometry so that map gets to the location of Finland
        centroid = filtered_palma.geometry.unary_union.centroid

        # Create a new Folium map centered on Finland's geometry
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=6, tiles="cartodbpositron")

        # Reset the index of the filtered_palma DataFrame
        filtered_palma = filtered_palma.reset_index()
        responsive_to_window_width()
        m = create_map(m, filtered_palma, opportunity_type, mode_column)
        return m
    else:
        return None
def responsive_to_window_width():
    making_map_responsive = """
    <style>
    [title~="st.iframe"] { width: 100%}
    </style>
    """
    st.markdown(making_map_responsive, unsafe_allow_html=True)

def create_map(m, filtered_palma, opportunity_type, mode_column):
    filtered_palma = filtered_palma.replace([np.inf, -np.inf], np.nan).dropna(subset=[mode_column], how="any")
    # Add a choropleth layer to the map with the custom color scale
    max_value = max(filtered_palma[mode_column].max(), 10)
    choropleth = folium.Choropleth(
        geo_data=filtered_palma,
        data=filtered_palma,
        columns=['kunta', mode_column],
        key_on=f'feature.properties.kunta',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        bins = [0, 0.5, 1, 2,  4, 6, 8, 10, max_value],
        legend_name=f'Palma-ratio of accessible {opportunity_type.lower()}'
    ).add_to(m)

    # Hide the legend
    choropleth.color_scale.caption = ''
    m.add_child(choropleth.color_scale)


    # Add a tooltip to the choropleth layer
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=[mode_column],
            aliases=[f'Palma-ratio of accessible {opportunity_type.lower()}'],
            localize=True
        )
    )

    # Add filtered polygons to map
    geojson = folium.GeoJson(filtered_palma, style_function=style_polygon, highlight_function=highlight_polygon).add_to(m)
    # Add tooltip to display 'nimi' attribute on hover
    geojson.add_child(folium.features.GeoJsonTooltip(fields=['nimi'], aliases=['']))

    return m

def style_polygon(_):
    return {
        'fillColor': 'transparent',
        'color': 'transparent'
    }


def highlight_polygon(feature):
    return {
        'fillOpacity': 0,
        'weight': 3,
        'color': '#845EB8'
    }








def main():
    set_page()
    palma = read_data()
    m = filter_and_create_charts(palma)
    if m is not None:
        folium_static(m, height=800)
    else:
        st.warning('Please select mode of transportation and opportunity type')

if __name__ == "__main__":
    main()
