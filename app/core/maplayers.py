import folium
import branca
import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as mcolors


def matplotlib_to_step_colormap(cmap_name, bins, nan_color="#d3d3d3"):
    cmap = cm.get_cmap(cmap_name)
    norm = mcolors.Normalize(vmin=bins[0], vmax=bins[-1])
    colors = [mcolors.to_hex(cmap(norm(v))) for v in bins[:-1]]
    return branca.colormap.StepColormap(
        colors=colors,
        index=bins,
        vmin=bins[0],
        vmax=bins[-1],
    )

def add_custom_choropleth(
    fmap,
    gdf,
    value_column,
    key_on,
    bins=None,
    cmap="magma_r",
    nan_color="#d3d3d3",
    fill_opacity=0.6,
    line_opacity=0.2,
    border_color="darkgray",
    popup_fields=None,
    popup_aliases=None,
    show_legend=True,
    legend_caption=None,
    colorbar_width=300,
):
    """
    Add a more efficient custom choropleth layer using folium.GeoJson and precomputed colors.
    Supports both branca and matplotlib colormaps.
    """
    # Ensure data is numeric
    values = pd.to_numeric(gdf[value_column], errors="coerce")

    # Define bins if not provided
    if bins is None:
        min_val = values.min()
        max_val = values.max()
        if pd.isna(min_val) or pd.isna(max_val):
            raise ValueError("No valid values for choropleth")
        if abs(max_val - min_val) < 1e-6:
            min_val -= 0.01
            max_val += 0.01
        bins = np.linspace(min_val, max_val, 9)

    # Try branca first, fallback to matplotlib colormap
    try:
        branca_cmap = getattr(branca.colormap.linear, cmap)
        colormap = branca_cmap.scale(bins[0], bins[-1]).to_step(n=len(bins)-1)
    except AttributeError:
        colormap = matplotlib_to_step_colormap(cmap, bins, nan_color)

    if legend_caption:
        colormap.caption = legend_caption

    # Assign colors to each row
    gdf["__choropleth_color__"] = values.apply(lambda x: colormap(x) if pd.notnull(x) else nan_color)

    # Create the GeoJson layer with color styling
    choropleth_layer = folium.GeoJson(
        gdf,
        name="Choropleth",
        style_function=lambda feature: {
            "fillColor": feature["properties"]["__choropleth_color__"],
            "color": border_color,
            "weight": 1.5,
            "fillOpacity": fill_opacity,
            "opacity": line_opacity,
        },
        highlight_function=lambda feature: {
            "weight": 3,
            "color": "#1f77b4",
            "fillOpacity": 0.2,
        },
        popup=folium.GeoJsonPopup(
            fields=popup_fields or [value_column],
            aliases=popup_aliases or [value_column],
            localize=True,
        ) if popup_fields else None,
    )
    choropleth_layer.add_to(fmap)

    if show_legend:
        colormap.width = colorbar_width
        colormap.add_to(fmap)

    return choropleth_layer
