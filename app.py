import faicons as fa
import plotly.express as px

# Load data and compute static values
from shared import app_dir, earthquakes
from shinywidgets import render_plotly

from shiny import reactive, render
from shiny.express import input, ui

mag_rng = (earthquakes.magnitude.min(), earthquakes.magnitude.max())
depth_rng = (earthquakes.depth.min(), earthquakes.depth.max())

# Add page title and sidebar
ui.page_opts(title="Recent Earthquakes", fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_slider(
        "magnitude",
        "Magnitude",
        min=mag_rng[0],
        max=mag_rng[1],
        value=mag_rng,
        step=0.1,
    )
    ui.input_slider(
        "depth",
        "Depth (km)",
        min=depth_rng[0],
        max=depth_rng[1],
        value=depth_rng,
        step=1,
    )
    ui.input_checkbox_group(
        "mag_type",
        "Magnitude Type",
        earthquakes.magType.unique().tolist()[:5],
        selected=earthquakes.magType.unique().tolist()[:5],
        inline=True,
    )
    ui.input_action_button("reset", "Reset filter")

# Add main content
ICONS = {
    "earth": fa.icon_svg("earth-americas"),
    "gauge": fa.icon_svg("gauge-high"),
    "arrows": fa.icon_svg("arrows-down-to-people"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["earth"]):
        "Total earthquakes"

        @render.express
        def total_earthquakes():
            earthquake_data().shape[0]

    with ui.value_box(showcase=ICONS["gauge"]):
        "Average magnitude"

        @render.express
        def average_magnitude():
            d = earthquake_data()
            if d.shape[0] > 0:
                f"{d.magnitude.mean():.2f}"

    with ui.value_box(showcase=ICONS["arrows"]):
        "Average depth"

        @render.express
        def average_depth():
            d = earthquake_data()
            if d.shape[0] > 0:
                f"{d.depth.mean():.1f} km"


with ui.layout_columns(col_widths=[6, 6, 12]):
    with ui.card(full_screen=True):
        ui.card_header("Earthquake data")

        @render.data_frame
        def table():
            return render.DataGrid(earthquake_data())

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Magnitude vs Depth"
            with ui.popover(title="Add a color variable", placement="top"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "scatter_color",
                    None,
                    ["none", "magType", "net", "status"],
                    inline=True,
                )

        @render_plotly
        def scatterplot():
            color = input.scatter_color()
            return px.scatter(
                earthquake_data(),
                x="magnitude",
                y="depth",
                color=None if color == "none" else color,
                labels={"magnitude": "Magnitude", "depth": "Depth (km)"},
                hover_data=["place", "datetime"],
            )

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Magnitude distribution"
            with ui.popover(title="Split by variable"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "mag_dist_y",
                    "Split by:",
                    ["magType", "net", "status"],
                    selected="magType",
                    inline=True,
                )

        @render_plotly
        def mag_distribution():
            from ridgeplot import ridgeplot

            dat = earthquake_data()
            yvar = input.mag_dist_y()
            uvals = dat[yvar].unique()

            samples = [[dat.magnitude[dat[yvar] == val]] for val in uvals]

            plt = ridgeplot(
                samples=samples,
                labels=uvals,
                bandwidth=0.1,
                colorscale="viridis",
                colormode="row-index",
            )

            plt.update_layout(
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
                )
            )

            return plt


ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


@reactive.calc
def earthquake_data():
    mag = input.magnitude()
    depth = input.depth()
    idx1 = earthquakes.magnitude.between(mag[0], mag[1])
    idx2 = earthquakes.depth.between(depth[0], depth[1])
    idx3 = earthquakes.magType.isin(input.mag_type())
    return earthquakes[idx1 & idx2 & idx3]


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("magnitude", value=mag_rng)
    ui.update_slider("depth", value=depth_rng)
    ui.update_checkbox_group("mag_type", selected=earthquakes.magType.unique().tolist()[:5])
