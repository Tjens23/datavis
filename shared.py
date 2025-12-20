from pathlib import Path
import os

import pandas as pd
import kagglehub  # type: ignore

app_dir = Path(__file__).parent

# Download earthquakes dataset from Kaggle
path = kagglehub.dataset_download("shreyasur965/recent-earthquakes")
csv_file = os.path.join(path, "earthquakes.csv")
earthquakes = pd.read_csv(csv_file)

# Convert time to datetime (time is in milliseconds since epoch)
earthquakes['datetime'] = pd.to_datetime(earthquakes['time'], unit='ms')
