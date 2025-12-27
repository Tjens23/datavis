"""Outliers infographic showing top earthquakes."""
import pandas as pd
from shiny import ui

from helpers import format_date, get_alert_color


def build_outliers_infographic(earthquakes):
    """Build the top earthquakes infographic UI components."""
    # Get the top earthquake outliers
    giant = earthquakes.nlargest(1, 'magnitude').reset_index(drop=True).iloc[0]
    top_depth = earthquakes.nlargest(1, 'depth').reset_index(drop=True).iloc[0]
    top_felt = earthquakes.nlargest(1, 'felt').reset_index(drop=True).iloc[0]

    # Build sidebar cards: first = deepest, last = highest felt
    sidebar_cards = []
    # First small card: deepest
    quake = top_depth
    color = "#eab308"
    quake_felt = int(quake['felt']) if not pd.isna(quake['felt']) else 0
    quake_alert = quake['alert'] if not pd.isna(quake['alert']) else "None"
    quake_tsunami = "⚠️ Yes" if quake['tsunami'] == 1 else "No"
    card_depth = ui.card(
        ui.div(
            ui.h3(f"📍 {quake['depth']:.0f} KM", class_="mb-0 fw-bold", style=f"color: {color};"),
            ui.span("Deepest", class_="badge fs-6", style=f"background-color: {color};"),
            class_="d-flex justify-content-between align-items-center", style="margin-bottom: 2px;"
        ),
        ui.p(quake['place'], class_="mb-0 small fw-semibold", style="line-height: 1.2;"),
        ui.div(
            ui.tags.small(f"📅 {format_date(quake['datetime'])}", class_="text-muted"),
            ui.tags.small(
                ui.span("M", class_="fw-bold", style="color: #ef4444;"),
                f" {quake['magnitude']:.1f}",
                class_="text-muted"
            ),
            class_="d-flex gap-3", style="line-height: 1.2;"
        ),
        ui.div(
            ui.tags.small(f"👥 {quake_felt:,} felt", class_="text-muted"),
            ui.tags.small("⚠️ ", class_="text-muted"),
            ui.span(str(quake_alert).upper(), class_="badge small", style=f"background-color: {get_alert_color(quake_alert)};"),
            ui.tags.small(f"🌊 {quake_tsunami}", class_="text-muted"),
            class_="d-flex gap-3 align-items-center", style="line-height: 1.2;"
        ),
        style="flex: 1;"
    )
    sidebar_cards.append(card_depth)

    # Last small card: highest felt
    quake = top_felt
    color = "#22c55e"
    quake_felt = int(quake['felt']) if not pd.isna(quake['felt']) else 0
    quake_alert = quake['alert'] if not pd.isna(quake['alert']) else "None"
    quake_tsunami = "⚠️ Yes" if quake['tsunami'] == 1 else "No"
    card_felt = ui.card(
        ui.div(
            ui.h3(f"👥 {quake_felt:,}", class_="mb-0 fw-bold", style=f"color: {color};"),
            ui.span("Most Felt", class_="badge fs-6", style=f"background-color: {color};"),
            class_="d-flex justify-content-between align-items-center", style="margin-bottom: 2px;"
        ),
        ui.p(quake['place'], class_="mb-0 small fw-semibold", style="line-height: 1.2;"),
        ui.div(
            ui.tags.small(f"📅 {format_date(quake['datetime'])}", class_="text-muted"),
            ui.tags.small(
                ui.span("M", class_="fw-bold", style="color: #ef4444;"),
                f" {quake['magnitude']:.1f}",
                class_="text-muted"
            ),
<<<<<<< HEAD
            ui.div(
                ui.tags.small(f"👥 {quake_felt:,} felt", class_="text-muted"),
                ui.tags.small("⚠️ ", class_="text-muted"),
                ui.span(str(quake_alert).upper(), class_="badge small", style=f"background-color: {get_alert_color(quake_alert)};"),
                ui.tags.small(f"🌊 {quake_tsunami}", class_="text-muted"),
                class_="d-flex gap-3 align-items-center", style="line-height: 1.2;"
            ),
            style="flex: 1;"
        )
        sidebar_cards.append(card)

=======
            class_="d-flex gap-3", style="line-height: 1.2;"
        ),
        ui.div(
            ui.tags.small(f"📍 {quake['depth']:.0f}km", class_="text-muted"),
            ui.tags.small("⚠️ ", class_="text-muted"),
            ui.span(str(quake_alert).upper(), class_="badge small", style=f"background-color: {get_alert_color(quake_alert)};"),
            ui.tags.small(f"🌊 {quake_tsunami}", class_="text-muted"),
            class_="d-flex gap-3 align-items-center", style="line-height: 1.2;"
        ),
        style="flex: 1;"
    )
    sidebar_cards.append(card_felt)
    
>>>>>>> f016f53 (heatmap distribution and scatterplot matrix)
    # Magnitude scale
    mag_percent = (giant['magnitude'] / 10) * 100
    mag_scale_html = f'''
        <div style="background: linear-gradient(to right, #22c55e, #eab308, #f97316, #ef4444);
                    height: 12px; border-radius: 6px; position: relative;">
            <div style="position: absolute; left: {mag_percent}%; top: -4px;
                        width: 20px; height: 20px; background: white; border: 3px solid #ef4444;
                        border-radius: 50%; transform: translateX(-50%);"></div>
        </div>
        <div class="d-flex justify-content-between mt-1">
            <small class="text-muted">1</small>
            <small class="text-muted">5</small>
            <small class="text-muted">10</small>
        </div>
    '''

    felt = giant['felt'] if not pd.isna(giant['felt']) else 0
    alert = giant['alert'] if not pd.isna(giant['alert']) else "None"
    tsunami = "⚠️ Yes" if giant['tsunami'] == 1 else "No"

    return ui.div(
        ui.div(
            # Main card - Biggest Earthquake (#1)
            ui.card(
                ui.div(
                    ui.div(
                        ui.p("🏆 THE LARGEST EARTHQUAKE", class_="text-muted small fw-bold mb-0", style="letter-spacing: 2px; font-size: 0.7rem;"),
                        ui.h2(f"MAGNITUDE {giant['magnitude']:.1f}", class_="fw-bold mb-0", style="color: #ef4444;"),
                    ),
                    ui.div(
                        ui.span("Strongest", class_="badge fs-6", style="background-color: #ef4444;"),
                        class_="text-end"
                    ),
                    class_="d-flex justify-content-between align-items-start mb-1"
                ),
                ui.p(giant['place'], class_="mb-1 small fw-semibold"),
                ui.div(
                    ui.div(
                        ui.p("📅 Date", class_="text-muted small mb-0"),
                        ui.p(format_date(giant['datetime']), class_="small fw-semibold mb-0"),
                        class_="col-4"
                    ),
                    ui.div(
                        ui.p("📍 Depth", class_="text-muted small mb-0"),
                        ui.p(f"{giant['depth']:.0f}km", class_="small fw-semibold mb-0"),
                        class_="col-4"
                    ),
                    ui.div(
                        ui.p("🌍 Region", class_="text-muted small mb-0"),
                        ui.p(f"{giant['country']}", class_="small fw-semibold mb-0"),
                        class_="col-4"
                    ),
                    class_="row mb-1"
                ),
                ui.div(
                    ui.div(
                        ui.p("👥 Felt Reports", class_="text-muted small mb-0"),
                        ui.p(f"{int(felt):,} people", class_="small fw-semibold mb-0"),
                        class_="col-4"
                    ),
                    ui.div(
                        ui.p("⚠️ Alert Level", class_="text-muted small mb-0"),
                        ui.span(str(alert).upper(), class_="badge small", style=f"background-color: {get_alert_color(alert)};"),
                        class_="col-4"
                    ),
                    ui.div(
                        ui.p("🌊 Tsunami", class_="text-muted small mb-0"),
                        ui.p(tsunami, class_="small fw-semibold mb-0"),
                        class_="col-4"
                    ),
                    class_="row mb-1"
                ),
                ui.p("Magnitude Scale", class_="text-muted small mb-1"),
                ui.HTML(mag_scale_html),
                style="width: 100%;"
            ),
            class_="col-lg-8",
            style="display: flex;"
        ),
        ui.div(
            ui.div(*sidebar_cards, style="display: flex; flex-direction: column; gap: 0.5rem;"),
            class_="col-lg-4"
        ),
        class_="row g-3"
    )
