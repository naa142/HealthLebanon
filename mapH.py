import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim

# Set title for the app
st.title("Health Data in Lebanon")

# Load the dataset
data_load_state = st.text('Loading data...')
url = "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
df = pd.read_csv(url)
data_load_state.text("Data loaded!")

# Option to show the dataset
if st.checkbox('Show data'):
    st.write("Dataset Overview:")
    st.dataframe(df)

# Rename columns for ease of use
df.rename(columns={
    'Existence of chronic diseases - Diabetes ': 'Diabetes',
    'Existence of chronic diseases - Cardiovascular disease ': 'Cardiovascular Disease',
    'Existence of chronic diseases - Hypertension': 'Hypertension'
}, inplace=True)

# Initialize geolocator
geolocator = Nominatim(user_agent="geoapiExercises", timeout=10)

# Function to get coordinates
def get_coordinates(location):
    try:
        loc = geolocator.geocode(location)
        if loc:
            return loc.latitude, loc.longitude
        else:
            return None, None
    except Exception as e:
        st.error(f"Error geocoding {location}: {e}")
        return None, None

# Get unique governorates and initialize coordinates
governorates = df['refArea'].unique()
coords = []

# Geocode each governorate with a progress bar
geocode_progress = st.progress(0)
for i, governorate in enumerate(governorates):
    lat, lon = get_coordinates(governorate)
    coords.append({'Governorate': governorate, 'Latitude': lat, 'Longitude': lon})
    geocode_progress.progress((i + 1) / len(governorates))

# Create a DataFrame for coordinates
coords_df = pd.DataFrame(coords)

# Merge with original data
df = df.merge(coords_df, left_on='refArea', right_on='Governorate', how='left')

# Handle missing coordinates by setting them to default (Lebanon's central latitude/longitude)
df['Latitude'] = df['Latitude'].fillna(33.8938)  # Default to Lebanon's latitude
df['Longitude'] = df['Longitude'].fillna(35.5018)  # Default to Lebanon's longitude

# Sidebar: Select Areas
areas = df['refArea'].unique()
selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

# Filter the dataset based on selected areas
filtered_data = df[df['refArea'].isin(selected_areas)]

# Create a scatter mapbox plot
fig = px.scatter_mapbox(
    filtered_data,
    lat='Latitude',
    lon='Longitude',
    color='Diabetes',  # Color points based on diabetes status (Yes/No)
    size='Nb of Covid-19 cases',  # Size points based on the number of COVID-19 cases
    hover_name='refArea',  # Show additional data on hover
    hover_data={
        'Nb of Covid-19 cases': True,
        'Diabetes': True,
        'Cardiovascular Disease': True,
        'Hypertension': True
    },
    title="COVID-19 Cases by District and Diabetes Status",
    mapbox_style="carto-positron",  # Mapbox style
    zoom=6,  # Adjust zoom level
    center={"lat": 33.8938, "lon": 35.5018}  # Center on Lebanon
)

# Add Mapbox access token (replace with your token)
fig.update_layout(mapbox_accesstoken='your_mapbox_access_token')

# Display the map in Streamlit
st.plotly_chart(fig)

# Additional metric: Display total number of cases for selected areas
total_cases_selected = filtered_data['Nb of Covid-19 cases'].sum()
st.write(f"Total COVID-19 cases in selected areas: **{total_cases_selected:.2f}**")













    





