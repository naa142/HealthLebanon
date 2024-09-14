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
    'Existence of chronic diseases - Cardiovascular Disease ': 'Cardiovascular Disease',
    'Existence of chronic diseases - Hypertension': 'Hypertension'
}, inplace=True)

# Initialize geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

# Function to get coordinates
def get_coordinates(location):
    try:
        loc = geolocator.geocode(location, timeout=10)  # Increase timeout if needed
        if loc:
            return loc.latitude, loc.longitude
        else:
            return None, None
    except Exception as e:
        st.error(f"Error geocoding {location}: {e}")
        return None, None

# Get unique districts
districts = df['refArea'].unique()
coords = []

# Geocode each district
for district in districts:
    lat, lon = get_coordinates(district)
    if lat is None or lon is None:
        lat, lon = 33.8938, 35.5018  # Default to Lebanon center if geocoding fails
    coords.append({'District': district, 'Latitude': lat, 'Longitude': lon})

# Create a DataFrame for coordinates
coords_df = pd.DataFrame(coords)

# Merge with original data
df = df.merge(coords_df, left_on='refArea', right_on='District', how='left')

# Filter out rows with missing coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

# Debugging: Check if any latitude or longitude is still missing
st.write("Checking for missing Latitude/Longitude after merge:")
st.write(df[df[['Latitude', 'Longitude']].isnull().any(axis=1)])

# Ensure latitude and longitude are available
if df[['Latitude', 'Longitude']].isnull().any(axis=1).sum() == 0:
    # Sidebar: Select Areas
    areas = df['refArea'].unique()
    selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

    # Sidebar: Toggle percentage display on pie chart
    show_percentage = st.sidebar.checkbox("Show percentage on pie chart", value=False)

    # Filter the dataset based on selected areas
    filtered_data = df[df['refArea'].isin(selected_areas)]

    # Add Mapbox access token
    mapbox_access_token = "c06c01b0cf09497b9cd9eb1ce74372c0"  # Replace this with your Mapbox token

    # Create a scatter mapbox plot
    fig_map = px.scatter_mapbox(
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
        zoom=8,  # Adjust zoom level for Lebanon
        center={"lat": 33.8938, "lon": 35.5018}  # Center on Lebanon
    )

    # Update the layout with your Mapbox access token
    fig_map.update_layout(mapbox_accesstoken=mapbox_access_token)

    # Display the map in Streamlit
    st.plotly_chart(fig_map)
else:
    st.error("Latitude or Longitude data is missing, unable to generate the map.")






















    





