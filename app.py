import faicons as fa
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
import numpy as np

# Load data and compute static values
from shared import app_dir, earthquakes
from map import build_earthquake_map
from shinywidgets import render_plotly
from shinywidgets import render_widget

from shiny import reactive, render
from shiny.express import input, ui

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

mag_rng = (earthquakes.magnitude.min(), earthquakes.magnitude.max())
depth_rng = (earthquakes.depth.min(), earthquakes.depth.max())
manual_pdf_path = "manual.pdf"  # Served from the app's www/ directory
raw_columns = earthquakes.columns.tolist()


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


@reactive.effect
@reactive.event(input.raw_select_all_btn)
def _select_all_raw_columns():
    ui.update_checkbox_group("raw_columns", selected=raw_columns)


@reactive.effect
@reactive.event(input.raw_clear_all_btn)
def _clear_all_raw_columns():
    ui.update_checkbox_group("raw_columns", selected=[])


@reactive.effect
def _update_raw_toggle_label():
    sel = list(input.raw_columns() or raw_columns)
    ui.update_action_button("raw_toggle", label=f"{len(sel)} of {len(raw_columns)} columns \u25be")


# --------------------------------------------------------

# Add page title
ui.page_opts(title="", fillable=False)

ICONS = {
    "earth": fa.icon_svg("earth-americas"),
    "gauge": fa.icon_svg("gauge-high"),
    "arrows": fa.icon_svg("arrows-down-to-people"),
    "ellipsis": fa.icon_svg("ellipsis"),
    "chevron": fa.icon_svg("chevron-down"),
}

with ui.navset_bar(title="Recent Earthquakes", id="tabs"):
    with ui.nav_panel("Dashboard"):
        with ui.layout_columns(col_widths=[3, 9], gap="lg"):
            with ui.card(full_screen=True):
                ui.card_header("Filters")
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

            with ui.div(class_="d-flex flex-column gap-4 w-100"):
                with ui.layout_columns(fill=False):
                    with ui.value_box(showcase=ICONS["earth"], style="height: 70px"):
                        "Total earthquakes"

                        @render.express
                        def total_earthquakes():
                            earthquake_data().shape[0]

                    with ui.value_box(showcase=ICONS["gauge"], style="min-height: 140px"):
                        "Average magnitude"

                        @render.express
                        def average_magnitude():
                            d = earthquake_data()
                            if d.shape[0] > 0:
                                f"{d.magnitude.mean():.2f}"

                    with ui.value_box(showcase=ICONS["arrows"], style="min-height: 140px"):
                        "Average depth"

                        @render.express
                        def average_depth():
                            d = earthquake_data()
                            if d.shape[0] > 0:
                                f"{d.depth.mean():.1f} km"

                with ui.layout_columns(col_widths=[6, 6, 12]):
                    with ui.card(full_screen=True):
                        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                            "Magnitude vs Depth"
                            with ui.popover(title="Add a color variable", placement="top"):
                                ICONS["ellipsis"]
                                ui.input_radio_buttons(
                                    "scatter_color",
                                    None,
                                    ["none", "magType", "net"],
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

                with ui.layout_columns(col_widths=[12]):
                    with ui.card(full_screen=True, style="aspect-ratio: 1; min-height: 600px"):
                        ui.card_header("Earthquake map")
                        with ui.card_body(style="height: 100%"):
                            @render_plotly
                            def earthquake_map():
                                return build_earthquake_map(earthquake_data())

    with ui.nav_panel("Raw data"):
        with ui.card(full_screen=True):
            with ui.card_header(class_="d-flex justify-content-between align-items-center", style="position: relative;"):
                "Raw data (unfiltered)"
                ui.input_action_button(
                    "raw_toggle",
                    f"{len(raw_columns)} of {len(raw_columns)} columns \u25be",
                    class_="btn btn-link text-primary p-0",
                )
                with ui.panel_conditional("input.raw_toggle % 2 === 1"):
                    ui.div(
                        {
                            "style": "position: absolute; right: 0; top: calc(100% + 0.5rem); z-index: 2000;",
                            "class": "shadow-sm border bg-white p-3 rounded-3",
                        },
                        ui.div(
                            ui.input_action_button("raw_select_all_btn", "Select all", class_="btn btn-sm btn-outline-primary"),
                            ui.input_action_button("raw_clear_all_btn", "Clear", class_="btn btn-sm btn-outline-secondary"),
                            class_="d-flex gap-2 mb-2",
                        ),
                        ui.div(
                            ui.input_checkbox_group(
                                "raw_columns",
                                None,
                                choices=raw_columns,
                                selected=raw_columns,
                                inline=False,
                            ),
                            style="max-height: 240px; width: 260px; overflow-y: auto;",
                        ),
                    )

            @render.data_frame
            def raw_table():
                cols = list(input.raw_columns() or raw_columns)
                return render.DataGrid(earthquakes[cols])
    
    with ui.nav_panel("Manual"):
        with ui.card(full_screen=False):
            ui.card_header("Download manual")
            ui.markdown("Get the PDF version of the manual below.")
            ui.tags.a(
                "Download PDF",
                href=manual_pdf_path,
                download="manual.pdf",
                class_="btn btn-primary d-inline-flex align-items-center",
                style="width: fit-content; padding: 0.35rem 0.9rem;",
            )

ui.include_css(app_dir / "styles.css")
