import streamlit as st
import pandas as pd
import folium
from folium import plugins

# Set title for the app
st.title("Health Data in Lebanon")

# Load the dataset
data_load_state = st.text('Loading data...')
url = "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
df = pd.read_csv(url)
data_load_state.text("Data loaded!")

# Define a dictionary with predefined coordinates
coordinates = {
    'Mount_Lebanon_Governorate': (33.8333, 35.8333),
    'South_Governorate': (33.375, 35.3667),
    'Akkar_Governorate': (34.5, 36.0),
    'North_Governorate': (34.4333, 35.8333),
    'Beqaa_Governorate': (33.7333, 35.6667),
    # Add other districts and their coordinates here
}

# Add coordinates to the dataframe
df['Latitude'] = df['refArea'].map(lambda x: coordinates.get(x, (33.8938, 35.5018))[0])
df['Longitude'] = df['refArea'].map(lambda x: coordinates.get(x, (33.8938, 35.5018))[1])

# Filter out rows with missing coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

# Sidebar: Select Areas
areas = df['refArea'].unique()
selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

# Filter the dataset based on selected areas
filtered_data = df[df['refArea'].isin(selected_areas)]

# Create a base map
m = folium.Map(location=[33.8938, 35.5018], zoom_start=8)

# Add markers for each location
for _, row in filtered_data.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=row['Nb of Covid-19 cases'] / 100,  # Adjust radius scale
        color='red' if row['Diabetes'] == 'Yes' else 'green',
        fill=True,
        fill_color='red' if row['Diabetes'] == 'Yes' else 'green',
        fill_opacity=0.6,
        popup=folium.Popup(f"{row['refArea']} - Cases: {row['Nb of Covid-19 cases']}", max_width=300)
    ).add_to(m)

# Render map in Streamlit
st.folium_static(m)

























    





