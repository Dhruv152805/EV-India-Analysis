import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio

pd.set_option('display.max_columns', None)

pio.renderers.default = "browser"

ev = pd.read_csv("C:/Users/dkhan/Documents/gen ai ev vehicle/data/electric_vehicles_spec_2025.csv.csv")
stations = pd.read_csv("C:/Users/dkhan/Documents/gen ai ev vehicle/data/ev-charging-stations-india.csv")

# Keep only required columns
ev_required_cols = ['brand', 'model', 'battery_capacity_kWh', 'efficiency_wh_per_km', 'range_km']
ev = ev[ev_required_cols]

station_required_cols = ['name', 'city', 'address', 'lattitude', 'longitude', 'type']
stations = stations[station_required_cols]

print("Filtered EV DataFrame:")
print(ev.head())
print("\nFiltered Charging Station DataFrame:")
print(stations.head())

# -------- CLEANING PROCESS --------
print("\nBefore Cleaning:")
print("EV dataset shape:", ev.shape)
print("Charging Station dataset shape:", stations.shape)

# Handle missing values
ev['battery_capacity_kWh'].fillna(ev['battery_capacity_kWh'].mean(), inplace=True)
ev['efficiency_wh_per_km'].fillna(ev['efficiency_wh_per_km'].mean(), inplace=True)
ev['range_km'].fillna(ev['range_km'].mean(), inplace=True)

ev.dropna(subset=['brand', 'model'], inplace=True)
stations.dropna(subset=['lattitude', 'longitude', 'address'], inplace=True)

# Convert datatypes
stations['lattitude'] = pd.to_numeric(stations['lattitude'], errors='coerce')
stations['longitude'] = pd.to_numeric(stations['longitude'], errors='coerce')
stations.dropna(subset=['lattitude', 'longitude'], inplace=True)

# Remove duplicates
ev.drop_duplicates(inplace=True)
stations.drop_duplicates(inplace=True)

# Save cleaned datasets
ev.to_csv("C:/Users/dkhan/Documents/gen ai ev vehicle/data/ev_cleaned.csv", index=False)
stations.to_csv("C:/Users/dkhan/Documents/gen ai ev vehicle/data/station_cleaned.csv", index=False)

print("\nData Cleaning Completed Successfully!")
print("Cleaned EV dataset shape:", ev.shape)
print("Cleaned Charging Station dataset shape:", stations.shape)

print(ev.head())
print(stations.head())
print(ev.info())
print(stations.info())
print(ev.describe())
print(stations.describe())
print(ev.isnull().sum())
print(stations.isnull().sum())

plt.figure(figsize=(14, 4))

plt.subplot(1, 3, 1)
sns.histplot(ev['battery_capacity_kWh'], bins=20, kde=True)
plt.title('Battery Capacity Distribution (kWh)')

plt.subplot(1, 3, 2)
sns.histplot(ev['range_km'], bins=20, kde=True)
plt.title('Range Distribution (km)')

plt.subplot(1, 3, 3)
sns.histplot(ev['efficiency_wh_per_km'], bins=20, kde=True)
plt.title('Efficiency Distribution (Wh/km)')

plt.tight_layout()
plt.show()

# ---- Correlation Heatmap ----
plt.figure(figsize=(5, 4))
sns.heatmap(ev.corr(numeric_only=True), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Between EV Features")
plt.show()

print("\nCharging Station Types:")
print(stations['type'].value_counts())

# ---- City-wise Top 20 distribution ----
plt.figure(figsize=(10,6))

# Get top 20 cities
top_cities = stations['city'].value_counts().nlargest(20)

# Plot as horizontal bar chart
sns.barplot(x=top_cities.values, y=top_cities.index, palette="viridis")

plt.title("Top 20 Cities with Most Charging Stations", fontsize=14)
plt.xlabel("Number of Charging Stations")
plt.ylabel("City")
plt.tight_layout()
plt.show()

# Keep only stations located within India's valid latitude & longitude range
stations = stations[
    (stations['lattitude'].between(6, 38)) &
    (stations['longitude'].between(68, 98))
]

fig = px.scatter_mapbox(
    stations,
    lat='lattitude',  
    lon='longitude',
    hover_name='name',
    hover_data=['city', 'address'],
    zoom=5,
    height=650,
    color_discrete_sequence=['teal']
)

fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_center={"lat": 22.5, "lon": 78.9},
    title="EV Charging Stations Across India"
)
# Make map more interactive and crisp
fig.update_layout(
    dragmode="pan",
    margin=dict(l=0, r=0, t=60, b=0)
)

fig.show(config={
    "scrollZoom": True,
    "displaylogo": False
})

state_counts = stations['city'].value_counts().head(10)
print(state_counts)

