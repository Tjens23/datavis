import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from PIL import Image


def build_time_series_gif(data, aggregation, metric):
    """Build an animated GIF time series chart."""
    if len(data) == 0:
        return None
    
    data = data.copy()
    data = data.sort_values('datetime')
    
    if aggregation == "Daily":
        data['period'] = data['datetime'].dt.date
    elif aggregation == "Weekly":
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
    
    # Calculate trend line
    window = max(3, len(grouped) // 10)
    grouped['trend'] = grouped['value'].rolling(window=window, min_periods=1).mean()
    
    # Calculate bar width
    if len(grouped) > 1:
        bar_width = (grouped['period'].iloc[1] - grouped['period'].iloc[0]) * 0.8
    else:
        bar_width = pd.Timedelta(days=1)
    
    # Only 20 frames for fast loading
    total_frames = min(len(grouped), 20)
    step = max(1, len(grouped) // total_frames)
    frame_indices = [i * step for i in range(total_frames)]
    frame_indices.append(len(grouped) - 1)
    
    # Pre-render all frames as PIL images
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
        ax.set_title(f'{y_label} ({aggregation})', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=80)
        buf.seek(0)
        frames_images.append(Image.open(buf).copy())
        buf.close()
        plt.close(fig)
    
    # Save as GIF with PIL
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
    return gif_base64
