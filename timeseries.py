"""Animated time series visualization for earthquake data."""
import base64
import io
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

matplotlib.use("Agg")


def build_time_series_gif(data, aggregation, metric):
    """Build an animated GIF showing earthquake metrics over time.

    Args:
        data: DataFrame containing earthquake data with 'datetime' column
        aggregation: Time aggregation ('Daily', 'Weekly', 'Monthly')
        metric: Metric to display ('Average Magnitude', 'Max Magnitude',
                'Earthquake Count')

    Returns:
        Base64 encoded GIF string or None if no data
    """
    if data.empty:
        return None

    df = data.copy()
    df = df.sort_values("datetime")

    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M"}
    freq = freq_map.get(aggregation, "W")
    df.set_index("datetime", inplace=True)

    if metric == "Average Magnitude":
        series = df["magnitude"].resample(freq).mean()
        ylabel = "Avg Magnitude"
    elif metric == "Max Magnitude":
        series = df["magnitude"].resample(freq).max()
        ylabel = "Max Magnitude"
    else:
        series = df["magnitude"].resample(freq).count()
        ylabel = "Count"

    series = series.dropna()
    if len(series) < 2:
        return None

    dates = series.index.tolist()
    values = series.values.tolist()

    n_frames = min(len(dates), 20)
    step = max(1, len(dates) // n_frames)
    frame_indices = list(range(0, len(dates), step))
    if frame_indices[-1] != len(dates) - 1:
        frame_indices.append(len(dates) - 1)

    # Calculate bar width based on frequency
    if len(dates) > 1:
        time_delta = (dates[-1] - dates[0]) / len(dates)
        bar_width = time_delta * 0.8
    else:
        bar_width = 1

    frames = []
    fig, ax = plt.subplots(figsize=(10, 4), dpi=80)

    for idx in frame_indices:
        ax.clear()
        ax.bar(dates[: idx + 1], values[: idx + 1], color="#3b82f6", width=bar_width)

        if idx > 2:
            # Smooth moving average trend line that follows bar tops
            window = min(5, idx + 1)
            smoothed = np.convolve(values[: idx + 1], np.ones(window)/window, mode='same')
            ax.plot(dates[: idx + 1], smoothed, color="#ef4444", linewidth=2.5, linestyle='-')

        ax.set_xlim(dates[0], dates[-1])
        ax.set_ylim(0, max(values) * 1.1)
        ax.set_ylabel(ylabel)
        ax.set_xlabel("Date")
        ax.tick_params(axis="x", rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        frames.append(Image.open(buf).copy())
        buf.close()

    plt.close(fig)

    gif_buf = io.BytesIO()
    frames[0].save(
        gif_buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=150,
        loop=0,
    )
    gif_buf.seek(0)
    return base64.b64encode(gif_buf.read()).decode("utf-8")
