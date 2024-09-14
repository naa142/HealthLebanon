import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
import folium
from io import BytesIO
import base64
import streamlit.components.v1 as components

# Function to get coordinates from area name
def get_coordinates(area_name):
    try:
        location = geolocator.geocode(area_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        st.error(f"Error fetching coordinates for {area_name}: {e}")
        return None, None

# Initialize geocoder
geolocator = Nominatim(user_agent="geoapiExercises")

# Set title for the app
st.title("Health Data in Lebanon")

# Load and display the dataset
data_load_state = st.text('Loading data...')
data = pd.read_csv(r"C:\Users\Nour Abd El Ghani\Downloads\4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv")

# Option to show the dataset
if st.checkbox('Show data'):
    st.write("Dataset Overview:")
    st.dataframe(data)

# Check column names
st.write("Column names in the dataset:")
st.write(data.columns)

# Subheader for COVID-19 cases by area
st.subheader("COVID-19 Cases by Area")

# Check if required columns exist in the dataset
if 'refArea' in data.columns and 'Nb of Covid-19 cases' in data.columns and 'Existence of chronic diseases - Cardiovascular disease ' in data.columns:
    
    # Sidebar: Select Areas
    areas = data['refArea'].unique()
    selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

    # Sidebar: Toggle percentage display on pie chart
    show_percentage = st.sidebar.checkbox("Show percentage on pie chart", value=False)

    # Filter the dataset based on selected areas
    filtered_data = data[data['refArea'].isin(selected_areas)]
    
    # Aggregate the data by summing up COVID-19 cases per area
    agg_data = filtered_data.groupby('refArea').agg({'Nb of Covid-19 cases': 'sum', 'Existence of chronic diseases - Cardiovascular disease ': 'first'}).reset_index()

    # Calculate the total cases
    total_cases = agg_data['Nb of Covid-19 cases'].sum()

    # Create a map
    map_center = [33.8547, 35.8623]  # Central coordinates for Lebanon
    map_zoom = 8
    covid_map = folium.Map(location=map_center, zoom_start=map_zoom)

    # Add circles to the map
    for _, row in agg_data.iterrows():
        lat, lon = get_coordinates(row['refArea'])
        if lat and lon:
            color = 'red' if row['Existence of chronic diseases - Cardiovascular disease '] == 'Yes' else 'green'
            folium.CircleMarker(
                location=[lat, lon],
                radius=row['Nb of Covid-19 cases'] / 1000,  # Adjust size factor as needed
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                popup=f"{row['refArea']}: {row['Nb of Covid-19 cases']} cases"
            ).add_to(covid_map)

    # Save map to HTML
    map_html = 'map.html'
    covid_map.save(map_html)

    # Read HTML file and encode as base64
    with open(map_html, 'r', encoding='utf-8') as f:
        map_html_content = f.read()
    
    map_base64 = base64.b64encode(map_html_content.encode()).decode()

    # Embed the map in Streamlit
    components.html(f'<iframe src="data:text/html;base64,{map_base64}" width="100%" height="600"></iframe>', height=600)
    
    # Bar Chart: COVID-19 Cases by Area
    fig_bar = px.bar(agg_data, x='refArea', y='Nb of Covid-19 cases',
                     title="COVID-19 Cases by Area",
                     labels={'refArea': 'Area', 'Nb of Covid-19 cases': 'Number of Cases'},
                     template='plotly_dark')

    # Add hover info and annotations to the bar chart
    fig_bar.update_traces(texttemplate='%{y}', textposition='outside', hoverinfo='x+y')
    fig_bar.update_layout(transition_duration=500)

    # Pie Chart: Distribution of Cases by Area (without names on the chart)
    fig_pie = px.pie(agg_data, values='Nb of Covid-19 cases', names='refArea',
                     title="COVID-19 Case Distribution by Area",
                     template='plotly_dark',
                     color_discrete_sequence=px.colors.qualitative.Set1)

    # Handle percentage display based on checkbox
    if show_percentage:
        # Show percentage on hover
        agg_data['Percentage'] = (agg_data['Nb of Covid-19 cases'] / total_cases) * 100
        hover_text = agg_data.apply(
            lambda row: f"{row['refArea']}: {row['Nb of Covid-19 cases']} cases ({row['Percentage']:.2f}%)", axis=1
        )
        fig_pie.update_traces(hovertext=hover_text, textinfo='percent')
    else:
        # Only display number of cases on hover (no percentage)
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

    # Additional Metric: Display total number of cases for selected areas
    total_cases_selected = agg_data['Nb of Covid-19 cases'].sum()
    st.write(f"Total cases in selected areas: **{total_cases_selected:.2f}**")

else:
    st.error("Columns 'refArea', 'Nb of Covid-19 cases', or 'Existence of chronic diseases - Cardiovascular disease ' not found in the dataset.")

# Treemap: COVID-19 Cases by Town in each Area and Diabetes Status
if 'Town' in data.columns and 'Existence of chronic diseases - Diabetes ' in data.columns:  # Note the space after 'Diabetes'
    
    # Filter data for treemap and remove rows where 'Nb of Covid-19 cases' is 0 or missing
    treemap_data = filtered_data[filtered_data['Nb of Covid-19 cases'] > 0].copy()

    # Check if there are still rows left after filtering
    if not treemap_data.empty:
        # Group and aggregate the data
        treemap_data = treemap_data.groupby(['refArea', 'Town', 'Existence of chronic diseases - Diabetes ']).agg({'Nb of Covid-19 cases': 'sum'}).reset_index()

        # Create Treemap
        fig_treemap = px.treemap(
            treemap_data,
            path=['refArea', 'Town', 'Existence of chronic diseases - Diabetes '],
            values='Nb of Covid-19 cases',
            color='Existence of chronic diseases - Diabetes ',
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

    # Additional Metric: Display total number of cases for selected areas
    total_cases_selected = agg_data['Nb of Covid-19 cases'].sum()
    st.write(f"Total cases in selected areas: **{total_cases_selected:.2f}**")



    





