
import streamlit as st
import pandas as pd
import plotly.express as px

# Set title for the app
st.title("Health Data in Lebanon")

# Load and display the dataset
data_load_state = st.text('By Nour Abdelghani')
url =  "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
df = pd.read_csv(url)

# Option to show the dataset
if st.checkbox('Show data', key='show_data'):
    st.write("Dataset Overview:")
    st.dataframe(df)


# Sidebar for selecting visualization
st.sidebar.header("Select Visualization")
visualization_type = st.sidebar.selectbox(
    "Choose a visualization:",
    ["Map", "Bar Chart", "Pie Chart", "Treemap"],
    key='visualization_type'
)

# Conditional display of map settings based on selected visualization type
if visualization_type == "Map":
    st.sidebar.header("Map Settings")
    map_style = st.sidebar.selectbox("Select Map Style:", ["carto-positron", "open-street-map", "basic", "white-bg"], key='map_style')
    zoom_level = st.sidebar.slider("Zoom Level:", min_value=1, max_value=15, value=6, key='zoom_level')
    center_lat = st.sidebar.slider("Map Center Latitude:", min_value=-90.0, max_value=90.0, value=33.8938, key='center_lat')
    center_lon = st.sidebar.slider("Map Center Longitude:", min_value=-180.0, max_value=180.0, value=35.5018, key='center_lon')

# Subheader for COVID-19 cases by area
st.subheader("COVID-19 Cases by Area")

# Check if required columns exist in the dataset
if 'refArea' in df.columns and 'Nb of Covid-19 cases' in df.columns and 'Existence of chronic diseases - Cardiovascular disease ' in df.columns and 'Town' in df.columns:
    
    # Sidebar: Select Areas
    areas = df['refArea'].unique()
    selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas, key='selected_areas')

    # Sidebar: Toggle percentage display on pie chart (appears only when Pie Chart is selected)
    if visualization_type == "Pie Chart":
        show_percentage = st.sidebar.checkbox("Show percentage on pie chart", value=False, key='show_percentage')
    else:
        show_percentage = False

    # Filter the dataset based on selected areas
    filtered_df = df[df['refArea'].isin(selected_areas)]
    
    # Handle missing or zero values
    filtered_df = filtered_df[filtered_df['Nb of Covid-19 cases'] > 0].dropna(subset=['Nb of Covid-19 cases'])
    
    # Aggregate the data by summing up COVID-19 cases per area
    agg_df = filtered_df.groupby(['refArea']).agg({
        'Nb of Covid-19 cases': 'sum', 
        'Existence of chronic diseases - Cardiovascular disease ': 'first'
    }).reset_index()

    # Manually add latitude and longitude information
    coords_data = {
        'Governorate': [
            'Mount_Lebanon_Governorate', 'South_Governorate', 'Akkar_Governorate', 
            'North_Governorate', 'Baabda_District', 'Byblos_District', 'Nabatieh_Governorate', 
            'Tyre_District', 'Bsharri_District', 'Sidon_District', 'Batroun_District', 
            'Zgharta_District', 'Keserwan_District', 'Marjeyoun_District', 'Aley_District', 
            'Beqaa_Governorate', 'Matn_District', 'Miniyeh-Danniyeh_District', 'Bint_Jbeil_District', 
            'Hasbaya_District', 'Zahle_District', 'Western_Beqaa_District'
        ],
        'Latitude': [
            33.737305, 33.340319, 34.555501, 34.331770, 33.844179, 34.123695, 33.283620,
            33.213081, 34.238451, 33.454454, 34.247192, 34.360090, 34.012735, 33.364070,
            33.772089, 33.674620, 33.909724, 34.388802, 33.183254, 33.376925, 33.806659,
            33.600089
        ],
        'Longitude': [
            35.599890, 35.303844, 36.201645, 35.943696, 35.703280, 35.649356, 35.489779,
            35.288796, 35.986991, 35.338568, 35.725521, 35.898134, 35.787238, 35.587142,
            35.633047, 35.833376, 35.716795, 36.052057, 35.413805, 35.717419, 35.912587,
            35.748880
        ]
    }

    # Convert coords_data to a DataFrame and remove duplicates
    coords_df = pd.DataFrame(coords_data).drop_duplicates()

    # Merge with original data
    df = df.merge(coords_df, left_on='refArea', right_on='Governorate', how='left')

    # Check for missing values
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Create visualizations based on selected type
    if visualization_type == "Map":
        # Create a scatter mapbox plot
        fig = px.scatter_mapbox(
            df,
            lat='Latitude',
            lon='Longitude',
            size='Nb of Covid-19 cases',  # Size points based on number of cases
            color='Existence of chronic diseases - Cardiovascular disease ',  # Color points based on cardiovascular disease status
            color_discrete_map={
                'Yes': 'red',
                'No': 'blue'
            },
            hover_name='refArea',  # Show additional data on hover
            title="COVID-19 Cases by Area",
            mapbox_style=map_style,  # Mapbox style from sidebar
            zoom=zoom_level,  # Zoom level from sidebar
            center={"lat": center_lat, "lon": center_lon}  # Center on location from sidebar
        )

        # Update layout for better readability
        fig.update_layout(
            title_font_size=20,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=0, r=0, t=50, b=0)  # Adjust margins if needed
        )

        # Add Mapbox access token
        fig.update_layout(mapbox_accesstoken='pk.eyJ1IjoibmFhMTQyIiwiYSI6ImNtMG93ZGxqYTBjbTMycXIzanZmNGh5ZjYifQ.Brd1QyD5TYB9DuvtCTwxCw')

        # Display the map in Streamlit
        st.plotly_chart(fig)

    elif visualization_type == "Bar Chart":
        # Bar Chart: COVID-19 Cases by Area
        fig_bar = px.bar(agg_df, x='refArea', y='Nb of Covid-19 cases',
                         title="COVID-19 Cases by Area",
                         labels={'refArea': 'Area', 'Nb of Covid-19 cases': 'Number of Cases'},
                         template='plotly_dark')

        # Add hover info and annotations to the bar chart
        fig_bar.update_traces(texttemplate='%{y}', textposition='outside', hoverinfo='x+y')
        fig_bar.update_layout(transition_duration=500)

        # Display the Bar Chart
        st.plotly_chart(fig_bar)

    elif visualization_type == "Pie Chart":
        # Pie Chart: Distribution of COVID-19 Cases by Area
        fig_pie = px.pie(agg_df, names='refArea', values='Nb of Covid-19 cases',
                         title="Distribution of COVID-19 Cases by Area",
                         template='plotly_dark')

        total_cases = agg_df['Nb of Covid-19 cases'].sum()
        if show_percentage:
            fig_pie.update_traces(textinfo='percent', hoverinfo='label+percent')
        else:
            fig_pie.update_traces(textinfo='label', hoverinfo='label')

        # Update layout for readability
        fig_pie.update_layout(transition_duration=500)

        # Display the Pie Chart
        st.plotly_chart(fig_pie)

    elif visualization_type == "Treemap":
        # Treemap: COVID-19 Cases by Area and Town
        fig_treemap = px.treemap(
            filtered_df,  # Use the filtered dataframe based on selected areas
            path=['refArea', 'Town'],  # Include both governorate and town in the hierarchy
            values='Nb of Covid-19 cases',  # Number of cases as the value
            title="COVID-19 Cases by Area and Town",
            template='plotly_dark',
            color='Existence of chronic diseases - Cardiovascular disease ',  # Color based on cardiovascular disease status
            color_discrete_map={
                'Yes': 'red',
                'No': 'blue'
            },
            hover_data={'refArea': True, 'Town': True, 'Nb of Covid-19 cases': True}  # Hover info
        )

        # Update layout for readability
        fig_treemap.update_layout(transition_duration=500)

        # Display the Treemap
        st.plotly_chart(fig_treemap)

else:
    st.error("Required columns are missing from the dataset.")





















































    





