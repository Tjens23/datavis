"""Relationship/correlation graph visualization for earthquake data."""
import plotly.graph_objects as go
import numpy as np


def build_relation_graph(earthquakes):
    """Build a correlation heatmap showing relationships between earthquake variables.
    
    Args:
        earthquakes: DataFrame containing earthquake data
        
    Returns:
        Plotly figure object with correlation heatmap
    """
    df = earthquakes.copy()
    
    # Select numeric columns for correlation analysis
    numeric_cols = ['magnitude', 'depth', 'latitude', 'longitude']
    available_cols = [col for col in numeric_cols if col in df.columns]
    
    if len(available_cols) < 2:
        # Return empty figure if not enough numeric columns
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough numeric data for correlation analysis",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Calculate correlation matrix
    corr_matrix = df[available_cols].corr()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=available_cols,
        y=available_cols,
        colorscale='RdBu_r',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 12},
        hoverongaps=False,
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Variable Correlation Matrix",
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(side="bottom"),
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
        height=400,
        margin=dict(l=80, r=40, t=60, b=80)
    )
    
    return fig
