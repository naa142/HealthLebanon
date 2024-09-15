import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os

# Streamlit title
st.title("Health Data in Lebanon with Geocoded Areas")

# Load the dataset (CSV file from GitHub or your own file)
url = "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
df = pd.read_csv(url)

# Rename columns for ease of use (handling the space issues)
df.rename(columns={
    'Existence of chronic diseases - Diabetes ': 'Diabetes',
    'Existence of chronic diseases - Cardiovascular disease ': 'Cardiovascular Disease',
    'Existence of chronic diseases - Hypertension': 'Hypertension'
}, inplace=True)

# Check if a cached file with coordinates exists
cache_file = "cached_coordinates.csv"

if os.path.exists(cache_file):
    # Load cached coordinates if available
    coord_cache = pd.read_csv(cache_file)
    df = df.merge(coord_cache, on='refArea', how='left')
else:
    # Initialize geolocator
    geolocator = Nominatim(user_agent="lebanon_map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # Function to get coordinates using geopy
    def get_coordinates(area_name):
        try:
            location = geocode(area_name + ', Lebanon')
            if location:
                return location.latitude, location.longitude
            else:
                return None, None
        except:
            return None, None

    # Apply geocoding to get coordinates
    df['Latitude'], df['Longitude'] = zip(*df['refArea'].apply(get_coordinates))

    # Drop rows where coordinates couldn't be fetched
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Cache the coordinates to a file for future use
    coord_cache = df[['refArea', 'Latitude', 'Longitude']]
    coord_cache.to_csv(cache_file, index=False)

# Sidebar for area selection
areas = df['refArea'].unique()
selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

# Filter the data based on selected areas
filtered_data = df[df['refArea'].isin(selected_areas)]

# Define color based on the presence of Diabetes
filtered_data['Color'] = filtered_data['Diabetes'].apply(lambda x: 'green' if x.strip().lower() == 'no' else 'red')

# Plot the map using Plotly
fig = px.scatter_mapbox(
    filtered_data,
    lat='Latitude',
    lon='Longitude',
    color='Color',
    size='Nb of Covid-19 cases',
    hover_name='refArea',
    hover_data={'Nb of Covid-19 cases': True, 'Diabetes': True},
    zoom=8,
    mapbox_style='open-street-map',
    title="COVID-19 Cases in Lebanon"
)

# Display the map in Streamlit
st.plotly_chart(fig)































    





