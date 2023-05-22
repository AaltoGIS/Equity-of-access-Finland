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

## _________________ TABS ________________
tab1, tab2 = st.tabs(['Number of opportunities', 'Distribution of opportunities'])

with tab1:
    st.markdown("""
                ### 📍**Opportunity choice-set**
                
                The code in the backend is reading the *Bike stations* layer and sotre it in a variable.
                You can calculate frequencies or statistics of your data and call them 
                to the frontend as an informative message.
                
                For example, frequencies or statistics like:

                *description of opportunities here*
                
                """)

# Read in merged shapefile
merged_opportunities = gpd.read_file('streamlit/data/merged_shapefile.shp')

# Reproject the data to Web Mercator
merged_opportunities = merged_opportunities.to_crs('EPSG:4326')

# Get unique values from the 'municipality' column
municipalities = merged_opportunities['mncplty'].unique()

# Create a selectbox for municipalities
selected_municipality = st.selectbox('Select a municipality', municipalities)

# Filter the data based on the selected municipality
filtered_data = merged_opportunities[merged_opportunities['mncplty'] == selected_municipality]


# Summarize the number of each opportunity type for the selected municipality
opportunities = filtered_data.groupby('opprtnt').size().reset_index(name='count')

opportunities = opportunities.rename(columns={'opprtnt': 'Opportunity type'})

# Create a bar chart
fig = px.bar(opportunities, x='Opportunity type', y='count', color='Opportunity type', text='count')

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

# Set the map style
map_style = 'mapbox://styles/mapbox/light-v10'

# Set the initial viewport for the map
view_state = pdk.ViewState(
 latitude=60.164241183313685,
 longitude=24.93720902049495,
 zoom=10,
 pitch=0
)

# Create a layer for the selected municipality
municipality_layer = pdk.Layer(
 'GeoJsonLayer',
 data=filtered_data,
 get_radius = 50,
 get_fill_color=[255, 0, 0],
 pickable=True
)

# Create a deck.gl map with both layers
map = pdk.Deck(
    map_style=map_style,
    initial_view_state=view_state,
    layers=[municipality_layer]
)

# Display the chart and map in Streamlit using columns
col1, col2 = st.columns(2)
col1.plotly_chart(fig)
col2.pydeck_chart(map)
    # ## _____________ FREQUENCIES AND STATISTICS __________________ 

    # # read data
    # bikes = gpd.read_file('streamlit/data/bike-sharing-system-stations.gpkg')

    # # create DataFrame
    # bikes_df = bikes[['Name', 'x', 'y', 'Kapasiteet']].rename(columns={'x': 'longitude', 'y':'latitude'})
    # bikes_df = pd.DataFrame(bikes_df)

    # # frequencies and stats
    # count = bikes_df.Name.nunique()

    # min = bikes_df.Kapasiteet.min()
    # max = bikes_df.Kapasiteet.max()

    # avg = round(bikes_df.Kapasiteet.mean(), 2)
    # med = round(bikes_df.Kapasiteet.median(), 2)
    # std = round(bikes_df.Kapasiteet.std(), 2)
    # diff = round(avg-med, 2)

    # ## _____________ DISPLAY VALUES __________________ 

    # st.success(f'You have read successfully {count} Locations of bike stations at Helsinki-Finland')

    # col1, col2 =  st.columns(2)

    # with col1:
    #     st.info(f'The minimum bike capacity is {min} from station {bikes_df.loc[bikes_df.Kapasiteet==min].Name.unique()[0]}')

    #     st.metric('Average Capacity', value=avg, delta=f'{std} std')
        
    # with col2:
    #     st.error(f'The maximum bike capacity is {max} from station {bikes_df.loc[bikes_df.Kapasiteet==max].Name.unique()[0]}')

    #     st.metric('Median Capacity', value=med, delta=f'{diff} diff', delta_color='inverse')

    
    # with st.expander('Functions used', expanded=False):
    #     st.code("""
    #                 st.markdown()
                    
    #                 ---------------------------------------------------

    #                 column1, column2 = st.columns(2)
                    
    #                 with column1:
    #                     st.info("The minimum bike capacity...")
                        
    #                 with column2:
    #                     st.info("The maximum bike capacity...")
                        
    #                 ---------------------------------------------------
                    
    #                 st.metric('Label', value = statistic, delta = rate)
    #             """)
        
## -------------------------------------------------------------------------------------------------

# with tab2:
    
#     ## _____________ MAP __________________ 

#     st.markdown("""              
#                 ### ***Simple maps with PyDeckGl***
                
#                 If you have a dataset with ***longitude*** and ***latitude*** you can create
#                 a simple map with DeckGl. This function is already implemented in Streamlit 
#                 and supports a quick visualization. Of course, you can create more elaborated 
#                 maps but you have to create your own object and display it.
                
#                 Check out the next interactive examples:
                
#                 """)

#     # options
#     layers = ['Simple Scatter Map', 'Elaborated Scatter Map']

#     # add box
#     layer_type = st.selectbox('Choose the kind of visualization you want to display', options=layers, index=0)

#     # conditional for layers
#     if layer_type==layers[0]:
                
#         # map
#         st.map(bikes_df, zoom=10)

#         with st.expander('Code:', expanded=False):
#             st.code("""
#                     import streamlit as st
                    
#                     st.map(bikes_df, zoom=10)""")
            
#     if layer_type==layers[1]:
        
#         #map
#         st.pydeck_chart(pdk.Deck(
#                             map_style='mapbox://styles/mapbox/light-v9',
#                             tooltip={"text": "{Name}: {Kapasiteet} Bikes"},
                            
#                 initial_view_state=pdk.ViewState(
#                                                 latitude=60.171358,
#                                                 longitude=24.941349,
#                                                 zoom=11,
#                                                 pitch=45,
#                                                 ),
#                 layers=[
#                         pdk.Layer('ScatterplotLayer',
#                                 data=bikes_df,
#                                 pickable=True,
#                                 opacity=0.6,
#                                 stroked=True,
#                                 get_position='[longitude, latitude]',
#                                 get_color=[18, 84, 199],
#                                 get_line_color=[0, 0, 0],
#                                 line_width_min_pixels=1.5,
#                                 get_radius='Kapasiteet',
#                                 radius_scale=8,
#                                 radius_min_pixels=1,
#                                 radius_max_pixels=100)
#                         ],
#                     ))
        
#         with st.expander('Code:', expanded=False):
        
#             st.code("""
                    
#                 import pydeck as pdk
#                 import streamlit as st
                
#                 st.pydeck_chart(pdk.Deck(
#                             map_style='mapbox://styles/mapbox/light-v9',
#                             tooltip={"text": "{Name}: {Kapasiteet} Bikes"},
                            
#                 initial_view_state=pdk.ViewState(
#                                                 latitude=60.171358,
#                                                 longitude=24.941349,
#                                                 zoom=11,
#                                                 pitch=45,
#                                                 ),
#                 layers=[
#                         pdk.Layer('ScatterplotLayer',
#                                 data=bikes_df,
#                                 pickable=True,
#                                 opacity=0.6,
#                                 stroked=True,
#                                 get_position='[longitude, latitude]',
#                                 get_color=[18, 84, 199],
#                                 get_line_color=[0, 0, 0],
#                                 line_width_min_pixels=1.5,
#                                 get_radius='Kapasiteet',
#                                 radius_scale=8,
#                                 radius_min_pixels=1,
#                                 radius_max_pixels=100)
#                         ],
#                     ))
#                 """)
            
# ## -------------------------------------------------------------------------------------------------
