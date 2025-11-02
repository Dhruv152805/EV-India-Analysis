import kagglehub # type: ignore

# --- Download EV Specs dataset ---
ev_path = kagglehub.dataset_download("urvishahir/electric-vehicle-specifications-dataset-2025")
print("✅ EV Specs dataset downloaded at:", ev_path)

# --- Download EV Charging Stations dataset ---
station_path = kagglehub.dataset_download("saketpradhan/electric-vehicle-charging-stations-in-india")
print("✅ Charging Stations dataset downloaded at:", station_path)
