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

    st.markdown("""
                ### 📍**Opportunity choice-set**

                *description of opportunities here*
                
                """)
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
            zoom_level = 10
        # Filter data by selected opportunity types
        filtered_data = filtered_data[filtered_data['opprtnt'].isin(selected_types)]
        m, fig = create_charts(selected_municipality, filtered_data,zoom_level,opportunity_types)

        return m, fig


def create_charts(selected_municipality, filtered_data, zoom_level,opportunity_types):
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

    #----- CREATING A MAP ALONGSIDE CHART -----
    # Calculate the centroid of the selected municipality's geometry so that map gets to the location of the points
    centroid = filtered_data.geometry.unary_union.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=zoom_level, tiles = "cartodbpositron")
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


if __name__ == "__main__":
    main()