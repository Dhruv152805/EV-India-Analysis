import os
import glob
import shutil

# ✅ Update the paths based on your system output
EV_PATH = r"C:\Users\dkhan\.cache\kagglehub\datasets\urvishahir\electric-vehicle-specifications-dataset-2025\versions\1"
STATION_PATH = r"C:\Users\dkhan\.cache\kagglehub\datasets\saketpradhan\electric-vehicle-charging-stations-in-india\versions\1"

# Create a local 'data' folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# Copy EV dataset CSV files
for file in glob.glob(os.path.join(EV_PATH, "*.csv")):
    shutil.copy(file, "data/")
    print("✅ Copied:", os.path.basename(file))

# Copy charging station dataset CSV files
for file in glob.glob(os.path.join(STATION_PATH, "*.csv")):
    shutil.copy(file, "data/")
    print("✅ Copied:", os.path.basename(file))

print("\nAll CSVs successfully moved to your 'data/' folder.")
