import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import fastf1 as ff1
from matplotlib.collections import LineCollection
import matplotlib.patches as patches

@st.cache_data
def load_data(year, location):
    """Load session data with caching."""
    session = ff1.get_session(year, location, 'Race')
    session.load()
    return session

st.sidebar.title("F1 Tyre Strategy Visualization")
selected_year = st.sidebar.selectbox('Select Year', range(2018, 2024))
selected_location = st.sidebar.selectbox('Select Location', [
    'Austria', 'Hungary', 'Italy', 'Belgium', 'Netherlands', 
    'Great Britain', 'Japan', 'Monaco', 'Spain', 'United States'
])

session = load_data(selected_year, selected_location)
laps = session.laps.copy()
results = session.results
race = session

laps['LapTime_seconds'] = laps['LapTime'].dt.total_seconds()
laps = laps[laps['LapNumber'] != 1].dropna(subset=['LapTime_seconds'])

laptimemean = laps['LapTime_seconds'].mean()
laptimestd = laps['LapTime_seconds'].std()
laps = laps[laps['LapTime_seconds'] < (laptimemean + 3 * laptimestd)]

for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
    laps[f'{sector}_seconds'] = laps[sector].dt.total_seconds()
    laps = laps.dropna(subset=[f'{sector}_seconds'])
    sector_mean = laps[f'{sector}_seconds'].mean()
    sector_std = laps[f'{sector}_seconds'].std()
    laps = laps[laps[f'{sector}_seconds'] < (sector_mean + 3 * sector_std)]

laps["LapTime_fuelCorrected"] = laps["LapTime_seconds"] - (
    3.3 * (laps["LapNumber"].max() - laps["LapNumber"]) / laps["LapNumber"].max()
)

plt.rcParams['figure.dpi'] = 300
plt.rcParams['figure.figsize'] = [6, 6]
plt.rcParams['font.family'] = 'serif'
plt.style.use('dark_background')

compound_color = {    'SOFT': '#FF0000',          # Red
    'MEDIUM': '#FFEF00',        # Yellow
    'HARD': '#E5E4E2',          # Light Grey
    'INTERMEDIATE': '#008000',  # Green
    'WET': '#0000FF',           # Blue
    'UNKNOWN': '#000000',       # Black
    'SUPERSOFT': '#800080',     # Purple
    'ULTRASOFT': '#FFA500',     # Orange
    'nan': '#00008B'            # Dark Blue 
                 }

laps['Compound_Color'] = laps['Compound'].map(compound_color)

fig, ax = plt.subplots()
sns.scatterplot(x='LapNumber', y='Driver', data=laps, hue='Compound', palette=compound_color, s=60, marker='o', ax=ax)
sns.scatterplot(x='LapNumber', y='Driver', data=laps[laps['IsPitStop']], color='blue', s=100, marker='|', linewidth=1.5, ax=ax)

ax.set_title(f'Tyre Strategy | {race.weekend.name} {race.weekend.year}', fontsize=18, fontweight='bold', color='white')
ax.set_xlabel('Lap Number', fontsize=15, fontweight='bold', color='white')
ax.set_ylabel('Driver', fontsize=15, fontweight='bold', color='white')
ax.tick_params(labelsize=6, color='white')

plt.legend(bbox_to_anchor=(.15, 0), loc="lower center", ncol=laps['Compound'].nunique(), frameon=False, fontsize=10)
st.pyplot(fig)
