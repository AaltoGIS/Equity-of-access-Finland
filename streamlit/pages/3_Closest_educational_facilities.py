import streamlit as st
import pandas as pd
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

# Read data from CSV files
data = pd.read_csv('streamlit/data/access_ttm.csv', usecols=lambda col: col != 'geometry')
data2 = pd.read_csv('streamlit/data/access_ttm_cycling.csv', usecols=lambda col: col != 'geometry')
grid = pd.read_csv('streamlit/data/grid.csv', usecols=lambda col: col != 'geometry')


# Extract unique values for municipality column
municipality = data['kunta'].unique()

# Create multiselect and slider widgets
col1, col2, col3 = st.columns([2, 0.2, 2])

with col1:
    options = st.multiselect(
        'Select a municipality', municipality
    )

with col3:
    x_axis_length = st.slider(
        'Select maximum travel-time',
        min_value=0,
        max_value=60,
        value=(0, 60),
        step=1
    )

# Filter data based on selected municipalities
if options:
    data = data[data['kunta'].isin(options)]
    data2 = data2[data2['kunta'].isin(options)]
    grid = grid[grid['kunta'].isin(options)]

# Filter data based on selected maximum travel time
max_travel_time = x_axis_length[1]
cumulative_share_pt = [sum(data.loc[data['trv__50'] <= x, ['he_7_12', 'h_13_15', 'h_16_17']].sum(axis=1)) / grid[['he_7_12', 'he_13_15', 'he_16_17']].sum().sum() for x in range(0, max_travel_time + 1)]
cumulative_share_cycling = [sum(data2.loc[data2['trv__50'] <= x, ['he_7_12', 'h_13_15', 'h_16_17']].sum(axis=1)) / grid[['he_7_12', 'he_13_15', 'he_16_17']].sum().sum() for x in range(0, max_travel_time + 1)]

# Reshape data for plotting
data_long = pd.DataFrame({
    'accessibility': list(range(0, max_travel_time + 1)) * 2,
    'cumulative_share': cumulative_share_pt + cumulative_share_cycling,
    'mode': ['Public Transport + 1 000 m walk'] * (max_travel_time + 1) + ['Cycling'] * (max_travel_time + 1)
})

# Plot cumulative share line graph
fig, ax = plt.subplots(figsize=(6, 4))
data_long.groupby('mode').plot(x='accessibility', y='cumulative_share', ax=ax)
ax.legend(['Public Transport + 1 000 m walk', 'Cycling'])
ax.set_xlabel('Travel time to nearest educational institution (min)')
ax.set_ylabel('Cumulative share of 7-17-year-old population')
ax.set_title('Accessibility of nearest educational facilities in the capital region')

st.pyplot(fig)
