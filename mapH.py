import streamlit as st
import pandas as pd
import plotly.express as px

# Set title for the app
st.title("Health Data in Lebanon")

# Load and display the dataset
data_load_state = st.text('Loading data...')
url = "https://raw.githubusercontent.com/naa142/HealthLebanon/main/4a0321bc971cc2f793d3367fd0b55a34_20240905_102823.csv"
df = pd.read_csv(url)

# Rename columns for ease of use
df.rename(columns={
    'Existence of chronic diseases - Diabetes ': 'Diabetes',
    'Existence of chronic diseases - Cardiovascular disease ': 'Cardiovascular Disease',
    'Existence of chronic diseases - Hypertension': 'Hypertension'
}, inplace=True)

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
if 'refArea' in df.columns and 'Nb of Covid-19 cases' in df.columns and 'Cardiovascular Disease' in df.columns:

    # Sidebar: Select Areas
    areas = df['refArea'].unique()
    selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

    # Sidebar: Toggle percentage display on pie chart
    show_percentage = st.sidebar.checkbox("Show percentage on pie chart", value=False)

    # Sidebar: Toggle map visibility
    show_map = st.sidebar.checkbox("Show Map", value=True)

    # Filter the dataset based on selected areas
    filtered_df = df[df['refArea'].isin(selected_areas)]

    # Aggregate the data by summing up COVID-19 cases per area
    agg_data = filtered_df.groupby('refArea').agg({'Nb of Covid-19 cases': 'sum', 'Cardiovascular Disease': 'first'}).reset_index()

    # Calculate the total cases
    total_cases = agg_data['Nb of Covid-19 cases'].sum()

    if show_map:
        # Predefined coordinates for areas
        coordinates_dict = {
            'Mount_Lebanon_Governorate': (33.8331, 35.5971),
            'Beirut': (33.8938, 35.5018),
            'North_Governorate': (34.4367, 35.8308),
            'Bekaa_Governorate': (33.8547, 36.0960),
            'South_Governorate': (33.3686, 35.2881),
            'Nabatiye_Governorate': (33.3789, 35.4835),
            'Akkar_Governorate': (34.5431, 36.0785),
            'Baalbek-Hermel_Governorate': (34.1991, 36.2606),
            'Tripoli_District,_Lebanon': (34.4331, 35.8442),
            'Hermel_District': (34.3956, 36.3855)
            # Add more areas and their coordinates as needed
        }

        # Function to get coordinates from predefined dictionary
        def get_coordinates(area):
            return coordinates_dict.get(area, (None, None))

        # Apply the coordinates to the DataFrame
        df['Latitude'], df['Longitude'] = zip(*df['refArea'].apply(get_coordinates))

        # Remove rows without coordinates
        df_map = df.dropna(subset=['Latitude', 'Longitude'])

        # Check if coordinates were added
        st.write(df_map[['refArea', 'Latitude', 'Longitude']].head())

        # Create a scatter mapbox plot
        fig = px.scatter_mapbox(
            df_map,
            lat='Latitude',
            lon='Longitude',
            color='Diabetes',  # Optional: Color points based on another variable
            size='Nb of Covid-19 cases',  # Optional: Size points based on another variable
            hover_name='refArea',  # Show additional data on hover
            title="COVID-19 Cases by Governorate",
            mapbox_style="carto-positron",  # Mapbox style; can be customized
            zoom=7,  # Adjust zoom level
            center={"lat": 33.8547, "lon": 35.8623}  # Center on Lebanon
        )

        # Update layout for better readability
        fig.update_layout(
            title_font_size=20,
            margin=dict(l=0, r=0, t=50, b=0)  # Adjust margins if needed
        )

        # Add Mapbox access token (optional)
        # If you have a Mapbox access token, uncomment the following line and add your token
        # fig.update_layout(mapbox_accesstoken='your_mapbox_access_token')

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

    # Pie Chart: Distribution of Cases by Area
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
    st.error("Columns 'refArea', 'Nb of Covid-19 cases', or 'Cardiovascular Disease' not found in the dataset.")

# Treemap: COVID-19 Cases by Town in each Area and Diabetes Status
if 'Town' in df.columns and 'Diabetes' in df.columns:

    # Filter data for treemap and remove rows where 'Nb of Covid-19 cases' is 0 or missing
    treemap_df = filtered_df[filtered_df['Nb of Covid-19 cases'] > 0].copy()

    # Check if there are still rows left after filtering
    if not treemap_df.empty:
        # Group and aggregate the data
        treemap_df = treemap_df.groupby(['refArea', 'Town', 'Diabetes']).agg({'Nb of Covid-19 cases': 'sum'}).reset_index()

        # Create Treemap
        fig_treemap = px.treemap(
            treemap_df,
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

    # Additional Metric: Display total number of cases for selected areas
    total_cases_selected = agg_data['Nb of Covid-19 cases'].sum()
    st.write(f"Total cases in selected areas: **{total_cases_selected:.2f}**")










    





