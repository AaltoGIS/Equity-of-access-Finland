import streamlit as st
import geopandas as gpd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import folium_static

def set_page():
    st.set_page_config(page_title="Opportunity choice-set", 
                    layout="wide", 
                    initial_sidebar_state="expanded")

    st.markdown('''
    ### **Opportunity choice-set** 🌍

    <span style="font-size: 18px;">With the tool below you can explore the distribution of different opportunities that one might consider important in their daily lives. It also contains the opportunity choice set used in the accessibility analysis of this paper. First select the opportunities you want to be displayed. Then the distribution of these opportunities across Finland. After that you can select specific municipalities to explore.</span>
    ''', unsafe_allow_html=True)

def read_data():
    data = gpd.read_file('streamlit/data/merged_opportunities.shp')
    # Reproject the data to Web Mercator
    data = data.to_crs('EPSG:4326')
    return data

def filter_and_create_charts(data):
    opportunity_types = data['opprtnt'].unique()
    selected_types = st.multiselect('Select opportunity types:', opportunity_types)

    if not selected_types:
        return None
    
    else:
        # Get unique values from the 'municipality' column
        municipalities = data['mncplty'].unique()
        # Add an "All" option to the municipalities list so that data can be looked at nationally
        municipalities = np.insert(municipalities, 0, 'Finland')
        # Create a selectbox for different municipalities
        selected_municipality = st.selectbox('Select a municipality', municipalities)
        # Filter the data based on the selected municipality or All
        if selected_municipality == 'Finland':
            filtered_data = data
            zoom_level = 5
        else:
            filtered_data = data[data['mncplty'] == selected_municipality]
            zoom_level = 9
        # Filter data by selected opportunity types
        filtered_data = filtered_data[filtered_data['opprtnt'].isin(selected_types)]
        m, fig = create_charts(selected_municipality, filtered_data,zoom_level,opportunity_types)

        return m, fig


def create_charts(selected_municipality, filtered_data, zoom_level, opportunity_types):
    # Read kunnat2023 shapefile
    municipality_polygons = gpd.read_file('streamlit/data/kunnat2023.shp')
    # Reproject the data to WGS84
    municipality_polygons = municipality_polygons.to_crs('EPSG:4326')
    
    # Summarize the number of each opportunity type for the selected municipality or all
    opportunity_sums = filtered_data.groupby(['opprtnt', 'color']).size().reset_index(name='count')
    # Rename the opportunity column
    opportunity_sums = opportunity_sums.rename(columns={'opprtnt': 'Opportunity type'})

    # Create a bar chart
    fig = px.bar(
        opportunity_sums,
        x='Opportunity type',
        y='count',
        color='Opportunity type',
        text='count',
        color_discrete_sequence=opportunity_sums['color'].unique()
    )
    # Update the layout of the chart
    fig.update_layout(
        title=f'Number of opportunities in {selected_municipality}',
        title_font_size=24,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False
    )
    fig.update_traces(textposition='outside')

    with st.spinner(text="Loading map..."):
        #----- CREATING A MAP ALONGSIDE CHART -----
        # Calculate the centroid of the selected municipality's geometry so that map gets to the location of the points
        centroid = filtered_data.geometry.unary_union.centroid
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles="cartodbpositron")
        
        # Add a polygon layer to the map for the selected municipality
        if selected_municipality != 'Finland':
            # Filter municipality polygons based on selected municipality
            filtered_polygons = municipality_polygons[municipality_polygons['nimi'] == selected_municipality]
            # Add polygon layer to map
            folium.GeoJson(
                filtered_polygons,
                style_function=lambda feature: {
                    'fillColor': 'transparent',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0,
                }
            ).add_to(m)
    
        # Add a point layer to the map for each opportunity type
        for opportunity_type in opportunity_types:
            # Filter the data to only include rows for this opportunity type
            data = filtered_data[filtered_data['opprtnt'] == opportunity_type]
            # Check if the data DataFrame is empty
            if not data.empty:
                # Get the color for this opportunity type from the first row of data
                color = data.iloc[0]['color']
                add_point_layer(data, color, m)

        return m, fig


# Define a function for adding a point layer to the map
# Add a point layer to the map for this opportunity type
def add_point_layer(gdf, color, m):
    # Add CircleMarkers to the map
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            color='white',
            weight=0.8,
            fill=True,
            fill_color=color,
            fill_opacity=1
        ).add_child(folium.Tooltip(row['name'])).add_to(m)

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

    <span style="font-size: 18px;">The data of the different opportunities has been collected from different sources, either from readily available open databases or webscraped
    and then geocoded by using python scripts. The data used here is from year 2021.</span>

    ''', unsafe_allow_html=True)
    
    st.markdown("""
        <div>
        <b>Pharmacies:</b>  
                    <div style="margin-left: 20px;">Association of Finnish Pharmacies | https://www.apteekki.fi/apteekkihaku.html</div>
        <b>Grocery shops:</b> 
                    <div style="margin-left: 20px;">Grocery shop websites | https://www.s-kaupat.fi/myymalat, https://www.k-ruoka.fi/k-citymarket?kaupat, https://www.lidl.fi/c/myymaelaet/s10021311,  https://www.m-ketju.fi/myymalat/</div>
        <b>Libraries:</b>
                    <div style="margin-left: 20px;">OpenStreetMap contributors</div>
        <b>Public sports facilities:</b>
            <div style="margin-left: 20px;">University of Jyväskylä, lipas.fi</div>
        <b>Healthcare</b>
            <div style="margin-left: 20px;">Finnish institute of health and welfare</div>
        <b>Educational facilities</b>
            <div style="margin-left: 20px;">Statistics Finland | https://www.stat.fi/org/avoindata/paikkatietoaineistot/oppilaitokset_en.html</div>
        
        </div>

        
        """, unsafe_allow_html=True)

def main():
    set_page()
    data = read_data()
    result = filter_and_create_charts(data)
    if result is not None:
        m, fig = result
        col1, col2 = st.columns([1, 1])
        col1.plotly_chart(fig, use_container_width=True)

        responsive_to_window_width()
        # Display the map in Streamlit
        with col2:
            with st.spinner(text="Loading map..."):
                folium_static(m)
    else:
        # Handle the case where filter_and_create_charts returns None
        st.warning('Please select at least one opportunity type.')
    add_description()

if __name__ == "__main__":
    main()