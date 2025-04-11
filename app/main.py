import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path
import requests
import uuid
from shapely.geometry import GeometryCollection
import numpy as np

APP_VERSION = "v0.1.0-beta.1"

# --- Ensure set_page_config is the first Streamlit command ---
st.set_page_config(page_title="InsightAtlas | Canadian Demographic Explorer", layout="wide")
st.sidebar.caption(f"Version: {APP_VERSION}")
st.subheader("Census Tracts 2021")

# --- Configuration Block ---
# Use cloud data or local files
use_cloud_data = True

# Cloud data settings (update these URLs with your actual Google Drive file IDs)

CLOUD_CSV_URL = "https://drive.google.com/uc?export=download&id=1ERHEMcBhyPcgYq2r5iwxEO9KIH45TAN7"
CLOUD_GEOJSON_URL = "https://drive.google.com/uc?export=download&id=1galoO4I9wobrq0lo-ojPCKg0B6ZHrlob"

# Local directory for cloud data (both locally and when deployed)
CLOUD_DATA_DIR = "data/cloud"

# --- Set file paths based on configuration ---
if use_cloud_data:
    def download_from_gdrive(url, dest_path):
        dest_path = Path(dest_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        status_placeholder = st.empty()  # Temporary message container

        if not dest_path.exists():
            status_placeholder.info(f"Downloading {dest_path.name} from cloud...")
            response = requests.get(url)

            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    status_placeholder.empty()
                    st.error(
                        f"{dest_path.name} appears to be an HTML file. "
                        "Please check sharing permissions or use a proper direct download link."
                    )
                    return None
                dest_path.write_bytes(response.content)
                status_placeholder.empty()  # Remove "Downloading..." message
            else:
                status_placeholder.empty()
                st.error(f"Failed to download {dest_path.name} (status code: {response.status_code})")
                return None
        return str(dest_path)

    GEOJSON_PATH = download_from_gdrive(CLOUD_GEOJSON_URL, f"{CLOUD_DATA_DIR}/ct_boundaries.geojson")
    CSV_PATH = download_from_gdrive(CLOUD_CSV_URL, f"{CLOUD_DATA_DIR}/ct_values.csv")
    if GEOJSON_PATH is None or CSV_PATH is None:
        st.error("Cloud data download failed. Please check the URLs and file sharing settings on Google Drive.")
        st.stop()
else:
    GEOJSON_PATH = "config/prototype/ct_boundaries.geojson"
    CSV_PATH = "config/prototype/ct_values.csv"

JOIN_KEY = "DGUID"

# --- Load GeoJSON with fixes for invalid geometries and reproject to EPSG:4326 ---
@st.cache_data
def load_geojson(path):
    logs = []
    try:
        gdf = gpd.read_file(path)

        # Fix invalid geometries
        invalid_count = (~gdf.geometry.is_valid).sum()
        if invalid_count > 0:
            logs.append(f"Fixed {invalid_count} invalid geometries using buffer(0).")
            gdf["geometry"] = gdf["geometry"].buffer(0)

        # Reproject if necessary
        if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
            logs.append(f"Reprojected from {gdf.crs} to EPSG:4326.")
            gdf = gdf.to_crs(epsg=4326)

        # Simplify the geometry for rendering (0.0001 is about 10m resolution)
        gdf["geometry"] = gdf["geometry"].simplify(0.0001, preserve_topology=True)

        return gdf, logs
    except Exception as e:
        st.error(f"Failed to load GeoJSON: {e}")
        return None, []

@st.cache_data
def load_ct_values(csv_path):
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Failed to load CT values CSV: {e}")
        return None

# --- Load and filter data ---
gdf, preprocessing_logs = load_geojson(GEOJSON_PATH)
df_values = load_ct_values(CSV_PATH)

if gdf is not None and df_values is not None:
    # Filter GeoDataFrame to include only CTs present in the values CSV
    gdf = gdf[gdf[JOIN_KEY].isin(df_values[JOIN_KEY])]

    # Define metric options and labels
    unit = "(Pop. %)"
    metric_options = {
        f"Age 20-34 {unit}": "age_20to34",
        f"Renting {unit}": "renting",
        f"Visible Minority {unit}": "viz_minority",
        f"Bachelor's or higher {unit}": "edu_abvBach",
        f"Immigrated in 2016-2021 {unit}": "immigrated_af2016"
    }

    # Select metric from dropdown in sidebar
    selected_label = st.sidebar.selectbox("Select metric to visualize:", list(metric_options.keys()))
    selected_metric = metric_options[selected_label]

    # Label the map
    st.markdown(f"""
    <div>
      <h4 style='font-size: 1rem; margin-top: -1.3rem; margin-bottom: -1.5rem; opacity: 0.8;'>{selected_label}</h4>
    </div>
    """, unsafe_allow_html=True)

    # Merge selected metric into the GeoDataFrame
    gdf = gdf.merge(df_values[[JOIN_KEY, selected_metric]], on=JOIN_KEY, how="left")

    unioned = gdf.geometry.union_all()

    # If it's a GeometryCollection, compute the centroid of all its parts
    if isinstance(unioned, GeometryCollection):
        # Filter to geometries with area > 0 (avoid empty LineStrings/Points)
        parts = [geom for geom in unioned.geoms if geom.area > 0]
        if parts:
            centroid = GeometryCollection(parts).centroid
        else:
            centroid = unioned.centroid
    else:
        centroid = unioned.centroid

    # --- Map Rendering ---
    center_coords = [centroid.y, centroid.x]

    m = folium.Map(location=center_coords, zoom_start=9.4, tiles="cartodbpositron")

    # Ensure the selected metric is numeric
    gdf[selected_metric] = pd.to_numeric(gdf[selected_metric], errors='coerce')

    # Defensive bin generation
    min_val = gdf[selected_metric].min()
    max_val = gdf[selected_metric].max()

    if pd.isna(min_val) or pd.isna(max_val):
        st.error(f"No valid data for metric '{selected_label}'")
        st.stop()

    if abs(max_val - min_val) < 1e-6:
        min_val -= 0.01
        max_val += 0.01

    bins = list(np.linspace(min_val, max_val, 9))

    # Choropleth layer using selected metric
    choropleth = folium.Choropleth(
        geo_data=gdf,
        data=gdf,
        columns=[JOIN_KEY, selected_metric],
        key_on=f"feature.properties.{JOIN_KEY}",
        fill_color="magma_r",
        fill_opacity=0.6,
        line_opacity=0.2,
        nan_fill_color="lightgray",
        bins=bins,#9,
    )
    try:
        choropleth.color_scale.width = 300
    except Exception as e:
        st.warning("Could not adjust color scale width.")

    unique_key = f"{selected_metric}_{uuid.uuid4()}"

    try:
        choropleth.add_to(m)

        folium.GeoJson(
            gdf,
            name="CT Boundaries",
            style_function=lambda feature: {
                'color': 'darkgray',
                'weight': 1.5,
                'fillOpacity': 0
            },
            highlight_function=lambda feature: {
                'weight': 3,
                'color': '#1f77b4',
                'fillOpacity': 0.2,
            },
            popup=folium.GeoJsonPopup(
                fields=[JOIN_KEY, "CTNAME", selected_metric],
                aliases=["DGUID:", "Name:", "Value:"],
                localize=True
            )
        ).add_to(m)

        st_folium(m, use_container_width=True, height=600, returned_objects=[], key=unique_key)
    except Exception as e:
        st.error("Map rendering failed due to an unexpected error.")
        st.exception(e)

    # --- Consolidated Collapsed Section ---
    with st.expander("Preprocessing logs, diagnostics, and data preview", expanded=False):
        # Show preprocessing logs
        if preprocessing_logs:
            st.markdown("**Preprocessing Logs:**")
            for msg in preprocessing_logs:
                st.info(msg)
        else:
            st.markdown("**Preprocessing Logs:** No issues detected.")

        # Diagnostics information
        st.markdown("**Diagnostics:**")
        st.success(f"Filtered to {len(gdf)} CT boundaries based on data availability.")
        st.write("Selected Metric:", selected_label, "→", selected_metric)

        # Data preview table
        st.markdown("**Data Preview (First 5 Rows):**")
        st.dataframe(gdf[[JOIN_KEY, "CTNAME", "LANDAREA", selected_metric]].head())
else:
    st.warning("Unable to load or render CT boundaries.")