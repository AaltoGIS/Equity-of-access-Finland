import streamlit as st
from PIL import Image

## _____________ Routing engine __________________ 

# page
st.set_page_config(page_title="Routing engine", 
                   layout="wide", 
                   initial_sidebar_state="expanded")

st.markdown("""
 ### 🖥️ **Routing engine**

 *Routing with r5r is incredibly fast. For a large region you can easily calculate multiple scenarios during a one hour meeting.  
 As the typical workflow of such routing tasks is shortened it opens up new possibilities to do more in dept analysis of distribution effects and to analyze different scenarios.*
 
 """)

# set CSS style for lineheight
st.markdown(
    """
    <style>
        .element-container p {
            line-height: 1.5;
        }
    </style>
    """,
    unsafe_allow_html=True
)

image = Image.open('streamlit/data/Kuva4.png')
st.image(image, use_column_width=True)

# Style image max widths
st.markdown(
    """
    <style>
        .element-container img {
            max-width: 1000px;
        }
    </style>
    """,
    unsafe_allow_html=True
)