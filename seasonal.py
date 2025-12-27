"""Monthly and seasonal earthquake distribution chart."""
import plotly.graph_objects as go


# Season colors
SEASON_COLORS = {
    "Winter": "#3b82f6",  # Blue
    "Spring": "#22c55e",  # Green
    "Summer": "#f59e0b",  # Orange/Yellow
    "Fall": "#ef4444",    # Red/Brown
}

# Month to season mapping
MONTH_TO_SEASON = {
    1: "Winter", 2: "Winter", 3: "Spring",
    4: "Spring", 5: "Spring", 6: "Summer",
    7: "Summer", 8: "Summer", 9: "Fall",
    10: "Fall", 11: "Fall", 12: "Winter"
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def build_monthly_chart(earthquakes):
    """Build a bar chart of earthquakes by month, colored by season, with a donut chart overlay."""
    df = earthquakes.copy()
    # Use existing 'month_num' and 'season' columns if present, otherwise create them
    if 'month_num' not in df.columns:
        if 'datetime' in df.columns:
            df['month_num'] = df['datetime'].dt.month
        elif 'month' in df.columns:
            df['month_num'] = df['month']
        else:
            raise ValueError("No 'month_num', 'month', or 'datetime' column found in DataFrame.")
    if 'season' not in df.columns:
        df['season'] = df['month_num'].apply(lambda x: MONTH_TO_SEASON[x])

    # Count earthquakes per month
    monthly_counts = df.groupby('month_num').size().reset_index(name='count')

    # Add month names and seasons (use existing if present)
    monthly_counts['month'] = monthly_counts['month_num'].apply(lambda x: MONTH_NAMES[x-1])
    if 'season' in df.columns:
        monthly_counts['season'] = monthly_counts['month_num'].map(df.drop_duplicates('month_num').set_index('month_num')['season'])
    else:
        monthly_counts['season'] = monthly_counts['month_num'].apply(lambda x: MONTH_TO_SEASON[x])

    # Sort by month number
    monthly_counts = monthly_counts.sort_values('month_num')

    # Calculate seasonal totals for donut chart
    seasonal_counts = monthly_counts.groupby('season')['count'].sum().reset_index()
    # Order seasons correctly
    season_order = ["Winter", "Spring", "Summer", "Fall"]
    seasonal_counts['order'] = seasonal_counts['season'].apply(lambda x: season_order.index(x))
    seasonal_counts = seasonal_counts.sort_values('order')

    # Create figure
    fig = go.Figure()

    # Add bar traces
    for season in ["Winter", "Spring", "Summer", "Fall"]:
        season_data = monthly_counts[monthly_counts['season'] == season]
        fig.add_trace(go.Bar(
            x=season_data['month'],
            y=season_data['count'],
            name=season,
            marker_color=SEASON_COLORS[season],
            hovertemplate="<b>%{x}</b><br>Earthquakes: %{y}<br>Season: " + season + "<extra></extra>",
            showlegend=True,
            xaxis='x',
            yaxis='y'
        ))

    # Add donut chart as a pie trace with domain positioning (inside bar chart, top left)
    fig.add_trace(go.Pie(
        labels=seasonal_counts['season'],
        values=seasonal_counts['count'],
        hole=0.5,
        marker_colors=[SEASON_COLORS[s] for s in seasonal_counts['season']],
        domain=dict(x=[0.02, 0.25], y=[0.5, 0.95]),
        textinfo='percent',
        textfont=dict(size=9),
        hovertemplate="<b>%{label}</b><br>Earthquakes: %{value}<br>%{percent}<extra></extra>",
        showlegend=False,
        name="Seasonal"
    ))

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Earthquakes",
        barmode='group',
        showlegend=True,
        legend=dict(
            x=0.97,
            y=0.97,
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
            font=dict(size=10),
            itemsizing='constant',
            indentation=10,
            title=dict(
                text="  Season",
                font=dict(size=10),
                side='top'
            )
        ),
        xaxis=dict(
            categoryorder='array',
            categoryarray=MONTH_NAMES,
            domain=[0, 1]
        ),
        margin={"l": 40, "r": 40, "t": 60, "b": 40},
        height=400
    )

    # Add highlight box for Jul-Sep
    max_count = monthly_counts['count'].max()
    fig.add_vrect(
        x0=5.5, x1=8.5,  # Numeric positions: between Jun(5) and Jul(6), between Sep(8) and Oct(9)
        fillcolor="rgba(245, 158, 11, 0.15)",  # Light orange
        layer="below",
        line_width=2,
        line_color="rgba(245, 158, 11, 0.5)",
    )

    # Add annotation for the highlighted region
    fig.add_annotation(
        x="Aug",
        y=max_count * 1.1,
        text="Peak Activity",
        showarrow=False,
        font=dict(size=12, color="#f59e0b", weight="bold"),
    )

    return fig
