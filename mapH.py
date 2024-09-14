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

# Check if latitude and longitude are properly set
if df[['Latitude', 'Longitude']].isnull().any().sum() == 0:
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
    try:
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
    except ValueError as e:
        st.error(f"ValueError: {e}")
else:
    st.error("Latitude or Longitude data is missing, unable to generate the map.")

# Aggregate data for bar and pie charts
agg_data = filtered_data.groupby('refArea').agg({
    'Nb of Covid-19 cases': 'sum',
    'Diabetes': 'first'
}).reset_index()

# Bar Chart: COVID-19 Cases by Area
fig_bar = px.bar(
    agg_data,
    x='refArea',
    y='Nb of Covid-19 cases',
    title="COVID-19 Cases by Area",
    labels={'refArea': 'Area', 'Nb of Covid-19 cases': 'Number of Cases'},
    template='plotly_dark'
)
fig_bar.update_traces(texttemplate='%{y}', textposition='outside', hoverinfo='x+y')
fig_bar.update_layout(transition_duration=500)

# Pie Chart: Distribution of Cases by Area
fig_pie = px.pie(
    agg_data,
    values='Nb of Covid-19 cases',
    names='refArea',
    title="COVID-19 Case Distribution by Area",
    template='plotly_dark',
    color_discrete_sequence=px.colors.qualitative.Set1
)

# Handle percentage display based on checkbox
if show_percentage:
    total_cases = agg_data['Nb of Covid-19 cases'].sum()
    agg_data['Percentage'] = (agg_data['Nb of Covid-19 cases'] / total_cases) * 100
    hover_text = agg_data.apply(
        lambda row: f"{row['refArea']}: {row['Nb of Covid-19 cases']} cases ({row['Percentage']:.2f}%)", axis=1
    )
    fig_pie.update_traces(hovertext=hover_text, textinfo='percent')
else:
    hover_text = agg_data.apply(
        lambda row: f"{row['refArea']}: {row['Nb of Covid-19 cases']} cases", axis=1
    )
    fig_pie.update_traces(hovertext=hover_text, textinfo='none')

# Optional: Explode sections of the pie chart for selected areas
fig_pie.update_traces(pull=[0.1 if area in selected_areas else 0 for area in agg_data['refArea']])

# Display the Bar Chart
st.plotly_chart(fig_bar)

# Display the Pie Chart
st.plotly_chart(fig_pie)

# Treemap: COVID-19 Cases by Town in each Area and Diabetes Status
if 'Town' in df.columns and 'Diabetes' in df.columns:
    
    # Filter data for treemap and remove rows where 'Nb of Covid-19 cases' is 0 or missing
    treemap_data = filtered_data[filtered_data['Nb of Covid-19 cases'] > 0].copy()
    
    # Check if there are still rows left after filtering
    if not treemap_data.empty:
        # Group and aggregate the data
        treemap_data = treemap_data.groupby(['refArea', 'Town', 'Diabetes']).agg({'Nb of Covid-19 cases': 'sum'}).reset_index()

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
        fig_treemap.update_traces(root_color='white')
        st.plotly_chart(fig_treemap)
    else:
        st.warning("No COVID-19 cases available for the selected areas.")
    
# Additional Metric: Display total number of cases for selected areas
total_cases_selected = filtered_data['Nb of Covid-19 cases'].sum()
st.write(f"Total COVID-19 cases in selected areas: **{total_cases_selected:.2f}**")























    





