import streamlit as st
from streamlit.components.v1 import html
import geopandas as gpd
import pandas as pd 
import pydeck as pdk
import numpy as np
import plotly.express as px

## _____________ OPPORTUNITY CHOICE-SET __________________ 

# page
st.set_page_config(page_title="Equity of access", 
 layout="wide", 
 initial_sidebar_state="expanded")


st.markdown('''
### **Measuring equity of access** 📏

<span style="font-size: 18px;">This tool allows you to compare palma-ratios of the different municipalities in Finland. Palma-ratios have been calculated for each municipality, using the national cumulative accessibility distribution of grocery shops (see page <b>3. Cumulative access</b>🚌). In this context Palma-ratio is the measure of average accessibility of the richest 10 % divided by the average accessibility of the poorest 40 %. The higher the number, bigger the equity differences</b></span><br><br>A more detailed description of what the metric actually means.

''', unsafe_allow_html=True)
