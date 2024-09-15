import streamlit as st
import pandas as pd
import plotly.express as px

# Set title for the app
st.title("Health Data in Lebanon")

# Load and display the dataset
data_load_state = st.text('Loading data...')
url = "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
df = pd.read_csv(url)

# Option to show the dataset
if st.checkbox('Show data'):
    st.write("Dataset Overview:")
    st.dataframe(df)

# Check column names
st.write("Column names in the dataset:")
st.write(df.columns)

# Subheader for COVID-19 cases by area
st.subheader("COVID-19 Cases by Area")

# Check if required columns exist in the dataset
if 'refArea' in df.columns and 'Nb of Covid-19 cases' in df.columns and 'Existence of chronic diseases - Cardiovascular disease ' in df.columns:
    
    # Sidebar: Select Areas
    areas = df['refArea'].unique()
    selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

    # Sidebar: Toggle percentage display on pie chart
    show_percentage = st.sidebar.checkbox("Show percentage on pie chart", value=False)
    
    # Sidebar: Map settings
    st.sidebar.header("Map Settings")
    map_style = st.sidebar.selectbox("Select Map Style:", ["carto-positron", "open-street-map", "basic", "white-bg"])
    zoom_level = st.sidebar.slider("Zoom Level:", min_value=1, max_value=15, value=6)
    center_lat = st.sidebar.slider("Map Center Latitude:", min_value=-90.0, max_value=90.0, value=33.8938)
    center_lon = st.sidebar.slider("Map Center Longitude:", min_value=-180.0, max_value=180.0, value=35.5018)

    # Filter the dataset based on selected areas
    filtered_df = df[df['refArea'].isin(selected_areas)]
    
    # Aggregate the data by summing up COVID-19 cases per area
    agg_df = filtered_df.groupby('refArea').agg({
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

    # Print the lengths of the lists to verify
    st.write(f"Length of Governorate list: {len(coords_df['Governorate'])}")
    st.write(f"Length of Latitude list: {len(coords_df['Latitude'])}")
    st.write(f"Length of Longitude list: {len(coords_df['Longitude'])}")

    # Check the contents of coords_df
    st.write("Coordinates DataFrame:")
    st.write(coords_df)

    # Merge with original data
    df = df.merge(coords_df, left_on='refArea', right_on='Governorate', how='left')

    # Check for missing values
    missing_latitude = df['Latitude'].isna().sum()
    missing_longitude = df['Longitude'].isna().sum()
    st.write(f"Missing Latitude values: {missing_latitude}")
    st.write(f"Missing Longitude values: {missing_longitude}")

    # Drop rows with missing coordinates (if any)
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Verify the merged DataFrame
    st.write("Merged DataFrame head:")
    st.write(df.head())

    # Checkbox for displaying Map
    show_map = st.checkbox("Show Map", value=True)

    if show_map:
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

    # Checkbox for displaying Bar Chart
    show_bar_chart = st.checkbox("Show Bar Chart", value=True)

    if show_bar_chart:
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

    # Checkbox for displaying Pie Chart
    show_pie_chart = st.checkbox("Show Pie Chart", value=True)

    if show_pie_chart:
        # Pie Chart: Distribution of Cases by Area (without names on the chart)
        fig_pie = px.pie(agg_df, values='Nb of Covid-19 cases', names='refArea',
                         title="COVID-19 Case Distribution by Area",
                         template='plotly_dark',
                         color_discrete_sequence=px.colors.qualitative.Set1)

        # Handle percentage display based on checkbox
        total_cases = agg_df['Nb of Covid-19 cases'].sum()
        if show_percentage:
            hover_text = agg_df.apply(
                lambda row: f"{row['refArea']}: {row['Nb of Covid-19 cases']} cases ({row['Nb of Covid-19 cases']/total_cases*100:.2f}%)", axis=1
            )
            fig_pie.update_traces(hovertext=hover_text, textinfo='percent')
        else:
            hover_text = agg_df.apply(
                lambda row: f"{row['refArea']}: {row['Nb of Covid-19 cases']} cases", axis=1
            )
            fig_pie.update_traces(hovertext=hover_text, textinfo='none')

        fig_pie.update_traces(pull=[0.1 if area in selected_areas else 0 for area in agg_df['refArea']])
        st.plotly_chart(fig_pie)

    # Checkbox for displaying Tree Map
    show_tree_map = st.checkbox("Show Tree Map", value=True)

    if show_tree_map:
        # Tree Map: Distribution of COVID-19 Cases with Towns
        try:
            fig_tree = px.treemap(agg_df, path=['refArea', 'Town'], values='Nb of Covid-19 cases',
                                  color='Existence of chronic diseases - Cardiovascular disease ',
                                  color_discrete_map={
                                      'Yes': 'red',
                                      'No': 'blue'
                                  },
                                  title="COVID-19 Cases Distribution by Area and Town",
                                  template='plotly_dark')

            fig_tree.update_layout(
                title_font_size=20,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            st.plotly_chart(fig_tree)
        except ValueError as e:
            st.error(f"Error creating Tree Map: {e}")

    # Additional Metric: Display total number of cases for selected areas
    total_cases_selected = agg_df['Nb of Covid-19 cases'].sum()
    st.write(f"Total cases in selected areas: **{total_cases_selected:.2f}**")

else:
    st.error("Columns 'refArea', 'Nb of Covid-19 cases', or 'Existence of chronic diseases - Cardiovascular disease ' not found in the dataset.")


















































    





