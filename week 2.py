import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib  # for saving model

# 1️⃣ Load Cleaned Data
ev = pd.read_csv("C:/Users/dkhan/Documents/gen ai ev vehicle/data/ev_cleaned.csv")

# 2️⃣ Select Features and Target
X = ev[['battery_capacity_kWh', 'efficiency_wh_per_km']]
y = ev['range_km']

# 3️⃣ Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# 4️⃣ Scale Data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5️⃣ Train Gradient Boosting Model
gb_model = GradientBoostingRegressor(random_state=42)
gb_model.fit(X_train_scaled, y_train)

# 6️⃣ Predictions
y_pred = gb_model.predict(X_test_scaled)

# 7️⃣ Evaluation Metrics
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = sqrt(mean_squared_error(y_test, y_pred))

print(f"\nModel Performance:")
print(f"R² Score: {r2:.4f}")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

# 8️⃣ Visualization: Actual vs Predicted
plt.figure(figsize=(7,5))
plt.scatter(y_test, y_pred, color='teal', alpha=0.7)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.title("Actual vs Predicted EV Range (Gradient Boosting)")
plt.xlabel("Actual Range (km)")
plt.ylabel("Predicted Range (km)")
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

# step1_save_model.py
import os
import joblib

MODEL_DIR = r"C:\Users\dkhan\Documents\gen ai ev vehicle\models"
os.makedirs(MODEL_DIR, exist_ok=True)

print("Model directory ready:", MODEL_DIR)

os.makedirs(r"C:\Users\dkhan\Documents\gen ai ev vehicle\models", exist_ok=True)
joblib.dump(gb_model, r"C:\Users\dkhan\Documents\gen ai ev vehicle\models\gradient_boosting_ev.pkl")
joblib.dump(scaler, r"C:\Users\dkhan\Documents\gen ai ev vehicle\models\scaler.pkl")
print("Saved model and scaler.")
