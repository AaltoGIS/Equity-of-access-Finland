import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import numpy as np
import folium
from streamlit_folium import folium_static
from functions.markdown_functions import responsive_to_window_width


## _____________ OPPORTUNITY CHOICE-SET __________________ 

def set_page():
    st.set_page_config(page_title="Cumulative metrics", 
    layout="wide", 
    initial_sidebar_state="expanded")

    st.markdown('''
    ### **Closest educational facilities**📚✏️

    <span style="font-size: 18px;">With this tool you can compare access differences between different Finnish municipalities. The figure plots the cumulative share of 7-17 old population against the travel time it takes 
    to reach nearest educational facility for that particular population, either with cycling or public transport. <b style="color: #845EB8;">From the dropdown menu, select the municipality you want to analyze. By hovering over the cumulative figure
    you can see a popup appear that has more detailed information.</b></span>
    ''', unsafe_allow_html=True)

def read_data():
    # Read data from CSV files
    pt_data = pd.read_csv('streamlit/data/access_ttm_pt.csv')
    cycling_data = pd.read_csv('streamlit/data/access_ttm_cycling.csv')
    grid = pd.read_csv('streamlit/data/grid.csv')
    # Extract unique values for municipality column
    municipality = pt_data['nimi'].unique()
    # Add an option for all municipalities
    municipality = np.insert(municipality, 0, "All municipalities")
    # Store municipality variable in st.session_state
    st.session_state.municipality = municipality

    return pt_data, cycling_data, grid, municipality


def filter_data(pt_data, cycling_data, grid):
    
    if 'selected_municipality' not in st.session_state:
        st.session_state.selected_municipality = "All municipalities"

    option = st.selectbox(
        'Select a municipality', st.session_state.municipality, key='selected_municipality'
    )


    # Filter data based on selected municipality
    if option != "All municipalities":
        pt_data = pt_data[pt_data['nimi'] == option].copy()
        cycling_data = cycling_data[cycling_data['nimi'] == option].copy()
        grid = grid[grid['nimi'] == option].copy()

    # Delete negative values from population fields
    grid.loc[grid['he_7_12'] < 0, 'he_7_12'] = 0
    grid.loc[grid['he_13_15'] < 0, 'h_13_15'] = 0
    grid.loc[grid['he_16_17'] < 0, 'h_16_17'] = 0


    pt_data.loc[pt_data['he_7_12'] < 0, 'he_7_12'] = 0
    pt_data.loc[pt_data['h_13_15'] < 0, 'h_13_15'] = 0
    pt_data.loc[pt_data['h_16_17'] < 0, 'h_16_17'] = 0

    cycling_data.loc[cycling_data['he_7_12'] < 0, 'he_7_12'] = 0
    cycling_data.loc[cycling_data['h_13_15'] < 0, 'h_13_15'] = 0
    cycling_data.loc[cycling_data['h_16_17'] < 0, 'h_16_17'] = 0

    # Calculate cumulative share for all travel times
    max_travel_time = 60
    cumulative_share_pt = [sum(pt_data.loc[pt_data['trv__50'] <= x, ['he_7_12', 'h_13_15', 'h_16_17']].sum(axis=1)) /
                            grid[['he_7_12', 'he_13_15', 'he_16_17']].sum().sum() for x in range(0, max_travel_time + 1)]
    cumulative_share_cycling = [sum(cycling_data.loc[cycling_data['trv__50'] <= x, ['he_7_12', 'h_13_15', 'h_16_17']].sum(axis=1)) /
                                grid[['he_7_12', 'he_13_15', 'he_16_17']].sum().sum() for x in range(0, max_travel_time + 1)]

    data_long = pd.DataFrame({
        'travel_time': list(range(0, max_travel_time + 1)) * 2,
        'access': cumulative_share_pt + cumulative_share_cycling,
        'mode': ['Public Transport + 1 000 m walk'] * (max_travel_time + 1) + ['Cycling'] * (max_travel_time + 1),
        'kunta': [option] * (max_travel_time + 1) * 2
    })

    fig = create_fig(data_long)

    return fig




def create_fig(data_long):
    # Plot cumulative share line graph
    nimi = data_long['kunta'].iloc[0]
    fig = px.line(data_long, x='travel_time', y='access', color='mode', custom_data=['mode'], color_discrete_sequence=['#DD6E82', '#845EB8'])
    fig.update_layout(
        title=f'Accessibility of nearest educational facilities in {nimi}',
        xaxis_title='Travel time to nearest educational institution (min)',
        yaxis_title='Cumulative share of <br>7-17-year-old population (%)',
        legend_title='Mode',
        title_font=dict(
            size=22
        ),
        xaxis=dict(
            title_font=dict(size=18),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title_font=dict(size=18),
            tickfont=dict(size=14)
        )
    )
    fig.update_traces(hovertemplate='Travel time to nearest educational institution <b>%{x} min</b><br>Share of population that can access nearest facility: <b>%{y}</b>')
    fig.update_yaxes(tickformat='.0%')
    return fig


def create_map(selected_municipality):
    municipality_polygons = gpd.read_file('streamlit/data/kunnat2023.shp')
    municipality_polygons = municipality_polygons.to_crs('EPSG:4326')

    # Select municipalities where the field in 'nimi' is same in municipality and municipality polygons and insert it to filtered_polygons
    if selected_municipality != "All municipalities":
        filtered_polygons = municipality_polygons[municipality_polygons['nimi'] == selected_municipality]
        zoom_level = 7
    else:
        filtered_polygons = municipality_polygons
        zoom_level = 5
    centroid = filtered_polygons.geometry.unary_union.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles="cartodbpositron")

    # Add filtered polygons to map
    folium.GeoJson(filtered_polygons, style_function=style_polygon).add_to(m)
    responsive_to_window_width()
    # Display map
    folium_static(m)

def style_polygon(_):
    return {
        'fillColor': '#845EB8',
        'color': '#845EB8'
    }

def add_description():
    st.markdown('''
    ### **Methodology**

    <span style="font-size: 18px;"> The data on this page has been created by using the travel time matrix function of [R5R](https://github.com/ipeaGIT/r5r) to generate a travel time matrix between the central coordinates of the
    [Finnish population grid](https://www.stat.fi/tup/ruututietokanta/index_en.html) and coordinates of [Finnish educational institutions](https://www.stat.fi/org/avoindata/paikkatietoaineistot/oppilaitokset_en.html).
    up to 60 minutes. Based on the created travel time matrix, minimum travel cost to closest facilities has been calculated by using the [accessibility package](https://ipeagit.github.io/accessibility/#accessibility).
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
    try:
        pt_data, cycling_data, grid, municipality
    except NameError:
        pt_data, cycling_data, grid, municipality = read_data()
    
    fig = filter_data(pt_data, cycling_data, grid)
    col1, col2 = st.columns([2.3,1])
    with col1:
        st.plotly_chart(fig, use_container_width=True, responsive=True)
    with col2:
        create_map(st.session_state.selected_municipality)

    add_description()

if __name__ == "__main__":
    main()
