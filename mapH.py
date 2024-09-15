import streamlit as st
import pandas as pd
import plotly.express as px

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
    'Existence of chronic diseases - Cardiovascular disease ': 'Cardiovascular Disease',
    'Existence of chronic diseases - Hypertension': 'Hypertension'
}, inplace=True)

# Fallback coordinates for Lebanese districts (dictionary of known locations)
fallback_coords = {
    "Bsharri_District": (34.2500, 36.0100),
    "Sidon_District": (33.5631, 35.3683),
    "Batroun_District": (34.2553, 35.6589),
    "Zgharta_District": (34.4000, 35.9500),
    "Keserwan_District": (33.9800, 35.7100),
    "Marjeyoun_District": (33.3556, 35.5919),
    "Aley_District": (33.8100, 35.5800),
    "Beqaa_Governorate": (33.8547, 35.9058),
    "Matn_District": (33.8330, 35.5500),
    "Miniyeh–Danniyeh_District": (34.4829, 35.9256),
    "Bint_Jbeil_District": (33.1172, 35.4442),
    "Hasbaya_District": (33.3981, 35.6847),
    "Zahlé_District": (33.8495, 35.9042),
    "Western_Beqaa_District": (33.7000, 35.8000),
    "Baalbek-Hermel_Governorate": (34.0200, 36.2160),
    "Tripoli_District,_Lebanon": (34.4342, 35.8362),
    "Hermel_District": (34.3900, 36.3900)
}

# Create a function to return fallback coordinates
def get_fallback_coordinates(district):
    return fallback_coords.get(district, (33.8938, 35.5018))  # Default to Beirut if not found

# Apply fallback coordinates to the dataset
df['Latitude'], df['Longitude'] = zip(*df['refArea'].apply(get_fallback_coordinates))

# Sidebar: Select Areas
areas = df['refArea'].unique()
selected_areas = st.sidebar.multiselect("Select Areas:", areas, default=areas)

# Sidebar: Toggle percentage display on pie chart
show_percentage = st.sidebar.checkbox("Show percentage on pie chart", value=False)

# Filter the dataset based on selected areas
filtered_data = df[df['refArea'].isin(selected_areas)]

# Add Mapbox access token
mapbox_access_token = "pk.eyJ1IjoibmFhMTQyIiwiYSI6ImNtMHA4dWN1cTAzbDQya3FzZnNpM2c2ZzgifQ.fYMRblnLF2DytRffA1s51Q"

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
            'Existence of chronic diseases - Cardiovascular disease ': True,  # Correct column name
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

        # Display the treemap
        st.plotly_chart(fig_treemap)
    else:
        st.write("No data available for the Treemap.")

































    





