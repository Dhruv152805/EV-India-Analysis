import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

from week_3 import predict_range, estimate_current_range, reachable_stations
from week_3 import stations as station_df

# App Title
st.title("EV Range & Charging Assistant Chatbot")
st.markdown("Interactively pick your current location (and optional destination) on the map, choose a vehicle model, and get range + charging station guidance.")


### Vehicle selection and battery
ev_data = None
try:
    ev_data = pd.read_csv(r"C:\Users\dkhan\Documents\gen ai ev vehicle\data\ev_cleaned.csv")
except Exception:
    # If dataset isn't available, we'll fall back to manual inputs
    ev_data = None

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Vehicle & Battery")
    model_options = []
    if ev_data is not None and 'model' in ev_data.columns:
        # dedupe and sort
        model_options = sorted(ev_data['model'].dropna().unique().tolist())
    if model_options:
        vehicle_model = st.selectbox("Choose vehicle model (from dataset)", options=["-- Custom --"] + model_options)
    else:
        vehicle_model = "-- Custom --"

    if vehicle_model != "-- Custom --" and ev_data is not None:
        # take median values for battery and efficiency if multiple entries
        sel = ev_data[ev_data['model'] == vehicle_model]
        if not sel.empty:
            battery_capacity = float(sel['battery_capacity_kWh'].median())
            efficiency = float(sel['efficiency_wh_per_km'].median())
            st.markdown(f"**Selected:** {vehicle_model} — estimated battery: **{battery_capacity} kWh**, efficiency: **{efficiency} Wh/km**")
        else:
            vehicle_model = "-- Custom --"

    if vehicle_model == "-- Custom --":
        battery_capacity = st.number_input("Battery Capacity (kWh)", min_value=10.0, max_value=200.0, value=50.0)
        efficiency = st.number_input("Efficiency (Wh/km)", min_value=50.0, max_value=300.0, value=150.0)

    battery_percent = st.slider("Current Charge (%)", 0, 100, 80)

with col2:
    st.subheader("Trip & Driving")
    avg_speed = st.number_input("Assumed average speed (km/h)", min_value=10, max_value=150, value=50)
    route_buffer_km = st.number_input("Station search buffer from route (km)", min_value=1, max_value=100, value=10)


### Interactive map for location (and optional destination)
st.subheader("Pick current location on map (click) — India")
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
folium.TileLayer('OpenStreetMap').add_to(m)
folium.LatLngPopup().add_to(m)

map_data = st_folium(m, width=800, height=450)

clicked = map_data.get('last_clicked') if map_data else None
start_lat = None
start_lon = None
if clicked:
    start_lat = clicked.get('lat')
    start_lon = clicked.get('lng')
    st.markdown(f"**Selected start:** {start_lat:.6f}, {start_lon:.6f}")
else:
    st.info("Click on the map to select your current location. You can also use the fallback inputs below.")
    start_lat = st.number_input("Fallback: Current Latitude", value=28.6139)
    start_lon = st.number_input("Fallback: Current Longitude", value=77.2090)

dest_choice = st.checkbox("Select destination on map (to find stations along route)")
end_lat = None
end_lon = None
if dest_choice:
    st.caption("After checking this, click a second point on the same map to pick destination.")
    dest_clicked = map_data.get('last_clicked') if map_data else None
    # If user clicked twice, streamlit_folium stores last click only — provide a small helper to accept manual input
    st.write("If the map click didn't capture destination, provide destination coords below.")
    end_lat = st.number_input("Destination Latitude", value=28.7041)
    end_lon = st.number_input("Destination Longitude", value=77.1025)

### Run analysis
if st.button("🔍 Get EV Insights"):
    # Calculate predicted full range and available range
    predicted_range = predict_range(battery_capacity, efficiency)
    available_range = estimate_current_range(predicted_range, battery_percent)

    st.metric("Predicted Full Range (km)", f"{predicted_range:.2f}")
    st.metric("Estimated Range with Current Charge (km)", f"{available_range:.2f}")

    st.divider()

    # Nearest stations to current location
    st.subheader("🔌 Nearest EV Charging Stations (closest to you)")
    try:
        station_df['distance_km'] = station_df.apply(lambda row: geodesic((start_lat, start_lon), (row['lattitude'], row['longitude'])).km, axis=1)
        nearest = station_df.sort_values(by='distance_km').head(10)[['name', 'city', 'address', 'distance_km']]
        st.dataframe(nearest.reset_index(drop=True))
    except Exception as e:
        st.error(f"Could not compute nearest stations: {e}")

    st.divider()

    # Stations reachable within available range
    st.subheader("🚗 Stations reachable with current charge")
    try:
        reachable = station_df[station_df['distance_km'] <= available_range].sort_values(by='distance_km')
        if reachable.empty:
            st.info("No stations within your available range.")
        else:
            st.dataframe(reachable[['name', 'city', 'address', 'distance_km']].reset_index(drop=True))
    except Exception as e:
        st.error(f"Error finding reachable stations: {e}")

    # Stations along route (if destination provided)
    if dest_choice and end_lat is not None and end_lon is not None:
        st.divider()
        st.subheader("🗺️ Stations along the route (buffer method)")
        try:
            start = (start_lat, start_lon)
            end = (end_lat, end_lon)
            route_length = geodesic(start, end).km

            def is_near_route(station_lat, station_lon, s=start, e=end, buf=route_buffer_km):
                # near-route if distance(start,station) + distance(station,end) <= route_length + 2*buf
                d1 = geodesic(s, (station_lat, station_lon)).km
                d2 = geodesic((station_lat, station_lon), e).km
                return (d1 + d2) <= (route_length + 2 * buf)

            station_df['on_route'] = station_df.apply(lambda r: is_near_route(r['lattitude'], r['longitude']), axis=1)
            on_route = station_df[station_df['on_route']].copy()
            on_route['dist_from_start_km'] = on_route.apply(lambda r: geodesic(start, (r['lattitude'], r['longitude'])).km, axis=1)
            on_route = on_route.sort_values(by='dist_from_start_km')
            if on_route.empty:
                st.info("No charging stations found within the buffer of the route.")
            else:
                st.dataframe(on_route[['name', 'city', 'address', 'dist_from_start_km']].reset_index(drop=True))
        except Exception as e:
            st.error(f"Error computing stations along route: {e}")

    # Driving time estimate before recharge required
    st.divider()
    st.subheader("⏱️ Estimated driving time before recharge")
    if avg_speed > 0:
        hours = available_range / float(avg_speed)
        hrs = int(hours)
        mins = int((hours - hrs) * 60)
        st.write(f"With an average speed of {avg_speed} km/h you can drive about **{hours:.2f} hours** (~{hrs}h {mins}m) before recharge is required.")
    else:
        st.write("Enter a positive average speed to estimate driving time.")

    st.success(" Analysis Complete! Ready for your next trip!")


# Footer
st.markdown("---")
st.caption(" Developed by Dhruv | EV Smart Assistant ")
