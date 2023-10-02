import streamlit as st
from streamlit.components.v1 import html
import geopandas as gpd
import folium
import numpy as np
from streamlit_folium import folium_static
import branca.colormap as cm
from pages.utils import DATA_FOLDER

def set_page():
    """
    Sets the page and gives the introduction to the tool.
    """
    st.set_page_config(page_title="Equity of access", 
    layout="wide", 
    initial_sidebar_state="expanded")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('''
        ### **Measuring equity of access** 📏

        <span style="font-size: 18px;">This tool allows you to compare the equity of access between different municipalities in Finland, by using Palma ratio. The Palma ratio is calculated using the national cumulative accessibility distribution of opportunities (found on page <b>3. Cumulative access of opportunities </b>🚌) and mean income of population within each 1 km x 1 km grid cell. Results are aggregated on a municipal level. In this context the ratio measures the average accessibility of the top 10 % income residents within a municipality divided by the average accessibility of the bottom 40 % income residents. A higher Palma ratio indicates greater equity difference in access when income changes. Values higher than 1 indicate that the top 10 % income residents have better access than the bottom 40 % income residents. For example, if a Palma ratio is 10 it indicates that the wealthiest have 10 times better access than the poorest. Values below 1 indicates that the bottom 40 % income residents have better access. A ratio of 1 indicates that the access is at an equilibrium (in many cases this usually means there are no access with the particular modes).

        ''', unsafe_allow_html=True)
    with col2:
        st.image("streamlit/pictures/palma_picture.png", use_column_width=True)

    st.markdown('''
    <i><b>Note:</b> In the map and table below some municipalities have 0 or inf values. When the values are inf, it means that there is no access for lower-income residents, but there is access for higher-income residents, resulting in inf values. On the other hand, when the value is 0, it means that there is no access for higher-income residents, but there is access for lower-income residents. Some municipalities are also not present, this is the case when there are not enough data points to present the different income deciles or there is no access with a particular mode.</i></span><br><br>

    ''', unsafe_allow_html=True)


def read_data():
    """
    Reads and reprojects palma data
    """
    data = gpd.read_file(DATA_FOLDER / 'palma_ratios_finland_for_different_opportunity_types_with_cycling_and_transit_updated.gpkg')
    palma = data.to_crs('EPSG:4326')
    return palma

def filter_and_create_charts(palma):
    """
    Filters palma data and creates a folium map object.

    Args:
        palma: palma ratio data created by the accessibility function of the accessibility R-package

    Returns:
        m: A folium map object
        filtered_palma: a subset where 0, inf and NAN occurances have been removed
        mode_column: contains the user selection, which mode to look at
    """
    col1, col2 = st.columns([1, 1])

    with col1:
        selected_mode = st.selectbox('Select mode', ('Bicycle','Public transport + 1 000 m walk'))
        travel_time = st.radio("Select travel time cut-off:", ("30 min", "45 min", "60 min"), horizontal = True)
    with col2:
        opportunity_type = st.selectbox("Select opportunity type:", ("School", "Pharmacy", "Grocery store", "Library", "Healthcare", "Jobs", "Outdoor sports facilities"))
        

    # Map the selected mode to the corresponding abbreviation in the field name
    mode_abbreviation = 'jl' if selected_mode == 'Public transport + 1 000 m walk' else 'pp'

    if selected_mode and opportunity_type:
        # Map the selected opportunity type to the corresponding abbreviation in the field name
        opportunity_type_abbreviation = {
            'Pharmacy': 'aptk',
            'Grocery store': 'ruok',
            'Library': 'kirja',
            'School': 'koul',
            'Healthcare': 'sair',
            'Jobs': "tyo",
            'Outdoor sports facilities': 'lahi'
        }[opportunity_type]

        # Map the selected travel time cut-off to the corresponding value in the field name
        travel_time_value = travel_time.split()[0]
        # Construct the field name based on the selected values
        mode_column = f'{mode_abbreviation}_{opportunity_type_abbreviation}_{travel_time_value}'
        # Count the total number of missing values in the palma DataFrame

 
        # Select the mode_column, kunta, vuosi, nimi, namn, name, and geometry columns from the palma DataFrame
        filtered_palma = palma[[mode_column, 'kunta', 'vuosi', 'nimi', 'namn', 'name', 'geometry']]

        # Filter out rows where the value in the mode_column is either np.nan or None
        filtered_palma = filtered_palma[~filtered_palma[mode_column].isin([np.nan, None])]

        centroid = filtered_palma.geometry.unary_union.centroid
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=5, tiles="cartodbpositron")
        responsive_to_window_width()
        m = create_map(m, filtered_palma, opportunity_type, mode_column)
        return m, filtered_palma, mode_column
    else:
        return None
    
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

def create_map(m, filtered_palma, opportunity_type, mode_column):
    """
    Adds choropleth layer to the initialized Folium map and adds tooltips

    Args:
        m: Folium map base centered on Finland's geometry
        filtered_palma: a subset where 0, inf and NAN occurances have been removed
        mode_column: contains the user selection, which mode to look at

    Returns:
        m: A folium map object with choropleth layer and tooltips
    """
    # Create a custom color map using a built-in color map from the branca library
    fill_color = cm.LinearColormap(
        ["#4A6FE3", "#788CE1", "#9DA8E2", "#C0C5E3", "#a6a6a6", "#E6BCC3", "#E495A5", "#DD6D87", "#D33F6A"],  # Colors
        vmin=0, vmax=2,  # Range of values
        index=[0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]  # Class intervals
    )


    choropleth = folium.GeoJson(
        filtered_palma,
        style_function=lambda feature: {
            'fillColor': fill_color(feature['properties'][mode_column]),
            'fillOpacity': 0.8,
            'weight': 1,
            'color': "#666"
        },
        highlight_function=lambda feature: {
            'fillOpacity': 0.9,
            'weight': 3,
            'color': '#ffffff',
        }
    ).add_to(m)

    # Add a tooltip to the choropleth layer to display the Palma ratio
    choropleth.add_child(
        folium.features.GeoJsonTooltip(
            fields=['nimi', mode_column],
            aliases=['Municipality''', f'Palma ratio ({opportunity_type.lower()})'],
            localize=True
        )
    )
    # Add a color scale legend to the map
    fill_color.caption = 'Palma ratio'
    m.add_child(fill_color)

    return m



def style_polygon(_):
    """
    Styling function used for highlighting map objects. A transparent layer is cast on top of the municiaplities so that highlights can be made on top of them. 
    """
    return {
        'fillColor': 'transparent',
        'color': 'transparent'
    }


def highlight_polygon(_):
    """
    Styling function used for highlighting map objects
    """
    return {
        'fillOpacity': 0,
        'weight': 3,
        'color': '#845EB8'
    }

def rank_list(filtered_palma, mode_column):
    """
    Creating a dataframe table to rank different municipalities based on Palma ratio.
        
    Args:
        filtered_palma: a subset where NA and NAN occurances have been removed
        mode_column: contains the user selection, which mode to look at

    Returns:
        m: A folium map object with choropleth layer and tooltips
    """
    # Selects the right Palma ratio field based on selection
    df = filtered_palma[['nimi', mode_column]].copy()
    df.columns = ['Kunta', 'Palma ratio']
    df = df.sort_values(by='Palma ratio', ascending=False)
    df = df.round({'Palma ratio': 4})
    df['Palma ratio'] = df['Palma ratio'].astype(str).replace('inf', "inf")
    df = df.reset_index(drop=True)
    df.index += 1
    return df


def add_description():
    """
    Adds a methodology description
    """
    st.markdown('''
    ### **Methodology**

    <span style="font-size: 18px;">Palma ratio is calculated by using the palma_ratio() function of the [accessibility package](https://ipeagit.github.io/accessibility/#accessibility). The function uses the cumulative access dataset (found on page <b>3. Cumulative access of opportunities </b>🚌) and the mean income of population within each grid cell found in the [Finnish population grid](https://www.stat.fi/tup/ruututietokanta/index_en.html).  Results are grouped and calculated for each municipality.</span>
    <br><br>
    <div style="text-align: center;"">
    <i>Service hosted by GIST Lab, Aalto University. Licensed under CC-BY.</i>
    <br><br>
    <img style="align-items: center; margin-bottom: 8px;" src="https://gistlab.science/wp-content/uploads/2023/08/Aalto_logo_black.png" width="300">
    </div>

    ''', unsafe_allow_html=True)
    

def main():
    set_page()
    palma = read_data()
    m,filtered_palma, mode_column = filter_and_create_charts(palma)
    col1, col2 = st.columns([1,1])
    if m is not None:
        with col1:
            df = rank_list(filtered_palma, mode_column)
            st.dataframe(df, width=750, height=600)
        with col2:
            folium_static(m, height=600)
    else:
        st.warning('Please select mode of transportation and opportunity type')
    add_description()

if __name__ == "__main__":
    main()
