import plotly.express as px
import pandas as pd

def build_scatterplot_matrix(df: pd.DataFrame):
    """
    Create a scatterplot matrix (SPLOM) showing pairwise relations for key attributes.
    Attributes: magnitude, depth, latitude, longitude, felt, alert, tsunami
    """
    # Select important columns (adjust as needed)
    columns = [
        'magnitude', 'depth', 'felt'
    ]
    # Filter out missing values for selected columns
    df_filtered = df.dropna(subset=columns)
    labels = {
        'magnitude': 'Magnitude',
        'depth': 'Depth',
        'felt': 'Felt Reports',
    }
    fig = px.scatter_matrix(
        df_filtered,
        dimensions=['magnitude', 'depth', 'felt'],
        labels=labels,
        title=""
    )
    fig.update_traces(diagonal_visible=False)
    fig.update_layout(
        margin=dict(l=40, r=20, t=40, b=60),
        autosize=False,
        width=440,
        height=440
    )
    # Ensure x-axis titles are visible for each subplot
    # Fix axis title assignment
    for axis in fig.layout:
        if axis.startswith('xaxis'):
            if hasattr(fig.layout[axis], 'title') and hasattr(fig.layout[axis].title, 'text'):
                if not fig.layout[axis].title.text:
                    fig.layout[axis].title.text = axis.replace('xaxis', '').capitalize() or 'Value'
    # Explicitly set axis titles for each subplot
    for i, dim in enumerate(['magnitude', 'depth', 'felt'], start=1):
        axis_name = f'xaxis{i}'
        if axis_name in fig.layout:
            fig.layout[axis_name].title.text = labels[dim]
    fig.update_layout(
        margin=dict(l=40, r=20, t=0, b=80),
        autosize=False,
        width=440,
        height=440
    )
    return fig
