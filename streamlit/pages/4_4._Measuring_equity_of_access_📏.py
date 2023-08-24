import streamlit as st
from streamlit.components.v1 import html
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import branca.colormap as cm


def set_page():
    """
    Sets the page and gives the introduction to the tool.
    """
    st.set_page_config(page_title="Equity of access", 
    layout="wide", 
    initial_sidebar_state="expanded")
    st.markdown('''
    ### **Measuring equity of access** 📏

    <span style="font-size: 18px;">This tool allows you to compare the equity of access between different municipalities in Finland, by using Palma ratio. The Palma ratio is calculated using the national cumulative accessibility distribution of opportunities (found on page <b>3. Cumulative access of opportunities </b>🚌) and mean income of population within each 1 km x 1 km grid cell. Results are aggregated on a municipal level. In this context the ratio measures the average accessibility of the top 10% income residents within a municipality divided by the average accessibility of the bottom 40% income residents. A higher Palma ratio indicates greater equity difference in access when income changes. For example, a Palma ratio of 10 means that the top 10% income residents have 10 times better access than the bottom 40% income residents. <br><br><i><b>Note:</b> In the map and table below some municipalities are not present. This is the case when there are not enough data points or the access is at an equilibrium (in this case this usually means there are no access with the particular modes). Some municipalities also contain extream differences, particularly in municipalities that have a large surface area and low population density.</i></span><br><br>

    ''', unsafe_allow_html=True)


def read_data():
    """
    Reads and reprojects palma data
    """
    data = gpd.read_file('streamlit/data/palma.gpkg')
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
        selected_mode = st.selectbox('Select mode', ('Public transport + 1 000 m walk', 'Bicycle'))
        travel_time = st.radio("Select travel time cut-off:", ("30 min", "45 min", "60 min"), horizontal = True)
    with col2:
        opportunity_type = st.selectbox("Select opportunity type:", ("Pharmacy", "Grocery store", "Library", "School", "Healthcare"))
        

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
        }[opportunity_type]

        # Map the selected travel time cut-off to the corresponding value in the field name
        travel_time_value = travel_time.split()[0]
        # Construct the field name based on the selected values
        mode_column = f'{mode_abbreviation}_{opportunity_type_abbreviation}_{travel_time_value}'

        # Filter the palma data based on the selected mode, opportunity type, and travel time cut-off
        filtered_palma = palma[palma[mode_column] >= 0]
        centroid = filtered_palma.geometry.unary_union.centroid
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=5, tiles="cartodbpositron")
        filtered_palma = filtered_palma[~filtered_palma[mode_column].isin([0, float('inf'), float('-inf'), None])]
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
        ["#FFFFC8", "#FDEBA8", "#F8CD6D", "#F5A800", "#F17B00", "#E54000", "#B51700", "#7D0025"],  # Colors
        vmin=0, vmax=10,  # Range of values
        index=[0, 1, 2, 3, 4, 6, 8, 10]  # Class intervals
    )

    choropleth = folium.GeoJson(
        filtered_palma,
        style_function=lambda feature: {
            'fillColor': fill_color(feature['properties'][mode_column]),
            'fillOpacity': 0.8,
            'weight': 0,
        },
        highlight_function=lambda feature: {
            'fillOpacity': 0.9,
            'weight': 3,
            'color': '#666',
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
        filtered_palma: a subset where 0, inf and NAN occurances have been removed
        mode_column: contains the user selection, which mode to look at

    Returns:
        m: A folium map object with choropleth layer and tooltips
    """
    # Selects the right Palma ratio field based on selection
    df = filtered_palma[['nimi', mode_column]].copy()
    df.columns = ['Kunta', 'Palma ratio']
    df = df.sort_values(by='Palma ratio', ascending=False)
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
    <br><br><i>App made by Matti Pönkänen (2023). Licensed under CC-BY.</i>

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
