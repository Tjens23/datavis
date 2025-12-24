import plotly.express as px


def build_scatterplot(data, color_var):
    """Build a scatter plot of magnitude vs depth."""
    if len(data) == 0:
        return px.scatter(title="No data to display")
    
    if color_var == "none":
        fig = px.scatter(
            data, 
            x='magnitude', 
            y='depth',
            hover_name='place',
            hover_data=['datetime', 'magnitude', 'depth'],
            labels={'magnitude': 'Magnitude', 'depth': 'Depth (km)'},
            title='Magnitude vs Depth'
        )
    else:
        fig = px.scatter(
            data, 
            x='magnitude', 
            y='depth',
            color=color_var,
            hover_name='place',
            hover_data=['datetime', 'magnitude', 'depth'],
            labels={'magnitude': 'Magnitude', 'depth': 'Depth (km)'},
            title='Magnitude vs Depth'
        )
    
    fig.update_traces(marker=dict(size=8, opacity=0.6))
    fig.update_layout(height=400)
    
    return fig
