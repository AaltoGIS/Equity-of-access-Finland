'''
The Web App was developed based on a demo introduced in the "Web Visualization Workshop 2023" at Aalto Geoinformatics Research Lab.
Original author of the demo that was used as a base for this app is Bryan R. Vallejo
This particular web app was produced ny Matti Pönkänen
'''

import streamlit as st
import geopandas as gpd
import pandas as pd 


## ___________________ APP _______________________ 

st.set_page_config(page_title="Accessibility web app", 
                   page_icon="🌍", 
                   layout="centered", 
                   initial_sidebar_state="auto")

# info
st.markdown("""
 <div style="display: flex; align-items: center;">
   <h2 style="margin: 0;">Measuring accessibility equity in Finland with open-sourced GIS-tools</h2>
   <img style="margin-left: auto;" src="https://raw.githubusercontent.com/ipeaGIT/r5r/master/r-package/man/figures/r5r_blue.png" width="100" height="110">
 </div>
 This web app was developed to showcase some of the national datasets produced for the research paper. 
 
 ###### 👈 ***From the sidebar you can explore different datasets produced for accessibility equity analysis***

 ## Routing engine

 *description*

 ## **Datasets**
 ##### Opportunity data (destination choice set)
 - list all data utilized for the equity analysis
 ##### National grid
 - list all data utilized for the equity analysis
 *description*
 ##### Transport modes
- list all modes analyzed
 ##### Code Repository
 - github repo
 
 *Matti Pönkänen and Geoinformatics Department at Aalto University (2023). Licensed under CC-BY.*
 
 """, unsafe_allow_html=True)

# Take a logarithmic to see how results change.  So we see how the results change and are not as clustered. As an interactive version the scatterplot
# 