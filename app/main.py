import streamlit as st
import folium
from streamlit_folium import st_folium

from core.maplayers import add_custom_choropleth
from utils.map_utils import compute_map_view
from utils.data_loader import load_geojson, load_ct_values, download_from_gdrive

APP_VERSION = "v0.4.0.dev1"
st.set_page_config(page_title="InsightAtlas | Canadian Demographic Explorer", layout="wide")
st.sidebar.caption(f"Version: {APP_VERSION}")
st.subheader("Census Tracts 2021")

# --- Configuration ---
use_cloud_data = True
CLOUD_DATA_DIR = "data/cloud"
CLOUD_CSV_URL = "https://drive.google.com/uc?export=download&id=1ERHEMcBhyPcgYq2r5iwxEO9KIH45TAN7"
CLOUD_GEOJSON_URL = "https://drive.google.com/uc?export=download&id=1galoO4I9wobrq0lo-ojPCKg0B6ZHrlob"

# default city
default_metro = "Vancouver"

if use_cloud_data:
    GEOJSON_PATH = download_from_gdrive(CLOUD_GEOJSON_URL, f"{CLOUD_DATA_DIR}/ct_boundaries.geojson")
    CSV_PATH = download_from_gdrive(CLOUD_CSV_URL, f"{CLOUD_DATA_DIR}/ct_values.csv")
else:
    GEOJSON_PATH = "config/prototype/ct_boundaries.geojson"
    CSV_PATH = "config/prototype/ct_values.csv"

JOIN_KEY = "DGUID"
unit = "(Pop. %)"
METRICS = {
    f"Age 20-34 {unit}": "age_20to34",
    f"Renting {unit}": "renting",
    f"Visible Minority {unit}": "viz_minority",
    f"Bachelor's or higher {unit}": "edu_abvBach",
    f"Immigrated in 2016-2021 {unit}": "immigrated_af2016"
}

# any aditional columns to add to the joint table
columns_others = ['riding_name']

# --- Load and merge ---
gdf, logs = load_geojson(GEOJSON_PATH)
df = load_ct_values(CSV_PATH)

if gdf is not None and df is not None:
    df = df[[JOIN_KEY, "metro"] + list(METRICS.values()) + columns_others].copy()

    # --- Always filter by metro ---
    metro_options = sorted(df["metro"].dropna().unique())
    # if the default isn't in the table, select the first metro available
    if default_metro not in metro_options:
        default_metro = metro_options[0]
    selected_metro = st.sidebar.selectbox("Select metro area (searchable):",
                                          metro_options, index=metro_options.index(default_metro),
                                          help="Tip: you can use the dropdown a search bar too")

    # --- Sidebar metric selection ---
    selected_label = st.sidebar.selectbox("Select metric to visualize:", list(METRICS.keys()))
    selected_metric = METRICS[selected_label]

    # --- Filter data by metro ---
    df = df[df["metro"] == selected_metro]
    gdf = gdf[gdf[JOIN_KEY].isin(df[JOIN_KEY])]
    gdf = gdf.merge(df, on=JOIN_KEY, how="left")

    # --- Compute center ---
    center, zoom_start = compute_map_view(gdf)

    # --- Base map ---
    base_map = folium.Map(location=center, zoom_start=zoom_start, tiles="cartodbpositron")

    # --- Add each metric as a separate (exclusive) base layer ---
    fg_dict = {}
    colorbars = {}
    for label, metric in METRICS.items():
        choropleth, colorbar = add_custom_choropleth(
            fmap=None,
            gdf=gdf,
            value_column=metric,
            popup_fields=["CTUID", "riding_name", metric], #JOIN_KEY,
            popup_aliases=["ID:", "Riding:", "Value:"], #"DGUID:",
        )
        fg = folium.FeatureGroup(name=label, overlay=True)
        if colorbar:
            colorbars[label] = colorbar
        fg.add_child(choropleth)
        fg_dict[label] = fg

    # --- Display map ---
    st.markdown(f"""
    <div>
      <h4 style='font-size: 1rem; margin-top: -1.3rem; margin-bottom: -1.5rem; opacity: 0.8;'>{selected_label} - {selected_metro} </h4>
    </div>
    """, unsafe_allow_html=True)

    st_folium(
        base_map,
        feature_group_to_add=fg_dict[selected_label],
        height=600,
        use_container_width=True,
        returned_objects=[],
        key="map"
    )

    # --- Show colorbar ---
    legend_html = colorbars[selected_label]._repr_html_()
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            padding-right: 10px;
            margin-top: -650px;
        ">
            <div style="
                padding: 6px;
                border-radius: 4px;
                max-width: 100%;
            ">
                {legend_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Optional debug section ---
    with st.expander("Logs and diagnostics"):
        if logs:
            for msg in logs:
                st.info(msg)
        st.dataframe(gdf[[JOIN_KEY, "CTNAME", selected_metric]].head())
else:
    st.warning("Unable to load or render CT boundaries.")
