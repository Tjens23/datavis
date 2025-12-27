"""Geographic earthquake map visualization."""
import plotly.express as px
import plotly.graph_objects as go

from helpers import get_tectonic_plates


def build_earthquake_map(data, show_plates=True):
    """Return a Plotly mapbox figure for the given earthquake DataFrame."""
    if data.empty:
        fig = px.scatter_mapbox(lat=[], lon=[], zoom=1)
        return fig

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
        # Add legend entry for tectonic plate boundary (dummy trace)
        fig.add_trace(go.Scattermapbox(
            lon=[None, None],
            lat=[None, None],
            mode="lines",
            line=dict(width=2, color="rgba(255, 100, 100, 0.6)"),
            name="Tectonic plate boundary",
            showlegend=True,
            hoverinfo="skip",
            visible=True,
            legendgroup="tectonic",
            legendrank=100
        ))
        # Add padding to legend
        fig.update_layout(
            legend=dict(
                itemsizing='constant',
                yanchor='top',
                y=0.98,
                xanchor='left',
                x=0.01,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.1)',
                borderwidth=1,
                font=dict(size=12),
                title_font=dict(size=13),
            )
        )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, t=0, b=0),
        autosize=True,
        dragmode="zoom"
    )

    return fig
