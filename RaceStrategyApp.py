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

#list of drivers initials
drivers=['ver','ham','gas','lec','alo','sai','oco','nor','vet','zho','rus','tsu','lat','mag','msc','ric','sto','bot','per','alb']

laps["LapTime_fuelCorrected"] = laps["LapTime_seconds"] - (
    3.3 * (laps["LapNumber"].max() - laps["LapNumber"]) / laps["LapNumber"].max()
)
# Assuming session data has been loaded into the `session` variable
fig, ax = plt.subplots(figsize=(8.0, 4.9))

# Loop through all drivers in the session
for drv in session.drivers:
    drv_laps = session.laps.pick_driver(drv)

    # Get the driver's abbreviation
    abb = drv_laps['Driver'].iloc[0]

    # Get driver-specific style (color and linestyle)
    style = ff1.plotting.get_driver_style(identifier=abb,
                                          style=['color', 'linestyle'],
                                          session=session)

    # Plot lap number vs position for each driver
    ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
            label=abb, **style)

# Set axis limits and labels
ax.set_ylim([20.5, 0.5])  # Reversed to show position in ascending order (1st at the top)
ax.set_yticks([1, 5, 10, 15, 20])
ax.set_xlabel('Lap', fontsize=12)
ax.set_ylabel('Position', fontsize=12)

# Set legend and layout
ax.legend(bbox_to_anchor=(1.0, 1.02), title='Driver', loc='upper left', fontsize=10)
plt.tight_layout()

# Show the plot
plt.show()
plt.show()
