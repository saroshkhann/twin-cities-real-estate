import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Twin Cities Real Estate Map",
    page_icon="📍",
    layout="wide"
)

# Load data safely using pathlib
@st.cache_data
def load_data():
    data_path = Path(__file__).parent / 'data' / 'processed' / 'sector_price_summary.csv'
    if not data_path.exists():
        data_path = Path('sector_price_summary.csv')
    return pd.read_csv(data_path)

df = load_data()

st.title("🏡 Islamabad & Rawalpindi Sector Price Heatmap")
st.markdown("Explore residential plot pricing averages across sectors and housing societies.")

# Sidebar Controls
st.sidebar.header("Filter & Navigation")

city_filter = st.sidebar.multiselect(
    "Select City",
    options=sorted(df['city'].unique()),
    default=sorted(df['city'].unique())
)

min_listings = st.sidebar.slider(
    "Minimum Listings in Sector",
    min_value=1,
    max_value=int(df['listing_count'].max()),
    value=1
)

# Apply filters
filtered_df = df[
    (df['city'].isin(city_filter)) &
    (df['listing_count'] >= min_listings)
].copy().reset_index(drop=True)

# Sector Focus Selectbox
sector_options = ["Overview (All Sectors)"] + sorted(filtered_df['sector'].unique().tolist())
selected_sector = st.sidebar.selectbox("Jump to Sector:", sector_options)

# Dynamically set center and zoom level based on selection
if selected_sector != "Overview (All Sectors)":
    target_row = filtered_df[filtered_df['sector'] == selected_sector].iloc[0]
    map_center = {"lat": float(target_row['latitude']), "lon": float(target_row['longitude'])}
    map_zoom = 13.5  # Zoom in closely to the sector
else:
    map_center = {"lat": 33.6400, "lon": 73.0600}  # Twin cities regional center
    map_zoom = 10.2

# KPI Header Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Sectors Displayed", len(filtered_df))
col2.metric("Overall Avg Price", f"₨ {filtered_df['avg_price'].mean():.2f} Cr" if not filtered_df.empty else "N/A")

if selected_sector != "Overview (All Sectors)":
    col3.metric(f"Avg Price ({selected_sector})", f"₨ {target_row['avg_price']:.2f} Cr")
    col4.metric("Avg Price / Marla", f"₨ {target_row['avg_price_per_marla']:.3f} Cr")
else:
    top_sector = filtered_df.sort_values(by='avg_price', ascending=False).iloc[0] if not filtered_df.empty else None
    col3.metric("Highest Sector", f"{top_sector['sector']} (₨ {top_sector['avg_price']} Cr)" if top_sector is not None else "N/A")
    col4.metric("Total Unique Sectors", len(df['sector'].unique()))

st.markdown("---")

# Plotly Map figure (compatible with Plotly 7+)
fig = px.scatter_map(
    filtered_df,
    lat="latitude",
    lon="longitude",
    size="listing_count",
    color="avg_price",
    color_continuous_scale="Viridis",
    size_max=22,
    zoom=map_zoom,
    center=map_center,
    map_style="carto-positron",
    hover_name="sector",
    hover_data={
        "city": True,
        "avg_price": ":.2f",
        "median_price": ":.2f",
        "avg_price_per_marla": ":.3f",
        "listing_count": True,
        "latitude": False,
        "longitude": False
    },
    labels={
        "avg_price": "Avg Price (Crore)",
        "avg_price_per_marla": "Avg/Marla (Crore)",
        "listing_count": "Listings Count"
    }
)

fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=640
)

st.plotly_chart(fig, use_container_width=True)

# Detailed data table
with st.expander("📊 View Detailed Sector Data"):
    st.dataframe(
        filtered_df.sort_values(by='avg_price', ascending=False),
        use_container_width=True
    )