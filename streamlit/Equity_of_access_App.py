'''
The Web App was developed based on a demo introduced in the "Web Visualization Workshop 2023" at Aalto Geoinformatics Research Lab.
Original author of the demo that was used as a base for this app is Bryan R. Vallejo
This particular web app was produced ny Matti Pönkänen
'''

import streamlit as st


## ___________________ APP _______________________ 

st.set_page_config(page_title="Accessibility web app", 
                   page_icon="🌍", 
                   layout="wide", 
                   initial_sidebar_state="auto")

st.markdown("""
 <div style="display: flex; align-items: center;">
   <h2 style="margin: 0;">Measuring accessibility equity in Finland with open-sourced GIS-tools</h2>
   <img style="margin-left: auto;" src="https://raw.githubusercontent.com/ipeaGIT/r5r/master/r-package/man/figures/r5r_blue.png" width="100" height="110">
 </div>
 <span style="font-size: 18px;">This app was developed to showcase some of the national datasets produced for the research paper "Measuring accessibility equity in Finland with open-sourced GIS-tools". With the app, you can explore the distribution of different opportunities that one might consider important in their daily lives, compare access differences between different Finnish municipalities, and investigate the cumulative number of opportunities accessible by public transport or bicycle in different municipalities across Finland. You can also compare palma-ratios of the different municipalities in Finland and learn about the performance of the routing engine used.</span>
<br><br>
<h4 style="margin-left: -10px;">👈 From the sidebar you can explore different datasets produced for accessibility equity analysis.</h4>
<br><br><br><br>
 <i>App made by Matti Pönkänen, FLOU ltd (2023). Licensed under CC-BY.</i>
 
 """, unsafe_allow_html=True)
