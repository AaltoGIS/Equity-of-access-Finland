import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np

## _____________ Routing engine __________________ 

# page
st.set_page_config(page_title="Routing engine", 
                   layout="wide", 
                   initial_sidebar_state="expanded")

st.markdown("""
 ### **Routing engine** 🖥️

 As part of this research project, tests were conducted to measure the computation times of the [R5R](https://github.com/ipeaGIT/r5r) package on a typical work laptop, simulating real-life analysis workflows. The tests were run using the configuration found on the table below. Computational times for routing operations vary based on the size of the area being analyzed, mode selected, number of origins and destinations, and parameters set for the analysis. 

In a typical analysis setting the R5R package demonstrates high efficiency. Particularly for smaller regional sizes and municipalities, multiple accessibility scenarios can be run with the package within one hour. Building a multimodal routable network (with the specifications found on page **3. Cumulative access of opportunities** 🚌) takes 41 seconds for a regional area and 9 minutes for the whole nation. Calculating a travel time matrix for the whole nation for public transport takes only up to 55 minutes. Running cumulative metrics with the accessibility function for three different time scenarios for all grocery stores across the nation, took 40-44 minutes depending on the mode.
 
 """)


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


# Example dataframe
outputdframe = pd.DataFrame(
    [
        ["R5R version: 1.0.0", "AMD Ryzen 7 PRO 4750U 1.7 GHZ"],
        ["R5 version: 6.8", "36 GB of RAM (of which only 10 GB was allocated for the calculation)"],
        ["Java 11 Runtime Environment (64-bit)", "8 cores / 16 threads"],
        ["R version 4.2.2", ""]
    ],
    columns=['Software versions', 'Computer specifications']
)

# style
th_props = [
    ('font-size', '16px'),
    ('text-align', 'center'),
    ('font-weight', 'bold'),
    ('color', '#6d6d6d'),
    ('background-color', 'white')
]

td_props = [
    ('font-size', '14px')
]

styles = [
    dict(selector="th", props=th_props),
    dict(selector="td", props=td_props),
    dict(selector="th:nth-child(1)", props=[('color', 'white')]),
    dict(selector="td:nth-child(2)", props=[('font-weight', 'bold')]),
    dict(selector="th:nth-child(2)", props=[('background-color', '#574078'), ('color', 'white')]),
    dict(selector="th:nth-child(3)", props=[('background-color', '#ada07d'), ('color', 'white')]),
    dict(selector="table, th, td", props=[('border', '1px solid white')])
]

# color function
def color_cells1(x):
    c1 = 'background-color: #efe6fc'
    c2 = 'background-color: #EFEBE1'
    df1 = pd.DataFrame('', index=x.index, columns=x.columns)
    df1.iloc[:, 0] = c1
    df1.iloc[:, 1] = c2
    return df1

# table
df1 = outputdframe.style.apply(color_cells1, axis=None).set_properties(**{'text-align': 'left'}).set_table_styles(styles)

outputdframe = pd.DataFrame(
    np.array(
        [
            ["Land area", "338 440 km²", "13 248 km²"],
            ["Number of origin points", "157 784 (1 km x 1 km)", "50 473 (250 m x 250 m)"],
            ["Number of trip destinations (Grocery shops)", "2 384", "224"],
            ["Number of public transport lines", "9276", "113"],
            ["Number of edges (connections)", "2 909 608", "157 644"],
            ["Building a routable network", "552 seconds (9 min)", "41 seconds"],
            ["Calculating travel time matrix up to 60 minutes (Public transport)", "3 292 seconds (55 min)", "8 seconds"],
            ["Calculating cumulative access for one opportunity type", "2 624 seconds (44 min)", "6 seconds"]
        ]
    ),
    columns=['', 'Nation', 'Region (Pirkanmaa)']
)

# style
th_props = [
    ('font-size', '16px'),
    ('text-align', 'center'),
    ('font-weight', 'bold'),
    ('color', '#6d6d6d'),
    ('background-color', 'white')
]

td_props = [
    ('font-size', '14px')
]

styles = [
    dict(selector="th", props=th_props),
    dict(selector="td", props=td_props),
    dict(selector="th:nth-child(1)", props=[('color', 'white')]),
    dict(selector="td:nth-child(2)", props=[('font-weight', 'bold'), ('font-size', '15px'), ('background-color', '#f7f7f7')]),
    dict(selector="th:nth-child(3)", props=[('background-color', '#574078'), ('color', 'white')]),
    dict(selector="th:nth-child(4)", props=[('background-color', '#ada07d'), ('color', 'white')]),
    dict(selector="table, th, td", props=[('border', '1px solid white')])
]

# color function
def color_cells2(x):
    c1 = 'background-color: #efe6fc'
    c2 = 'background-color: #EFEBE1'
    df2 = pd.DataFrame('', index=x.index, columns=x.columns)
    df2.iloc[:, 1] = c1
    df2.iloc[:, 2] = c2
    return df2

col1, col2 = st.columns([4,2])
with col1:
    st.markdown('''
    <div style="padding-left: 35px;">
        <h4>Run times for typical calculations</h4>
    </div>
    ''', unsafe_allow_html=True)
    df2 = outputdframe.style.apply(color_cells2, axis=None).set_properties(**{'text-align': 'left'}).set_table_styles(styles)
    st.table(df2)
with col2:
    st.markdown('''
    <div style="padding-left: 27px;">
        <h4>Computer and software specifications</h4>
    </div>
    ''', unsafe_allow_html=True)
    st.table(df1)


