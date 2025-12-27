"""Scatter plot visualization for earthquake magnitude vs depth."""
import plotly.express as px


def build_scatterplot(data, color_var):
    """Build a scatter plot of magnitude vs depth.

    Args:
        data: DataFrame containing earthquake data with 'magnitude' and 'depth'
        color_var: Variable to use for coloring points ('none', 'magType', 'net')

    Returns:
        Plotly figure object
    """
    color = None if color_var == "none" else color_var
    fig = px.scatter(
        data,
        x="magnitude",
        y="depth",
        color=color,
        opacity=0.7,
        labels={"magnitude": "Magnitude", "depth": "Depth (km)"},
    )
    fig.update_layout(
        yaxis={"autorange": "reversed"},
        margin={"l": 40, "r": 20, "t": 20, "b": 40},
    )
    return fig
