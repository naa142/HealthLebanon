import pandas as pd
import folium
import streamlit as st

# Load the main dataset
st.title("Health Data in Lebanon")
data_load_state = st.text('Loading data...')
url = "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
df = pd.read_csv(url)
data_load_state.text("Data loaded!")

# Load local coordinates dataset
coords_file = 'lebanon_districts_coordinates.csv'  # Update with your local file name
coords_df = pd.read_csv(coords_file)

# Rename columns for ease of use
df.rename(columns={
    'Existence of chronic diseases - Diabetes ': 'Diabetes',
    'Existence of chronic diseases - Cardiovascular disease ': 'Cardiovascular Disease',
    'Existence of chronic diseases - Hypertension': 'Hypertension'
}, inplace=True)

# Merge coordinates with the main dataset
df = df.merge(coords_df, left_on='refArea', right_on='District', how='left')

# Filter out rows with missing coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

# Sidebar: Select Areas
areas = df['refArea'].unique()
selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

# Filter the dataset based on selected areas
filtered_data = df[df['refArea'].isin(selected_areas)]

# Create a Folium map
map_center = [33.8938, 35.5018]  # Center of Lebanon
map_zoom = 8
m = folium.Map(location=map_center, zoom_start=map_zoom)

# Add markers to the map
for _, row in filtered_data.iterrows():
    color = 'green' if row['Diabetes'].strip().lower() == 'no' else 'red'
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=row['Nb of Covid-19 cases'] / 100,  # Adjust size as needed
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=f"{row['refArea']}: {row['Nb of Covid-19 cases']} cases\nDiabetes: {row['Diabetes']}"
    ).add_to(m)

# Display the map in Streamlit
st.write("### COVID-19 Cases Map")
st.components.v1.html(m._repr_html_(), height=600)





























    





