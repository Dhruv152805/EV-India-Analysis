# chatbot_backend.py

import pandas as pd
import joblib
import numpy as np
from geopy.distance import geodesic

# Load model and scaler
model_path = r"C:\Users\dkhan\Documents\gen ai ev vehicle\models\gradient_boosting_ev.pkl"
scaler_path = r"C:\Users\dkhan\Documents\gen ai ev vehicle\models\scaler.pkl"

gb_model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Load station data
stations = pd.read_csv(r"C:\Users\dkhan\Documents\gen ai ev vehicle\data\station_cleaned.csv")

# --- Function 1: Predict EV Range ---
def predict_range(battery_capacity, efficiency):
    scaled_input = scaler.transform([[battery_capacity, efficiency]])
    predicted_range = gb_model.predict(scaled_input)[0]
    return round(predicted_range, 2)

# --- Function 2: Estimate available range based on battery percentage ---
def estimate_current_range(full_range_km, current_battery_percent):
    available_range = (full_range_km * current_battery_percent) / 100
    return round(available_range, 2)

# --- Function 3: Find nearest charging stations ---
def find_nearest_stations(current_lat, current_lon, max_distance_km=50):
    stations['distance_km'] = stations.apply(
        lambda row: geodesic((current_lat, current_lon), (row['lattitude'], row['longitude'])).km, axis=1)
    
    nearby = stations.sort_values(by='distance_km').head(5)
    return nearby[['name', 'city', 'address', 'distance_km']]

# --- Function 4: Find reachable stations within available range ---
def reachable_stations(current_lat, current_lon, available_range_km):
    stations['distance_km'] = stations.apply(
        lambda row: geodesic((current_lat, current_lon), (row['lattitude'], row['longitude'])).km, axis=1)
    
    reachable = stations[stations['distance_km'] <= available_range_km]
    return reachable[['name', 'city', 'address', 'distance_km']].sort_values(by='distance_km')



# Note: example/test code removed so this module can be safely imported by the
# Streamlit app. Use the exported functions from other modules (predict_range,
# estimate_current_range, find_nearest_stations, reachable_stations).
