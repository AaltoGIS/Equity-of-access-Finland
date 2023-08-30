'''
The Web App was developed based on a demo introduced in the "Web Visualization Workshop 2023" at Aalto Geoinformatics Research Lab.
Original author of the demo that was used as a base for this app is Bryan R. Vallejo
This particular web app was produced ny Matti Pönkänen (2023)
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
 <span style="font-size: 18px;">This app was developed to showcase some of the capabilities of open-source GIS tools and the national datasets produced for the research paper <i>Measuring accessibility equity in Finland with open-source GIS tools</i>. With this app, you can explore how different opportunities that most people consider necessities in their daily lives are distributed across Finland and its municipalities. You can also compare access differences between different Finnish municipalities and investigate the number of opportunities accessible by public transport or bicycle within certain time thresholds. Additionally, you have the possibility to use this tool to analyze the equity of access differences between municipalities.</span>
<br><br>
<h4 style="margin-left: -10px;">👈 From the sidebar you can explore different datasets produced for accessibility equity analysis.</h4>
<br><br><br><br>
 <i>App made by Matti Pönkänen (2023). Data hosted by Aalto University. Licensed under CC-BY.</i>
 
 """, unsafe_allow_html=True)
