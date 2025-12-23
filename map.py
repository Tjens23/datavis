import plotly.express as px
import plotly.graph_objects as go
import json
import urllib.request

# Cache tectonic plates data
_tectonic_plates_cache = None

def get_tectonic_plates():
    """Fetch tectonic plate boundaries GeoJSON (cached)."""
    global _tectonic_plates_cache
    if _tectonic_plates_cache is None:
        # Using the PB2002 plate boundaries dataset from GitHub
        url = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json"
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                _tectonic_plates_cache = json.loads(response.read().decode())
        except Exception as e:
            print(f"Could not fetch tectonic plates: {e}")
            _tectonic_plates_cache = {"type": "FeatureCollection", "features": []}
    return _tectonic_plates_cache


def build_earthquake_map(data, show_plates=True):
    """Return a Plotly mapbox figure for the given earthquake DataFrame."""
    if data.empty:
        return px.scatter_mapbox(lat=[], lon=[], zoom=1)

    fig = px.scatter_mapbox(
        data,
        lat="latitude",
        lon="longitude",
        color="depth",
        size="magnitude",
        hover_name="place",
        hover_data={"magnitude": True, "depth": True, "datetime": True},
        size_max=15,
        color_continuous_scale="Viridis",
        labels={"depth": "Depth (km)", "magnitude": "Magnitude"},
        zoom=1,
    )

    fig.update_traces(marker_opacity=0.8, marker=dict(sizemin=0.01))
    
    # Add tectonic plate boundaries
    if show_plates:
        plates = get_tectonic_plates()
        for feature in plates.get("features", []):
            if feature["geometry"]["type"] == "LineString":
                coords = feature["geometry"]["coordinates"]
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                fig.add_trace(go.Scattermapbox(
                    lon=lons,
                    lat=lats,
                    mode="lines",
                    line=dict(width=1.5, color="rgba(255, 100, 100, 0.6)"),
                    hoverinfo="skip",
                    showlegend=False,
                ))
            elif feature["geometry"]["type"] == "MultiLineString":
                for line in feature["geometry"]["coordinates"]:
                    lons = [c[0] for c in line]
                    lats = [c[1] for c in line]
                    fig.add_trace(go.Scattermapbox(
                        lon=lons,
                        lat=lats,
                        mode="lines",
                        line=dict(width=1.5, color="rgba(255, 100, 100, 0.6)"),
                        hoverinfo="skip",
                        showlegend=False,
                    ))
    
    fig.update_layout(
        mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0),
        autosize=True,
        dragmode="zoom",
    )

    return fig


