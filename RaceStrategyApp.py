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

st.sidebar.title("F1 Tyre Degradation Visualization")
selected_year = st.sidebar.selectbox('Select Year', range(2018, 2024))
selected_location = st.sidebar.selectbox('Select Location', [
    'Austria', 'Hungary', 'Italy', 'Belgium', 'Netherlands', 
    'Great Britain', 'Japan', 'Monaco', 'Spain', 'United States'
])

session = load_data(selected_year, selected_location)
laps = session.laps.copy()
results = session.results
race = session

for lap in range(5):
    #turn LapTime into seconds from DD:HH:MM:SS
    laps['LapTime_seconds'] = laps['LapTime'].dt.total_seconds()

    #drop all rows with NaN in LapTime_seconds
    laps = laps.dropna(subset=['LapTime_seconds'])

    laptimemean=laps['LapTime_seconds'].mean()
    laptimestd=laps['LapTime_seconds'].std()

    #drop all rows in laps with LapTime_seconds 3 std greater than the mean lap time
    laps = laps[laps['LapTime_seconds'] < (laptimemean + 3*laptimestd)]
    
    #finding the mean and std of the Sector times
    sector1mean=laps['Sector1Time_seconds'].mean()
    sector1std=laps['Sector1Time_seconds'].std()
    sector2mean=laps['Sector2Time_seconds'].mean()
    sector2std=laps['Sector2Time_seconds'].std()
    sector3mean=laps['Sector3Time_seconds'].mean()
    sector3std=laps['Sector3Time_seconds'].std()

    #drop all rows in laps with Sector1Time 3 std greater than the mean sector time
    laps = laps[laps['Sector1Time_seconds'] < (sector1mean + 3*sector1std)]
    #drop all rows in laps with Sector2Time 3 std greater than the mean sector time
    laps = laps[laps['Sector2Time_seconds'] < (sector2mean + 3*sector2std)]
    #drop all rows in laps with Sector3Time 3 std greater than the mean sector time
    laps = laps[laps['Sector3Time_seconds'] < (sector3mean + 3*sector3std)]

#list of drivers initials
drivers=['ver','ham','gas','lec','alo','sai','oco','nor','vet','zho','rus','tsu','lat','mag','msc','ric','sto','bot','per','alb']

laps["LapTime_fuelCorrected"] = laps["LapTime_seconds"] - (
    3.3 * (laps["LapNumber"].max() - laps["LapNumber"]) / laps["LapNumber"].max()
)

#making a dictionary for colors based off of the unique tyre compound
compound_color = {
    'SOFT': '#FF0000',
    'MEDIUM': '#FFEF00',
    'HARD': '#E5E4E2',
    'INTERMEDIATE': '#008000',
    'WET': '#0000FF',
    'UNKNOWN': '#000000',
    'SUPERSOFT': '#FF1493',  # Example: Deep Pink color for SUPERSOFT
    'ULTRASOFT': '#9400D3',  # Example: Dark Violet color for ULTRASOFT
    'nan': '#808080'  # Gray color to represent NaN values
}

#change UNKNOW in the laps dataframe to SOFT
laps.loc[laps['Compound']=='UNKNOWN','Compound']='UNKNOWN'

plt.rcParams['figure.figsize'] = (20, 10)
plt.rcParams['font.family'] = 'serif'
plt.style.use('dark_background')
plt.rcParams['figure.dpi'] = 300

#kde plot to show distribution of lap times for each compound
sns.kdeplot(data=laps,x='LapTime_fuelCorrected',hue='Compound',palette=compound_color,fill=True,common_norm=False,linewidth=1.5)
plt.title(f'Tyre Life by Compound | {race.name} {race.date}', fontsize=15, fontweight='bold',color='White')
plt.xlabel('Fuel Adjusted Lap Times (seconds)', fontsize=10, fontweight='bold',color='white')
plt.ylabel('Tyre Compound', fontsize=10, fontweight='bold',color='White')
