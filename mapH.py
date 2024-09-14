import pandas as pd
import plotly.express as px
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Streamlit title
st.title("Health Data in Lebanon with Geocoded Areas")

# Load your CSV file from GitHub
url = "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
df = pd.read_csv(url)

# Rename columns for ease of use
df.rename(columns={
    'Existence of chronic diseases - Diabetes ': 'Diabetes',
    'Existence of chronic diseases - Cardiovascular disease ': 'Cardiovascular Disease',
    'Existence of chronic diseases - Hypertension': 'Hypertension'
}, inplace=True)

# Function to get coordinates using geopy
def get_coordinates(area_name):
    geolocator = Nominatim(user_agent="lebanon_map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    location = geocode(area_name + ', Lebanon')
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Add Latitude and Longitude columns to your dataframe
if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
    df['Latitude'], df['Longitude'] = zip(*df['refArea'].apply(get_coordinates))

# Drop rows where coordinates could not be fetched
df = df.dropna(subset=['Latitude', 'Longitude'])

# Sidebar: Select Areas
areas = df['refArea'].unique()
selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

# Filter the dataset based on selected areas
filtered_data = df[df['refArea'].isin(selected_areas)]

# Define colors based on Diabetes presence
filtered_data['Color'] = filtered_data['Diabetes'].apply(lambda x: 'green' if x.strip().lower() == 'no' else 'red')

# Create a Plotly scatter mapbox
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

# Optionally, you can cache the coordinates to avoid calling the API repeatedly






























    





