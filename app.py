import faicons as fa
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
import numpy as np

# Load data and compute static values
from shared import app_dir, earthquakes
from shinywidgets import render_plotly
from shinywidgets import render_widget

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
                    ["none", "magType", "net"],
                    inline=True,
                )

        @render.ui
        def scatterplot():
            import io
            import base64
            from shiny import ui as ui_module
            
            data = earthquake_data()
            color_var = input.scatter_color()
            
            if len(data) == 0:
                return ui_module.HTML("<p>No data to display</p>")
            
            # Sort data by datetime for animation
            data = data.sort_values('datetime').reset_index(drop=True)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Set up the plot limits and labels
            ax.set_xlim(data['magnitude'].min() - 0.5, data['magnitude'].max() + 0.5)
            ax.set_ylim(data['depth'].min() - 10, data['depth'].max() + 10)
            ax.set_xlabel('Magnitude', fontsize=12)
            ax.set_ylabel('Depth (km)', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Prepare color mapping
            if color_var != "none" and color_var in data.columns:
                unique_vals = data[color_var].unique()
                colors = plt.cm.viridis(np.linspace(0, 1, len(unique_vals)))
                color_map = dict(zip(unique_vals, colors))
                point_colors = [color_map[val] for val in data[color_var]]
                
                # Add legend
                for i, val in enumerate(unique_vals):
                    ax.scatter([], [], c=[colors[i]], label=str(val), s=50)
                ax.legend(loc='upper right', fontsize=8)
            else:
                point_colors = ['#1f77b4'] * len(data)
            
            # Initialize scatter plot
            scatter = ax.scatter([], [], alpha=0.6, s=50)
            time_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                              fontsize=10, verticalalignment='top',
                              bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # Animation function
            def animate(frame):
                # Show earthquakes up to this frame
                idx = min(frame * 5, len(data))  # Show 5 points per frame
                current_data = data.iloc[:idx]
                
                if len(current_data) > 0:
                    scatter.set_offsets(np.c_[current_data['magnitude'], current_data['depth']])
                    scatter.set_color([point_colors[i] for i in range(idx)])
                    
                    # Update time text
                    latest_time = current_data['datetime'].iloc[-1]
                    time_text.set_text(f'Up to: {latest_time.strftime("%Y-%m-%d %H:%M")}')
                
                return scatter, time_text
            
            # Create animation
            frames = min(len(data) // 5 + 1, 100)  # Limit to 100 frames max
            anim = animation.FuncAnimation(fig, animate, frames=frames,
                                         interval=100, blit=True, repeat=True)
            
            plt.tight_layout()
            
            # Save animation as GIF to a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.gif') as tmp:
                tmp_path = tmp.name
            
            anim.save(tmp_path, writer='pillow', fps=10, dpi=100)
            plt.close(fig)
            
            # Read the GIF file and encode as base64
            with open(tmp_path, 'rb') as f:
                gif_data = f.read()
            
            # Clean up temp file
            import os
            os.unlink(tmp_path)
            
            # Encode as base64 and embed in img tag
            gif_base64 = base64.b64encode(gif_data).decode('utf-8')
            html = f'<img src="data:image/gif;base64,{gif_base64}" style="max-width:100%; height:auto;" />'
            
            return ui_module.HTML(html)

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
