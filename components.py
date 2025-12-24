"""Reusable UI components for the dashboard."""
import faicons as fa
from shiny.express import ui


ICONS = {
    "earth": fa.icon_svg("earth-americas"),
    "gauge": fa.icon_svg("gauge-high"),
    "arrows": fa.icon_svg("arrows-down-to-people"),
    "ellipsis": fa.icon_svg("ellipsis"),
    "chevron": fa.icon_svg("chevron-down"),
}


def stat_card(label: str, value: str, icon_key: str):
    """Create a statistics card with label, value, and icon."""
    with ui.card(class_="px-3 py-2"):
        with ui.div(class_="d-flex align-items-center justify-content-between gap-3"):
            with ui.div():
                ui.p(label, class_="mb-0 text-muted small")
                ui.p(value, class_="mb-0 fs-4 fw-bold")
            ui.div(ICONS[icon_key], class_="text-primary", style="font-size: 4rem;")
