import pandas as pd
import json
import urllib.request

# Cache tectonic plates data
_tectonic_plates_cache = None


def get_tectonic_plates():
    """Fetch tectonic plate boundaries GeoJSON (cached)."""
    global _tectonic_plates_cache
    if _tectonic_plates_cache is None:
        # Using the PB2002 plate boundaries dataset from GitHub
        url = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json"
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                _tectonic_plates_cache = json.loads(response.read().decode())
        except Exception as e:
            print(f"Could not fetch tectonic plates: {e}")
            _tectonic_plates_cache = {"type": "FeatureCollection", "features": []}
    return _tectonic_plates_cache


def get_alert_color(alert):
    """Return a color based on alert level."""
    colors = {"green": "#22c55e", "yellow": "#eab308", "orange": "#f97316", "red": "#ef4444"}
    return colors.get(str(alert).lower(), "#6b7280")


def format_date(dt):
    """Format a datetime object to a readable string."""
    if pd.isna(dt):
        return "Unknown"
    return dt.strftime("%B %d, %Y")

