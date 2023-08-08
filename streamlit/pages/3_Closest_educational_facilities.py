import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


## _____________ OPPORTUNITY CHOICE-SET __________________ 

def set_page():
    st.set_page_config(page_title="Cumulative metrics", 
    layout="wide", 
    initial_sidebar_state="expanded")

    st.markdown("""
    ### 🚏**Accessibility data**

    *Here lets add a set of different cumulative figures to closest facilities*
    
    """)

def read_data():
    # Read data from CSV files
    pt_data = pd.read_csv('streamlit/data/access_ttm_pt.csv')
    cycling_data = pd.read_csv('streamlit/data/access_ttm_cycling.csv')
    grid = pd.read_csv('streamlit/data/grid.csv')
    # Extract unique values for municipality column
    municipality = pt_data['nimi'].unique()
        # Add an option for all municipalities
    municipality = np.append(municipality, "All municipalities")

    return pt_data, cycling_data, grid, municipality


def filter_data(pt_data, cycling_data, grid, municipality):
    
    # Create selectbox widget
    option = st.selectbox(
        'Select a municipality', municipality, index=len(municipality)-1
    )

    # Filter data based on selected municipality
    if option != "All municipalities":
        pt_data = pt_data[pt_data['nimi'] == option]
        cycling_data = cycling_data[cycling_data['nimi'] == option]
        grid = grid[grid['nimi'] == option]

    # Delete negative values from population fields
    grid.loc[grid['he_7_12'] < 0, 'he_7_12'] = 0
    grid.loc[grid['he_13_15'] < 0, 'h_13_15'] = 0
    grid.loc[grid['he_16_17'] < 0, 'h_16_17'] = 0


    pt_data.loc[pt_data['he_7_12'] < 0, 'he_7_12'] = 0
    pt_data.loc[pt_data['h_13_15'] < 0, 'h_13_15'] = 0
    pt_data.loc[pt_data['h_16_17'] < 0, 'h_16_17'] = 0

    cycling_data.loc[cycling_data['he_7_12'] < 0, 'he_7_12'] = 0
    cycling_data.loc[cycling_data['h_13_15'] < 0, 'h_13_15'] = 0
    cycling_data.loc[cycling_data['h_16_17'] < 0, 'h_16_17'] = 0

    # Calculate cumulative share for all travel times
    max_travel_time = 60
    cumulative_share_pt = [sum(pt_data.loc[pt_data['trv__50'] <= x, ['he_7_12', 'h_13_15', 'h_16_17']].sum(axis=1)) /
                            grid[['he_7_12', 'he_13_15', 'he_16_17']].sum().sum() for x in range(0, max_travel_time + 1)]
    cumulative_share_cycling = [sum(cycling_data.loc[cycling_data['trv__50'] <= x, ['he_7_12', 'h_13_15', 'h_16_17']].sum(axis=1)) /
                                 grid[['he_7_12', 'he_13_15', 'he_16_17']].sum().sum() for x in range(0, max_travel_time + 1)]
    

    # Reshape data for plotting
    data_long = pd.DataFrame({
        'Travel time': list(range(0, max_travel_time + 1)) * 2,
        'Population share': cumulative_share_pt + cumulative_share_cycling,
        'mode': ['Public Transport + 1 000 m walk'] * (max_travel_time + 1) + ['Cycling'] * (max_travel_time + 1),
        'kunta': [option] * (max_travel_time + 1) * 2
    })

    fig = create_fig(data_long)

    return fig



def create_fig(data_long):
    # Plot cumulative share line graph
    nimi = data_long['kunta'].iloc[0]
    fig = px.line(data_long, x='Travel time', y='Population share', color='mode')
    fig.update_layout(
        title=f'Accessibility of nearest educational facilities in {nimi}',
        xaxis_title='Travel time to nearest educational institution (min)',
        yaxis_title='Cumulative share of 7-17-year-old population (%)',
        legend_title='Mode'
    )
    fig.update_yaxes(tickformat='%')
    return fig



def main():
    set_page()
    try:
        pt_data, cycling_data, grid, municipality
    except NameError:
        pt_data, cycling_data, grid, municipality = read_data()
    
    fig = filter_data(pt_data, cycling_data, grid, municipality)
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()