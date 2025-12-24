import faicons as fa
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import io
import base64
from PIL import Image

# Load data and compute static values
from shared import app_dir, earthquakes
from map import build_earthquake_map
from outliers import build_outliers_infographic
from seasonal import build_monthly_chart
from shinywidgets import render_plotly
from shinywidgets import render_widget

from shiny import reactive, render
from shiny import ui as ui_module
from shiny.express import input, ui
from shiny.ui import showcase_left_center

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
                        data = earthquake_data()
                        color_var = input.scatter_color()
                        
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
                
                with ui.card(full_screen=True, style="min-height: 600px"):
                    with ui.card_header():
                        ui.h4("Earthquakes most often occur around tectonic plate boundaries", class_="mb-0")
                        ui.p("", class_="mb-0 text-muted small")
                    with ui.card_body(style="height: 100%"):
                        @render_plotly
                        def earthquake_map():
                            return build_earthquake_map(earthquake_data())
                
                with ui.card(full_screen=True, style="min-height: 500px"):
                    with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                        ui.h4("Earthquake Magnitude Over Time", class_="mb-0")
                        with ui.popover(title="Chart settings", placement="top"):
                            ICONS["ellipsis"]
                            ui.input_radio_buttons(
                                "time_aggregation",
                                "Aggregation",
                                ["Daily", "Weekly", "Monthly"],
                                selected="Weekly",
                                inline=True,
                            )
                            ui.input_radio_buttons(
                                "time_metric",
                                "Metric",
                                ["Average Magnitude", "Max Magnitude", "Earthquake Count"],
                                selected="Average Magnitude",
                                inline=True,
                            )
                    
                    @render.ui
                    def time_series_chart():
                        data = earthquake_data().copy()
                        
                        if len(data) == 0:
                            return ui_module.HTML("<p>No data available</p>")
                        
                        data = data.sort_values('datetime')
                        
                        agg = input.time_aggregation()
                        metric = input.time_metric()
                        
                        if agg == "Daily":
                            data['period'] = data['datetime'].dt.date
                        elif agg == "Weekly":
                            data['period'] = data['datetime'].dt.to_period('W').apply(lambda x: x.start_time.date())
                        else:
                            data['period'] = data['datetime'].dt.to_period('M').apply(lambda x: x.start_time.date())
                        
                        if metric == "Average Magnitude":
                            grouped = data.groupby('period')['magnitude'].mean().reset_index()
                            grouped.columns = ['period', 'value']
                            y_label = "Average Magnitude"
                        elif metric == "Max Magnitude":
                            grouped = data.groupby('period')['magnitude'].max().reset_index()
                            grouped.columns = ['period', 'value']
                            y_label = "Max Magnitude"
                        else:
                            grouped = data.groupby('period').size().reset_index()
                            grouped.columns = ['period', 'value']
                            y_label = "Number of Earthquakes"
                        
                        grouped['period'] = pd.to_datetime(grouped['period'])
                        grouped = grouped.sort_values('period').reset_index(drop=True)
                        
                        # Beregn trendlinje
                        window = max(3, len(grouped) // 10)
                        grouped['trend'] = grouped['value'].rolling(window=window, min_periods=1).mean()
                        
                        # Beregn bar bredde
                        if len(grouped) > 1:
                            bar_width = (grouped['period'].iloc[1] - grouped['period'].iloc[0]) * 0.8
                        else:
                            bar_width = pd.Timedelta(days=1)
                        
                        # Kun 20 frames for hurtig loading
                        total_frames = min(len(grouped), 20)
                        step = max(1, len(grouped) // total_frames)
                        frame_indices = [i * step for i in range(total_frames)]
                        frame_indices.append(len(grouped) - 1)
                        
                        # Pre-render alle frames som PIL images
                        frames_images = []
                        
                        x_min = grouped['period'].min() - pd.Timedelta(days=5)
                        x_max = grouped['period'].max() + pd.Timedelta(days=5)
                        y_max = grouped['value'].max() * 1.15
                        
                        for frame_idx in frame_indices:
                            fig, ax = plt.subplots(figsize=(10, 4), dpi=80)
                            
                            idx = min(frame_idx + 1, len(grouped))
                            frame_data = grouped.iloc[:idx]
                            
                            ax.bar(frame_data['period'], frame_data['value'], 
                                   color='steelblue', alpha=0.7, width=bar_width)
                            ax.plot(frame_data['period'], frame_data['trend'], 
                                    color='red', linewidth=2)
                            
                            ax.set_xlim(x_min, x_max)
                            ax.set_ylim(0, y_max)
                            ax.set_xlabel('Time', fontsize=10)
                            ax.set_ylabel(y_label, fontsize=10)
                            ax.set_title(f'{y_label} ({agg})', fontsize=12, fontweight='bold')
                            ax.grid(True, alpha=0.3)
                            fig.autofmt_xdate()
                            plt.tight_layout()
                            
                            # Gem til buffer
                            buf = io.BytesIO()
                            fig.savefig(buf, format='png', dpi=80)
                            buf.seek(0)
                            frames_images.append(Image.open(buf).copy())
                            buf.close()
                            plt.close(fig)
                        
                        # Gem som GIF direkte med PIL
                        gif_buffer = io.BytesIO()
                        frames_images[0].save(
                            gif_buffer,
                            format='GIF',
                            save_all=True,
                            append_images=frames_images[1:],
                            duration=120,
                            loop=0,
                            optimize=True
                        )
                        gif_buffer.seek(0)
                        
                        gif_base64 = base64.b64encode(gif_buffer.getvalue()).decode('utf-8')
                        html = f'<img src="data:image/gif;base64,{gif_base64}" style="max-width:100%; height:auto;" />'
                        
                        return ui_module.HTML(html)
                
                # Top Earthquakes Infographic
                ui.h4("The outliers", class_="mb-0")
                ui.p("The strongest earthquakes in the dataset", class_="mb-0 text-muted small")
                build_outliers_infographic(earthquakes)

                #Monthly/Seasonal distribution chart
                with ui.card(full_screen=True, style="min-height: 500px"):
                    with ui.card_header():
                        with ui.div():
                            ui.h4("Summer months see the highest earthquake activity", class_="mb-0")
                            ui.p("July–September account for nearly half of all recorded earthquakes", class_="mb-0 text-muted small")
                    with ui.card_body(style="height: 100%"):
                        @render_plotly
                        def monthly_chart():
                            return build_monthly_chart(earthquake_data())

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
