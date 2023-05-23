import streamlit as st
import geopandas as gpd
import pandas as pd 
import pydeck as pdk
import numpy as np
import plotly.express as px

## _____________ OPPORTUNITY CHOICE-SET __________________ 

# page
st.set_page_config(page_title="Access metrics", 
                   layout="wide", 
                   initial_sidebar_state="expanded")

st.markdown("""
            ### 🚲🚏**Accessibility data**

            *description of the accessibility metrics here*
            
            """)


# Read in shapefile
grid = gpd.read_file('streamlit/data/rttk_2019_1x1km_yhdistetty_saavutettavuus.shp')

# Reproject the data to Web Mercator
grid = grid.to_crs('EPSG:4326')