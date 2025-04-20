import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path
import requests

from core.maplayers import add_custom_choropleth
from utils.map_utils import compute_map_view

APP_VERSION = "v0.4.0.dev1"
st.set_page_config(page_title="InsightAtlas | Canadian Demographic Explorer", layout="wide")
st.sidebar.caption(f"Version: {APP_VERSION}")
st.subheader("Census Tracts 2021")

# --- Configuration ---
use_cloud_data = False
CLOUD_DATA_DIR = "data/cloud"
CLOUD_CSV_URL = "https://drive.google.com/uc?export=download&id=1ERHEMcBhyPcgYq2r5iwxEO9KIH45TAN7"
CLOUD_GEOJSON_URL = "https://drive.google.com/uc?export=download&id=1galoO4I9wobrq0lo-ojPCKg0B6ZHrlob"

# default city
default_metro = "Vancouver"

def download_from_gdrive(url, dest_path):
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if not dest_path.exists():
        status = st.empty()
        status.info(f"Downloading {dest_path.name}...")
        r = requests.get(url)
        if r.status_code == 200 and "text/html" not in r.headers.get("Content-Type", ""):
            dest_path.write_bytes(r.content)
        else:
            status.empty()
            st.error(f"Download failed or invalid format for {dest_path.name}")
            return None
        status.empty()
    return str(dest_path)

if use_cloud_data:
    GEOJSON_PATH = download_from_gdrive(CLOUD_GEOJSON_URL, f"{CLOUD_DATA_DIR}/ct_boundaries.geojson")
    CSV_PATH = download_from_gdrive(CLOUD_CSV_URL, f"{CLOUD_DATA_DIR}/ct_values.csv")
else:
    dir_local = "data/local"
    GEOJSON_PATH = f"{dir_local}/ct_boundaries.geojson"
    GEOJSON_PATH_2 = f"{dir_local}/FED_ED_boundaries_2023.geojson"
    CSV_PATH = f"{dir_local}/ct_values.csv"

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

@st.cache_data
def load_geojson(path):
    logs = []
    try:
        gdf = gpd.read_file(path)
        if (~gdf.geometry.is_valid).sum() > 0:
            logs.append("Fixed invalid geometries using buffer(0).")
            gdf["geometry"] = gdf["geometry"].buffer(0)
        if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
            logs.append(f"Reprojected from {gdf.crs} to EPSG:4326.")
            gdf = gdf.to_crs(epsg=4326)
        gdf["geometry"] = gdf["geometry"].simplify(0.0001, preserve_topology=True)
        return gdf, logs
    except Exception as e:
        st.error(f"Failed to load GeoJSON: {e}")
        return None, []

@st.cache_data
def load_ct_values(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Failed to load CT values CSV: {e}")
        return None

# --- Load and merge ---
gdf, logs = load_geojson(GEOJSON_PATH)
gdf2, logs2 = load_geojson(GEOJSON_PATH_2)
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

    # Ensure both GeoDataFrames are in the same CRS
    assert gdf.crs == gdf2.crs, "GeoDataFrames must be in the same CRS"
    # Spatial join to keep only EDs that intersect with the selected metro's tracts
    gdf2_filtered = gpd.sjoin(gdf2, gdf, how="inner", predicate="intersects").drop_duplicates(
        subset=gdf2.columns.tolist())

    # --- Compute center ---
    center, zoom_start = compute_map_view(gdf)

    # --- Base map ---
    base_map = folium.Map(location=center, zoom_start=zoom_start, tiles="cartodbpositron")

    # --- Add electoral districts boundaries ---
    label_ed = "Electoral District"
    show_ed = st.sidebar.checkbox("Show Electoral Districts", value=False)

    # --- Add each metric as a separate (exclusive) base layer ---
    fg_dict = {}
    colorbars = {}
    for label, metric in METRICS.items():

        # specify the popup info
        popup_fields=["CTUID", "riding_name", metric] #JOIN_KEY,
        popup_aliases=["ID:", "Riding:", "Value:"] #"DGUID:",

        choropleth, colorbar = add_custom_choropleth(
            fmap=None,
            gdf=gdf,
            value_column=metric,
            popup_fields=popup_fields,
            popup_aliases=popup_aliases
        )
        fg = folium.FeatureGroup(name=label, overlay=True)
        if colorbar:
            colorbars[label] = colorbar

        fg.add_child(choropleth)

        if show_ed:
            # add electoral district layer
            ed_layer = folium.GeoJson(
                gdf2_filtered,
                name="ED_bounds",
                style_function=lambda feature: {
                    "fillColor": None,
                    "color": "#4C6E91", #"DimGray" "#4C6E91"
                    "weight": 1.8,
                    "fillOpacity": 0.0,
                },
            )
            fg.add_child(ed_layer)

            # place a popup-only layer on the top
            interactive_layer, _ = add_custom_choropleth(
                fmap=None,
                gdf=gdf,
                value_column=metric,
                popup_fields=popup_fields,
                popup_aliases=popup_aliases,
                style_function=lambda feature: {
                    "color": "transparent",
                    "weight": 0,
                    "fillOpacity": 0.0,
                },
            )

            fg.add_child(interactive_layer)

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
