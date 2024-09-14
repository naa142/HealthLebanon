import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim

# Set title for the app
st.title("Health Data in Lebanon")

# Load and display the dataset
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
geolocator = Nominatim(user_agent="geoapiExercises")

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

# Get unique governorates
governorates = df['refArea'].unique()
coords = []

# Geocode each governorate
for governorate in governorates:
    lat, lon = get_coordinates(governorate)
    coords.append({'Governorate': governorate, 'Latitude': lat, 'Longitude': lon})

# Create a DataFrame for coordinates
coords_df = pd.DataFrame(coords)

# Merge with original data
df = df.merge(coords_df, left_on='refArea', right_on='Governorate', how='left')

# Ensure missing coordinates are set to (0, 0) or a default lat/lon
df['Latitude'] = df['Latitude'].fillna(0)
df['Longitude'] = df['Longitude'].fillna(0)

# Check if any rows are missing coordinates and print them for debugging
missing_coords = df[df['Latitude'] == 0]
if not missing_coords.empty:
    st.warning("Some districts are missing coordinates and are set to (0, 0):")
    st.write(missing_coords[['refArea', 'Latitude', 'Longitude']])

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
    color='Diabetes',  # Color points based on diabetes status
    size='Nb of Covid-19 cases',  # Size points based on the number of COVID-19 cases
    hover_name='refArea',  # Show additional data on hover
    title="COVID-19 Cases by Governorate",
    mapbox_style="carto-positron",  # Mapbox style
    zoom=6,  # Adjust zoom level
    center={"lat": 33.8938, "lon": 35.5018}  # Center map on Lebanon
)

# Update layout for better readability
fig.update_layout(
    title_font_size=20,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=0, r=0, t=50, b=0)  # Adjust margins if needed
)

# Add Mapbox access token (replace 'your_mapbox_access_token' with your actual token)
fig.update_layout(mapbox_accesstoken='your_mapbox_access_token')

# Display the map in Streamlit
st.plotly_chart(fig)

# Additional analysis or metrics
total_cases_selected = filtered_data['Nb of Covid-19 cases'].sum()
st.write(f"Total COVID-19 cases in selected areas: **{total_cases_selected:.2f}**")











    





