import plotly.express as px


def build_earthquake_map(data):
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
	fig.update_layout(
		mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0),
		autosize=True,
		dragmode="zoom",
	)

	return fig


