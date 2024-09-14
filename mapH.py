import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim

# Set title for the app
st.title("Health Data in Lebanon")

# Load and display the dataset
data_load_state = st.text('Loading data...')
url = "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
data = pd.read_csv(url)

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
            location = geolocator.geocode(location)
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

    # Merge with original data
    df = df.merge(coords_df, left_on='refArea', right_on='Governorate', how='left')

    # Check if coordinates were added
    st.write(df.head())

    # Create a scatter mapbox plot
    fig = px.scatter_mapbox(
        df,
        lat='Latitude',
        lon='Longitude',
        color='Diabetes',  # Optional: Color points based on another variable
        size='Nb of Covid-19 cases',  # Optional: Size points based on another variable
        hover_name='refArea',  # Show additional data on hover
        title="COVID-19 Cases by Governorate",
        mapbox_style="carto-positron",  # Mapbox style; can be customized
        zoom=6,  # Adjust zoom level
        center={"lat": 33.8938, "lon": 35.5018}  # Center on a specific location
    )

    # Update layout for better readability
    fig.update_layout(
        title_font_size=20,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=0, r=0, t=50, b=0)  # Adjust margins if needed
    )

    # Add Mapbox access token
    fig.update_layout(mapbox_accesstoken='your_mapbox_access_token')

    # Display the map in Streamlit
    st.plotly_chart(fig)

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
    st.error("Columns '




    





