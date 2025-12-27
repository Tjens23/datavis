"""Recent Earthquakes Dashboard - Main Application."""
import matplotlib.pyplot as plt
import numpy as np

from shiny import reactive, render
from shiny import ui as ui_module
from shiny.express import input, ui
from shinywidgets import render_plotly

from shared import app_dir, earthquakes
from components import ICONS
from map import build_earthquake_map
from outliers import build_outliers_infographic
from scatterplot import build_scatterplot
from seasonal import build_monthly_chart
from heatmap import build_mag_depth_heatmap
from scatter_matrix import build_scatterplot_matrix
from timeseries import build_time_series_gif
from shinywidgets import render_plotly
from shinywidgets import render_widget

from shared import app_dir, earthquakes
from shiny import reactive, render
from shiny.express import input, ui
from shiny.ui import showcase_left_center

mag_rng = (earthquakes.magnitude.min(), earthquakes.magnitude.max())
depth_rng = (earthquakes.depth.min(), earthquakes.depth.max())
raw_columns = earthquakes.columns.tolist()
mag_types = earthquakes.magType.unique().tolist()[:5]

@reactive.calc
def earthquake_data():
    """Filter earthquake data based on user inputs."""
    mag = input.magnitude()
    depth = input.depth()
    idx1 = earthquakes.magnitude.between(mag[0], mag[1])
    idx2 = earthquakes.depth.between(depth[0], depth[1])
    idx3 = earthquakes.magType.isin(input.mag_type())
    return earthquakes[idx1 & idx2 & idx3]


@reactive.effect
@reactive.event(input.reset)
def _reset_filters():
    ui.update_slider("magnitude", value=mag_rng)
    ui.update_slider("depth", value=depth_rng)
    ui.update_checkbox_group("mag_type", selected=mag_types)


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
    ui.update_action_button("raw_toggle", label=f"{len(sel)} of {len(raw_columns)} columns ▾")



ui.page_opts(title="", fillable=False)

with ui.navset_bar(title="Recent Earthquakes", id="tabs"):

    # DASHBOARD TAB
    with ui.nav_panel("Dashboard"):
        with ui.layout_columns(col_widths=[3, 9], gap="lg"):

            # Sidebar: Filters
            with ui.card(full_screen=True):
                ui.card_header("Filters")
                ui.input_slider("magnitude", "Magnitude",
                    min=mag_rng[0], max=mag_rng[1], value=mag_rng, step=0.1)
                ui.input_slider("depth", "Depth (km)",
                    min=depth_rng[0], max=depth_rng[1], value=depth_rng, step=1)
                ui.input_checkbox_group("mag_type", "Magnitude Type",
                    mag_types, selected=mag_types, inline=True)
                ui.input_action_button("reset", "Reset filter")

            # Main content area
            with ui.div(class_="d-flex flex-column gap-4 w-100"):

                # Statistics cards
                with ui.layout_columns(fill=False):
                    with ui.card(class_="px-3 py-2"):
                        with ui.div(class_="d-flex align-items-center justify-content-between gap-3"):
                            with ui.div():
                                ui.p("Total earthquakes", class_="mb-0 text-muted small")
                                @render.express
                                def total_earthquakes():
                                    ui.p(str(earthquake_data().shape[0]), class_="mb-0 fs-4 fw-bold")
                            ui.div(ICONS["earth"], class_="text-primary", style="font-size: 4rem;")

                    with ui.card(class_="px-3 py-2"):
                        with ui.div(class_="d-flex align-items-center justify-content-between gap-3"):
                            with ui.div():
                                ui.p("Average magnitude", class_="mb-0 text-muted small")
                                @render.express
                                def average_magnitude():
                                    d = earthquake_data()
                                    if d.shape[0] > 0:
                                        ui.p(f"{d.magnitude.mean():.2f}", class_="mb-0 fs-4 fw-bold")
                            ui.div(ICONS["gauge"], class_="text-primary", style="font-size: 4rem;")

                    with ui.card(class_="px-3 py-2"):
                        with ui.div(class_="d-flex align-items-center justify-content-between gap-3"):
                            with ui.div():
                                ui.p("Average depth", class_="mb-0 text-muted small")
                                @render.express
                                def average_depth():
                                    d = earthquake_data()
                                    if d.shape[0] > 0:
                                        ui.p(f"{d.depth.mean():.1f} km", class_="mb-0 fs-4 fw-bold")
                            ui.div(ICONS["arrows"], class_="text-primary", style="font-size: 4rem;")

                                # Time Series Animation
                with ui.card(full_screen=True, style="min-height: 500px"):
                    with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                        with ui.div():
                            ui.h4("Earthquake activity over time", class_="mb-0")
                            ui.p("Animated visualization of earthquake trends", class_="mb-0 text-muted small")
                        with ui.div(class_="d-flex gap-2"):
                            ui.input_select("ts_aggregation", None, ["Daily", "Weekly", "Monthly"], selected="Weekly")
                            ui.input_select("ts_metric", None, ["Average Magnitude", "Max Magnitude", "Earthquake Count"], selected="Earthquake Count")
                    with ui.card_body(style="height: 100%"):
                        @render.ui
                        def time_series_chart():
                            gif_data = build_time_series_gif(earthquake_data(), input.ts_aggregation(), input.ts_metric())
                            if gif_data:
                                return ui_module.HTML(f'<img src="data:image/gif;base64,{gif_data}" style="max-width:100%; height:auto;" />')
                            return ui_module.HTML("<p>Not enough data for time series</p>")
          
                # Earthquake Map
                with ui.card(full_screen=True, style="min-height: 600px"):
                    with ui.card_header():
                        ui.h4("Earthquakes most often occur around tectonic plate boundaries", class_="mb-0", style="margin-bottom:0;margin-top:0;")
                    with ui.card_body(style="height: 100%"):
                        @render_plotly
                        def earthquake_map():
                            return build_earthquake_map(earthquake_data())
                
                # Outlier Earthquakes Infographic
                ui.h4("The Outliers", class_="mb-0", style="margin-bottom:0;")
                ui.p("The outlier earthquakes in the dataset", class_="mb-0 text-muted small", style="margin-top:-20px;margin-bottom:0;")
                build_outliers_infographic(earthquakes)

                # Monthly distribution chart
                with ui.card(full_screen=True, style="min-height: 500px"):
                    with ui.card_header():
                        with ui.div():
                            ui.h4("Summer months see the highest earthquake activity", class_="mb-0")
                            ui.p("July–September account for nearly half of all recorded earthquakes", class_="mb-0 text-muted small")
                    with ui.card_body(style="height: 100%"):
                        @render_plotly
                        def monthly_chart():
                            return build_monthly_chart(earthquake_data())
                        
                                  
                # Scatter plot: Magnitude vs Depth
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
                        return build_scatterplot(earthquake_data(), input.scatter_color())
                    
                # Heatmap and Scatterplot Matrix side by side
                with ui.div(style="display: flex; gap: 2rem; flex-wrap: wrap; justify-content: center; width: 100%;"):
                    with ui.card(full_screen=True, style="width: 440px; height: 560px; margin: 0 1rem 0 0;"):
                        with ui.card_header():
                            with ui.div():
                                ui.h4("Most events are small to medium magnitude with shallow depth", class_="mb-0")
                        with ui.card_body(style="height: 100%"):
                            @render_plotly
                            def mag_depth_heatmap():
                                return build_mag_depth_heatmap(earthquake_data())

                    with ui.card(full_screen=True, style="width: 440px; height: 560px;"):
                        with ui.card_header():
                            with ui.div():
                                ui.h4("Pairwise relations between magnitude, depth, and felt reports", class_="mb-0")
                        with ui.card_body(style="height: 100%"):
                            @render_plotly
                            def scatter_matrix_plot():
                                return build_scatterplot_matrix(earthquake_data())
                    

                

    with ui.nav_panel("Raw data"):
        with ui.card(full_screen=True):
            with ui.card_header(class_="d-flex justify-content-between align-items-center", style="position: relative;"):
                "Raw data (unfiltered)"
                ui.input_action_button("raw_toggle",
                    f"{len(raw_columns)} of {len(raw_columns)} columns ▾",
                    class_="btn btn-link text-primary p-0")

                with ui.panel_conditional("input.raw_toggle % 2 === 1"):
                    ui.div(
                        {"style": "position: absolute; right: 0; top: calc(100% + 0.5rem); z-index: 2000;",
                         "class": "shadow-sm border bg-white p-3 rounded-3"},
                        ui.div(
                            ui.input_action_button("raw_select_all_btn", "Select all", class_="btn btn-sm btn-outline-primary"),
                            ui.input_action_button("raw_clear_all_btn", "Clear", class_="btn btn-sm btn-outline-secondary"),
                            class_="d-flex gap-2 mb-2"),
                        ui.div(
                            ui.input_checkbox_group("raw_columns", None, choices=raw_columns, selected=raw_columns, inline=False),
                            style="max-height: 240px; width: 260px; overflow-y: auto;"))

            @render.data_frame
            def raw_table():
                cols = list(input.raw_columns() or raw_columns)
                return render.DataGrid(earthquakes[cols])

    with ui.nav_panel("Manual"):
        with ui.card(full_screen=False):
            ui.card_header("Download manual")
            ui.markdown("Get the PDF version of the manual below.")
            ui.tags.a("Download PDF", href="manual.pdf", download="manual.pdf",
                class_="btn btn-primary d-inline-flex align-items-center",
                style="width: fit-content; padding: 0.35rem 0.9rem;")

# Include custom styles
ui.include_css(app_dir / "styles.css")
