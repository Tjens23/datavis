import kagglehub
import pandas as pd
import os
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go

path = kagglehub.dataset_download("shreyasur965/recent-earthquakes")
print("Path to dataset files:", path)

csv_file = os.path.join(path, "earthquakes.csv")
df = pd.read_csv(csv_file)

app = Dash(__name__)

fig_magnitude = px.histogram(df, x='magnitude', nbins=50, 
                              title='Earthquake Magnitude Distribution',
                              labels={'magnitude': 'Magnitude', 'count': 'Frequency'})

fig_map = px.scatter_geo(df, lat='latitude', lon='longitude', 
                          color='magnitude', size='magnitude',
                          hover_name='place', hover_data=['magnitude', 'depth'],
                          title='Earthquake Locations Worldwide',
                          color_continuous_scale='Reds')

fig_depth_mag = px.scatter(df, x='depth', y='magnitude', 
                            color='magnitude', hover_name='place',
                            title='Earthquake Depth vs Magnitude',
                            labels={'depth': 'Depth (km)', 'magnitude': 'Magnitude'},
                            color_continuous_scale='Viridis')

location_counts = df['place'].value_counts().head(10)
fig_locations = px.bar(x=location_counts.values, y=location_counts.index,
                       orientation='h',
                       title='Top 10 Locations by Earthquake Count',
                       labels={'x': 'Count', 'y': 'Location'})

app.layout = html.Div([
    html.H1('Recent Earthquakes Dashboard', 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    html.Div([
        html.H3(f'Total Earthquakes: {len(df)}', style={'textAlign': 'center'}),
        html.H3(f'Average Magnitude: {df["magnitude"].mean():.2f}', style={'textAlign': 'center'}),
        html.H3(f'Max Magnitude: {df["magnitude"].max():.2f}', style={'textAlign': 'center'}),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 30}),
    
    dcc.Graph(figure=fig_map),
    
    html.Div([
        html.Div([dcc.Graph(figure=fig_magnitude)], style={'width': '48%'}),
        html.Div([dcc.Graph(figure=fig_depth_mag)], style={'width': '48%'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    
    dcc.Graph(figure=fig_locations),
], style={'padding': 20})

if __name__ == '__main__':
    app.run(debug=True)