import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from pages.utils import DATA_FOLDER

# Bootstrap approach for mobile.

def set_page():
    """
    Sets the page and gives the introduction to the tool.
    """    
    st.set_page_config(page_title="Cumulative metrics", 
    layout="wide", 
    initial_sidebar_state="expanded")

    st.markdown('''
    ### **Closest educational facilities** 📚✏️

    <span style="font-size: 18px;">With this tool, you can compare the accessibility of educational facilities in different Finnish municipalities. The figure displays the cumulative share of the population aged 7-17 against the minimum travel time required to reach the nearest educational facility, either by cycling or public transport. This dataset considers all educational facilities for all origin locations, not just within municipal boundaries. To use the app, select the municipalities you want to analyze from the dropdown menu. By default, the graph displays data for all municipalities. To compare different selections, click the checkbox and select the municipalities you want to compare. When you hover your mouse over the cumulative figure, a popup will appear with more detailed information.</span><br>
             
    ''', unsafe_allow_html=True)

def read_data():
    """
    Reads nearest facility data needed to create cumulative figures

    Returns:
        pt_data: Contains nearest educational facility travel time data (by public transport)
        cycling_data: Contains nearest educational facility travel time data (by cycling)
        grid: Contains population data
        municipality: 

    """    
    pt_data = pd.read_csv(DATA_FOLDER / 'access_ttm_pt.csv')
    cycling_data = pd.read_csv(DATA_FOLDER / 'access_ttm_cycling.csv')
    grid = pd.read_csv(DATA_FOLDER / 'grid.csv')
    # Extract unique values for municipality column
    municipality = cycling_data['nimi'].unique()
    # Store municipality variable in st.session_state
    st.session_state.municipality = municipality

    return pt_data, cycling_data, grid, municipality


def filter_data(pt_data, cycling_data, grid):
    """
    Filters the data based on the selected municipalities and creates a figure.

    This function filters the public transportation, cycling, and population data based on the selected municipalities. It then creates a DataFrame with cumulative share data for public transportation and cycling using the `create_df` function. Finally, it creates a figure using the `create_fig` function.

    Args:
        pt_data: A DataFrame with public transportation data.
        cycling_data: A DataFrame with cycling data.
        grid: A DataFrame with population data.
        selected_municipalities: A list of selected municipalities.

    Returns:
        A figure displaying the cumulative share of public transportation and cycling for the selected municipalities.
    """
    if 'selected_municipality' not in st.session_state:
        st.session_state.selected_municipality = "All municipalities"
    col1, _ = st.columns([2,2])

    with col1:
        options = st.multiselect(
            'Select municipalities', st.session_state.municipality, key='selected_municipalities'
        )

    # Filter data based on selected municipalities
    if options:
        pt_data = pt_data[pt_data['nimi'].isin(options)].copy()
        cycling_data = cycling_data[cycling_data['nimi'].isin(options)].copy()
        grid = grid[grid['nimi'].isin(options)].copy()
    data_long = create_df(pt_data, cycling_data, grid, options)
    fig = create_fig(data_long)

    return fig

def filter_comparison_data(pt_data, cycling_data, grid):
    """
    Filters the data based on two sets of selected municipalities and creates a comparison figure.

    This function allows the user to select two sets of municipalities using Streamlit's `multiselect` widget. It then filters the public transportation, cycling, and population data based on the selected municipalities. The function creates two DataFrames with cumulative share data for public transportation and cycling using the `create_df` function. Finally, it creates a comparison figure using the `create_comparison_fig` function.

    Args:
        pt_data: A DataFrame with public transportation data.
        cycling_data: A DataFrame with cycling data.
        grid: A DataFrame with population data.

    Returns:
        A comparison figure displaying the cumulative share of public transportation and cycling for the two sets of selected municipalities.
    """    
    col1, col2 = st.columns([2,2])

    with col1:
        options1 = st.multiselect(
            'Select municipalities (selection 1):', st.session_state.municipality, key='selected_municipalities1'
        )
    with col2:
        options2 = st.multiselect(
            'Select municipalities (selection 2):', st.session_state.municipality, key='selected_municipalities2'
        )

    if not options1 or not options2:
        st.warning("Please select at least one municipality for each selection.")
        return


    # Filter data based on selected municipalities
    if options1:
        pt_data1 = pt_data[pt_data['nimi'].isin(options1)].copy()
        cycling_data1 = cycling_data[cycling_data['nimi'].isin(options1)].copy()
        grid1 = grid[grid['nimi'].isin(options1)].copy()
    else:
        pt_data1 = pt_data.copy()
        cycling_data1 = cycling_data.copy()
        grid1 = grid.copy()
    if options2:
        pt_data2 = pt_data[pt_data['nimi'].isin(options2)].copy()
        cycling_data2 = cycling_data[cycling_data['nimi'].isin(options2)].copy()
        grid2 = grid[grid['nimi'].isin(options2)].copy()
    else:
        pt_data2 = pt_data.copy()
        cycling_data2 = cycling_data.copy()
        grid2 = grid.copy()

    data_long1 = create_df(pt_data1, cycling_data1, grid1, options1)
    data_long2 = create_df(pt_data2, cycling_data2, grid2, options2)
    fig = create_comparison_fig(data_long1, data_long2, options1, options2)
    return fig


def create_df(pt_data, cycling_data, grid, options):
    """Create a DataFrame with cumulative share data for public transportation and cycling.

    This function calculates the cumulative share of public transportation (PT) and cycling for a range of travel times from 0 to max_travel_time. The result is stored in a DataFrame with columns for travel time, access, mode, and kunta.

    Args:
        pt_data: A DataFrame with public transportation data.
        cycling_data: A DataFrame with cycling data.
        grid: A DataFrame with population data.
        options: A list of options for the kunta column.

    Returns:
        A DataFrame with cumulative share data for public transportation and cycling.
    """
    max_travel_time = 60
    cumulative_share_pt = [sum(pt_data.loc[pt_data['trv__50'] <= x, ['he_7_12', 'h_13_15', 'h_16_17']].sum(axis=1)) /
                            grid[['he_7_12', 'he_13_15', 'he_16_17']].sum().sum() for x in range(0, max_travel_time + 1)]
    cumulative_share_cycling = [sum(cycling_data.loc[cycling_data['trv__50'] <= x, ['he_7_12', 'h_13_15', 'h_16_17']].sum(axis=1)) /
                                grid[['he_7_12', 'he_13_15', 'he_16_17']].sum().sum() for x in range(0, max_travel_time + 1)]

    mode_pt = ['Public transport + 1 000 m walk'] * (max_travel_time + 1)
    mode_cycling = ['Cycling'] * (max_travel_time + 1)

    data_long = pd.DataFrame({
        'travel_time': list(range(0, max_travel_time + 1)) * 2,
        'access': cumulative_share_pt + cumulative_share_cycling,
        'mode': mode_pt + mode_cycling,
        'kunta': [', '.join(options)] * (max_travel_time + 1) * 2
    })

    return data_long


def create_comparison_fig(data_long1, data_long2, options1, options2):
    """
    Creates a comparison figure displaying the cumulative share of access with public transportation and cycling for two sets of selected municipalities.

    This function takes two DataFrames with cumulative share data for public transportation and cycling, one for each set of selected municipalities. It uses the Plotly Express `line` function to create a comparison figure displaying the cumulative share of public transportation access and cycling access for the two sets of selected municipalities.

    Args:
        data_long1: A DataFrame with cumulative share data for public transportation and cycling for the first set of selected municipalities.
        data_long2: A DataFrame with cumulative share data for public transportation and cycling for the second set of selected municipalities.
        options1: A list of selected municipalities for the first set.
        options2: A list of selected municipalities for the second set.

    Returns:
        fig: A comparison figure displaying the cumulative share of public transportation and cycling for the two sets of selected municipalities.
    """    
    if sorted(options1) == sorted(options2):
        # If options1 and options2 are the same, only plot one set of data
        fig = px.line(data_long1, x='travel_time', y='access', color='mode', color_discrete_sequence=['#DD6E82', '#476dbf'])
    else:
        if len(options1) > 3 or len(options2) > 3:
            data_long = pd.concat([data_long1.assign(comparison='Selection 1'), data_long2.assign(comparison='Selection 2')])
            fig = px.line(data_long, x='travel_time', y='access', color='comparison', line_dash='mode',
                            color_discrete_sequence=['#DD6E82', '#476dbf'])
        else:
            data_long = pd.concat([data_long1, data_long2])
            fig = px.line(data_long, x='travel_time', y='access', color='kunta', line_dash='mode',
                            color_discrete_sequence=['#DD6E82', '#476dbf'])

    fig.update_layout(
        dragmode=False,
        title='Accessibility of nearest<br>educational facilities',
        xaxis_title='Travel time to nearest <br>educational facility (min)',
        yaxis_title='Cumulative share of <br>7-17-year-old population (%)',
        legend_title='Mode',
        height=650,
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
        ),
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.30,
            xanchor="center",
            yanchor="top"
        )
    )
    fig.update_traces(hovertemplate='Travel time to nearest educational facility <b>%{x} min</b><br>Share of population that can access nearest facility: <b>%{y}</b>')
    fig.update_yaxes(tickformat='.0%')
    for trace in fig.data:
        trace.name = trace.name.replace('Cycling', '<b>Cycling</b>')
        trace.name = trace.name.replace('Public transport + 1 000 m walk', '<b>Public transport + 1 000 m walk</b>')

    return fig



def create_fig(data_long):
    """
    Creates a figure displaying the cumulative share of public transportation access and cycling access to schools for a set of selected municipalities.

    This function takes a DataFrame with cumulative share data for public transportation and cycling. It uses the Plotly Express `line` function to create a figure displaying the cumulative share of public transportation and cycling for the selected municipalities.

    Args:
        data_long: A DataFrame with cumulative share data for public transportation and cycling for the selected municipalities.

    Returns:
        fig: A figure displaying the cumulative share of public transportation and cycling for the selected municipalities.
    """
    # Plot cumulative share line graph
    nimi = ', '.join(data_long['kunta'].iloc[0]) if isinstance(data_long['kunta'].iloc[0], list) else data_long['kunta'].iloc[0] or "All municipalities"
    if len(nimi.split(',')) > 3:
        nimi = "selection"
    fig = px.line(data_long, x='travel_time', y='access', color='mode', custom_data=['mode'], color_discrete_sequence=['#DD6E82', '#476dbf'])
    fig.update_layout(
        dragmode=False,
        title=f'Accessibility of nearest<br>educational facilities in {nimi}',
        xaxis_title='Travel time to nearest<br>educational facility (min)',
        yaxis_title='Cumulative share of <br>7-17-year-old population (%)',
        legend_title='Mode',
        height=650,
        title_font=dict(
            size=22
        ),
        xaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=14)
        ),
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.3,
            xanchor="center",
            yanchor="top"
        )
    )
    fig.update_traces(hovertemplate='Travel time to nearest educational facility <b>%{x} min</b><br>Share of population that can access nearest facility: <b>%{y}</b>')
    fig.update_yaxes(tickformat='.0%')
    for trace in fig.data:
        trace.name = trace.name.replace('Cycling', '<b>Cycling</b>')
        trace.name = trace.name.replace('Public transport + 1 000 m walk', '<b>Public transport + 1 000 m walk</b>')
    return fig


def create_map(selected_municipalities):
    """
    Creates a map displaying the selected municipalities.

    This function takes a list of selected municipalities and creates a map using the Folium library. The map displays the selected municipalities as polygons. If no municipalities are selected, the map displays the entire country of Finland.

    Args:
        selected_municipalities: A list of selected municipalities.

    """
    # Select municipalities where the field in 'nimi' is same in municipality and municipality polygons and insert it to filtered_polygons
    if selected_municipalities:
        municipality_polygons = gpd.read_parquet(DATA_FOLDER / 'kunnat2023.parquet')
        municipality_polygons = municipality_polygons.to_crs('EPSG:4326')
        filtered_polygons = municipality_polygons[municipality_polygons['nimi'].isin(selected_municipalities)]
        zoom_level = 7
    else:
        finland_polygons = gpd.read_file(DATA_FOLDER / 'suomi.gpkg')
        finland_polygons = finland_polygons.to_crs('EPSG:4326')
        filtered_polygons = finland_polygons
        zoom_level = 4
    centroid = filtered_polygons.geometry.unary_union.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles="cartodbpositron")

    # Add filtered polygons to map
    geojson = folium.GeoJson(filtered_polygons, style_function=style_polygon, highlight_function=highlight_polygon).add_to(m)
    # Add tooltip to display 'nimi' attribute on hover
    geojson.add_child(folium.features.GeoJsonTooltip(fields=['nimi'], aliases=['']))
    responsive_to_window_width()
    # Display map
    folium_static(m, height=500)

def style_polygon(_):
    return {
        'fillColor': '#DD6E82',
        'color': '#DD6E82'
    }

def highlight_polygon(_):
    return {
        'fillOpacity': 0.7,
        'weight': 3,
        'fillColor': '#DD6E82',
        'color': '#DD6E82'
    }

def create_comparison_map():
    """
    Creates a comparison map displaying two sets of selected municipalities.

    This function allows the user to select two sets of municipalities using Streamlit's `multiselect` widget. It then creates a map using the Folium library. The map displays the two sets of selected municipalities as polygons in different colors.
    """    
    municipality_polygons = gpd.read_parquet(DATA_FOLDER / 'kunnat2023.parquet')
    municipality_polygons = municipality_polygons.to_crs('EPSG:4326')

    # Select municipalities where the field in 'nimi' is same in municipality and municipality polygons and insert it to filtered_polygons
    filtered_polygons = municipality_polygons[municipality_polygons['nimi'].isin(st.session_state.selected_municipalities1 + st.session_state.selected_municipalities2)]
    zoom_level = 5
    centroid = filtered_polygons.geometry.unary_union.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles="cartodbpositron")

    # Add filtered polygons to map
    geojson = folium.GeoJson(filtered_polygons, style_function=style_comparison_polygon, highlight_function=highlight_comparison_polygon).add_to(m)
    # Add tooltip to display 'nimi' attribute on hover
    geojson.add_child(folium.features.GeoJsonTooltip(fields=['nimi'], aliases=['Municipality:']))
    responsive_to_window_width()
    # Display map
    folium_static(m, height=500)

def highlight_comparison_polygon(feature):
    return {
        'fillOpacity': 0.7,
        'weight': 3,
        'fillColor': '#DD6E82' if feature['properties']['nimi'] in st.session_state.selected_municipalities1 else '#476dbf',
        'color': '#DD6E82' if feature['properties']['nimi'] in st.session_state.selected_municipalities1 else '#476dbf'
    }


def style_comparison_polygon(polygon):
    if polygon['properties']['nimi'] in st.session_state.selected_municipalities1:
        return {
            'fillColor': '#DD6E82',
            'color': '#DD6E82'
        }
    elif polygon['properties']['nimi'] in st.session_state.selected_municipalities2:
        return {
            'fillColor': '#476dbf',
            'color': '#476dbf'
        }
def responsive_to_window_width():
    """
    A function that sets the map object width according to window size
    """    
    making_map_responsive = """
    <style>
    [title~="st.iframe"] { width: 100%}
    </style>
    """
    st.markdown(making_map_responsive, unsafe_allow_html=True)

def add_description():
    """
    Adds a methodology description
    """   
    st.markdown('''
    ### **Methodology**

    <span style="font-size: 18px;"> The data on this page has been created by using the travel time matrix function of [R5R](https://github.com/ipeaGIT/r5r) to generate a 60 minute travel time matrix between the central coordinates of the 1 km x 1 km
    [Finnish population grid](https://www.stat.fi/tup/ruututietokanta/index_en.html) and coordinates of [Finnish educational facilities](https://www.stat.fi/org/avoindata/paikkatietoaineistot/oppilaitokset_en.html). For more details on the spatial distribution of education see <b>1. Spatial distribution of opportunities </b> 🌍. Based on the created travel time matrix, minimum travel cost to closest facilities has been calculated by using the [accessibility package](https://ipeagit.github.io/accessibility/#accessibility). In the calculation, all educational facilities are considered for each location, not just wihtin municipal boundaries. This is because people do not tend to move within just the boundaries of municipalities, but consider opportunities within their daily mobility areas.
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
    
    <b style="font-size: 18px;">Transportation network:</b><br> 
    <ul>
        <li>National public transport GTFS (2021):<i> Finnish environment institute, Traficom, Matkahuolto & Digitransit.</i></li>
        <li>National transportation network (2022):<i> OpenStreetMap contributors, http://download.geofabrik.de/europe/finland.html</i></li>
    </ul>
    <br><br>
    <div style="text-align: center;"">
    <i>Service hosted by GIST Lab, Aalto University. Licensed under CC-BY.</i>
    <br><br>
    <img style="align-items: center; margin-bottom: 8px;" src="https://gistlab.science/wp-content/uploads/2023/08/Aalto_logo_black.png" width="300">
    </div>



    ''', unsafe_allow_html=True)
    
def main():
    set_page()
    if 'municipality' not in st.session_state:
        pt_data, cycling_data, grid, municipality = read_data()
    else:
        try:
            pt_data, cycling_data, grid, municipality
        except NameError:
            pt_data, cycling_data, grid, municipality = read_data()
    

    col1, _ = st.columns([2, 6])
    with col1:
        compare = st.checkbox('Compare municipalities')
    if compare:
        fig = filter_comparison_data(pt_data, cycling_data, grid)
        col1, col3 = st.columns([3,1])
        if fig is not None:
            with col1:
                    st.plotly_chart(fig, use_container_width=True, responsive=True)
            with col3:
                with st.spinner(text="Loading map..."):
                    create_comparison_map()
    else:
        fig = filter_data(pt_data, cycling_data, grid)
        col1, col3 = st.columns([2.5,1])
        with col1:
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, responsive=True)
        with col3:
            st.markdown("""
                        <h5 style="text-align: center; margin-top: 3px;">Administrative borders of selected area(s)</h5>""", unsafe_allow_html=True)
            with st.spinner(text="Loading map..."):
                create_map(st.session_state.selected_municipalities)

    add_description()



if __name__ == "__main__":
    main()
