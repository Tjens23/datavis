from pathlib import Path
import os

import pandas as pd
import kagglehub  # type: ignore

app_dir = Path(__file__).parent

# Download earthquakes dataset from Kaggle
path = kagglehub.dataset_download("shreyasur965/recent-earthquakes")
csv_file = os.path.join(path, "earthquakes.csv")
earthquakes = pd.read_csv(csv_file)

# --------------------------------------------------------
# Data processing
# --------------------------------------------------------

# Convert time to datetime (time is in milliseconds since epoch)
earthquakes['datetime'] = pd.to_datetime(earthquakes['time'], unit='ms')

# Make new columns for month and season
earthquakes['month'] = earthquakes['datetime'].dt.month
earthquakes['season'] = earthquakes['month'] % 12 // 3 + 1
season_mapping = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}
earthquakes['season'] = earthquakes['season'].map(season_mapping)

# Categoerize magnitude to small, medium, large in new column
earthquakes['magnitude_category'] = pd.cut(
    earthquakes['magnitude'],
    bins=[-float('inf'), 4.0, 6.0, float('inf')],
    labels=['Small', 'Medium', 'Large'])

# Categorize depth to shallow, intermediate, deep in new column
earthquakes['depth_category'] = pd.cut(
    earthquakes['depth'],
    bins=[-float('inf'), 70.0, 300.0, float('inf')],
    labels=['Shallow', 'Intermediate', 'Deep'])

# Filter out rows with missing values in key columns
earthquakes = earthquakes.dropna(subset=['magnitude', 'depth', 'latitude', 'longitude'])
earthquakes = earthquakes.reset_index(drop=True) # Reset index after filtering

# Delete duplicate rows based on 'id' column
earthquakes = earthquakes.drop_duplicates(subset=['id'])


# Remove unnecessary columns
columns_to_drop = ["type", "updated", "url", "detailUrl", "status", "code", "sources", "types", "rms", "geometryType", "placeOnly", "location", "locality", "postcode", "what3words", "locationDetails"]
earthquakes = earthquakes.drop(columns=columns_to_drop)
