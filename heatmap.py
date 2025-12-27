import plotly.express as px
import pandas as pd

def build_mag_depth_heatmap(df: pd.DataFrame):
    """
    Create a heatmap showing the density of events for each magnitude/depth category pair.
    Uses 'magnitude_category' and 'depth_category' columns in the DataFrame.
    """
    heatmap_data = df.groupby(['magnitude_category', 'depth_category']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='magnitude_category', columns='depth_category', values='count').fillna(0)
    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Depth Category", y="Magnitude Category", color="Event Count"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale="OrRd",
        text_auto=True
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=0, b=20),
        coloraxis_showscale=False,
        autosize=False,
        width=440,
        height=440
    )
    return fig
