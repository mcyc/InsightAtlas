import math

def compute_map_view(gdf):
    """
    Returns (center, zoom_level) for a GeoDataFrame such that all features are in view.
    """
    bounds = gdf.total_bounds  # (minx, miny, maxx, maxy)
    minx, miny, maxx, maxy = bounds
    center = [(miny + maxy) / 2, (minx + maxx) / 2]

    # Estimate zoom level (approximate) based on the East-West bounds extent
    lat_diff = abs(maxy - miny)
    max_diff = lat_diff

    print(f"max_diff: {max_diff}")

    # Heuristic to estimate zoom level (log scale inverse to coverage width)
    # Based on Web Mercator zoom level scale (~156543m per pixel at zoom 0)
    if max_diff == 0:
        zoom = 10
    else:
        zoom = 8.7 - math.log2(max_diff)
        zoom = max(3, min(zoom, 14))  # clamp zoom between 3 and 14

    return center, zoom
