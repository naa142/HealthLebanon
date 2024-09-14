import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim

# Set title for the app
st.title("Health Data in Lebanon")

# Load and display the dataset
url = "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
df = pd.read_csv(url)

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

# Predefined coordinates for some common areas
known_coords = {
    'Tripoli District, Lebanon': (34.433, 35.844),
    'Hermel District': (34.394, 36.384),
    'Mount Lebanon Governorate': (33.8547, 35.8623),
    # Add more known coordinates here...
}

# Initialize geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

# Function to get coordinates
def get_coordinates(location):
    # First check if location is in predefined coordinates
    if location in known_coords:
        return known_coords[location]
    
    # Otherwise, use the geocoding service with increased timeout
    try:
        location = geolocator.geocode(location, timeout=10)
        if location:
            return location.latitude, location.longitude
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

# Merge coordinates with the original data
df = df.merge(coords_df, left_on='refArea', right_on='Governorate', how='left')

# Display merged data for verification
st.write("Data with Coordinates:")
st.write(df.head())

# Create a scatter mapbox plot
fig = px.scatter_mapbox(
    df,
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

# Add Mapbox access token (replace with your own token)
fig.update_layout(mapbox_accesstoken='your_mapbox_access_token')

# Display the map in Streamlit
st.plotly_chart(fig)

# Sidebar: Select Areas for filtering
selected_areas = st.sidebar.multiselect("Select Areas:", df['refArea'].unique(), default=df['refArea'].unique())

# Filter data based on selected areas
filtered_data = df[df['refArea'].isin(selected_areas)]

# Bar chart: COVID-19 Cases by Area
fig_bar = px.bar(filtered_data, x='refArea', y='Nb of Covid-19 cases',
                 title="COVID-19 Cases by Area",
                 labels={'refArea': 'Area', 'Nb of Covid-19 cases': 'Number of Cases'},
                 template='plotly_dark')

# Update bar chart
fig_bar.update_traces(texttemplate='%{y}', textposition='outside', hoverinfo='x+y')
fig_bar.update_layout(transition_duration=500)

# Display the Bar Chart
st.plotly_chart(fig_bar)

# Treemap: COVID-19 Cases by Town and Diabetes Status
if 'Town' in df.columns and 'Diabetes' in df.columns:
    treemap_data = filtered_data[filtered_data['Nb of Covid-19 cases'] > 0].copy()
    
    if not treemap_data.empty:
        # Create Treemap
        fig_treemap = px.treemap(
            treemap_data,
            path=['refArea', 'Town', 'Diabetes'],
            values='Nb of Covid-19 cases',
            color='Diabetes',
            color_discrete_map={'Yes': 'red', 'No': 'green'},
            title="COVID-19 Cases by Town, Area, and Diabetes Status",
            template='plotly_dark'
        )

        # Set all districts to have a white background
        fig_treemap.update_traces(root_color='white')

        # Display the Treemap
        st.plotly_chart(fig_treemap)
    else:
        st.warning("No COVID-19 cases available for the selected areas.")

# Total number of cases for selected areas
total_cases_selected = filtered_data['Nb of Covid-19 cases'].sum()
st.write(f"Total cases in selected areas: **{total_cases_selected:.2f}**")

















    





