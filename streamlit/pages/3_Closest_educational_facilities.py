import streamlit as st
from streamlit.components.v1 import html
import geopandas as gpd
import pandas as pd 
import pydeck as pdk
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

## _____________ OPPORTUNITY CHOICE-SET __________________ 

# page
st.set_page_config(page_title="Cumulative metrics", 
 layout="wide", 
 initial_sidebar_state="expanded")

st.markdown("""
 ### 🚏**Accessibility data**

 *Here lets add a set of different cumulative figures to closest facilities*
 
 """)