import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- File paths ---
GEOJSON_PATH = "config/prototype/ct_boundaries.geojson"
CSV_PATH = "config/prototype/ct_values.csv"
JOIN_KEY = "DGUID"

# --- Page setup ---
st.set_page_config(page_title="InsightAtlas Prototype", layout="wide")
st.title("InsightAtlas: CT Boundary Viewer")

# --- Load GeoJSON with fix for invalid geometries and reproject to EPSG:4326 ---
st.subheader("Loading CT Boundaries")

@st.cache_data
def load_geojson(path):
    try:
        gdf = gpd.read_file(path)

        # Fix invalid geometries
        invalid_count = (~gdf.geometry.is_valid).sum()
        if invalid_count > 0:
            st.warning(f"Fixing {invalid_count} invalid geometries using buffer(0)")
            gdf["geometry"] = gdf["geometry"].buffer(0)

        # Reproject if necessary
        if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
            st.info(f"Reprojecting from {gdf.crs} to EPSG:4326...")
            gdf = gdf.to_crs(epsg=4326)

        # simplify the geomretry for the rendering, 0.0001 is about 10m resolution
        gdf["geometry"] = gdf["geometry"].simplify(0.0001, preserve_topology=True)

        return gdf
    except Exception as e:
        st.error(f"Failed to load GeoJSON: {e}")
        return None

@st.cache_data
def load_ct_values(csv_path):
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Failed to load CT values CSV: {e}")
        return None

# --- Load and filter data ---
gdf = load_geojson(GEOJSON_PATH)
df_values = load_ct_values(CSV_PATH)

if gdf is not None and df_values is not None:
    # Filter GeoDataFrame to include only CTs in the values CSV
    gdf = gdf[gdf[JOIN_KEY].isin(df_values[JOIN_KEY])]

    # Merge indicator data into GeoDataFrame
    gdf = gdf.merge(df_values[[JOIN_KEY, "age_20to34"]], on=JOIN_KEY, how="left")

    st.success(f"Filtered to {len(gdf)} CT boundaries based on data availability.")
    st.dataframe(gdf[[JOIN_KEY, "CTNAME", "LANDAREA", "age_20to34"]].head())

    # --- Map Rendering ---
    st.subheader("Map Preview")

    centroid = gdf.geometry.unary_union.centroid
    center_coords = [centroid.y, centroid.x]

    m = folium.Map(location=center_coords, zoom_start=11, tiles="cartodbpositron")

    # Choropleth layer using age_20to34
    folium.Choropleth(
        geo_data=gdf,
        data=gdf,
        columns=[JOIN_KEY, "age_20to34"],
        key_on=f"feature.properties.{JOIN_KEY}",
        fill_color="YlGnBu",
        fill_opacity=0.6,
        line_opacity=0.2,
        legend_name="Age 20–34 (%)",
        nan_fill_color="lightgray",
    ).add_to(m)

    # GeoJson layer with popups and highlight
    folium.GeoJson(
        gdf,
        name="CT Boundaries",
        style_function=lambda feature: {
            'color': 'darkgray',       # Border color
            'weight': 1.5,             # Thinner border
            'fillOpacity': 0           # Transparent fill for now
        },
        # highlight the boarder when clicking
        highlight_function=lambda feature: {
            'weight': 2,
            'color': '#ff6600',
            'fillOpacity': 0.1
        },
        # show pop up only when clicked
        popup=folium.GeoJsonPopup(
            fields=[JOIN_KEY, "CTNAME"],
            aliases=["CTUID:", "Name:"],
            localize=True
        )
    ).add_to(m)

    st_folium(m, width=900, height=600, returned_objects=[])
else:
    st.warning("Unable to load or render CT boundaries.")
