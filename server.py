from flask import Flask, request, jsonify, render_template
import sqlite3
import pickle
from datetime import datetime
import requests
from wether import get_weather

def get_weather():
    API_KEY = "0ad599cd40f18c7ae785f7563b0f5d5e"
    CITY = "Jammu"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data["main"]["temp"]

app = Flask(__name__)

# =============================
# GLOBAL VARIABLES (for dashboard)
# =============================
weather_temp = 0
water_temp = 0
flow_rate = 0
boiler_status = "OFF"

# =============================
# LOAD ML MODEL
# =============================
model = pickle.load(open("boiler_model.pkl", "rb"))

# =============================
# CREATE DATABASE
# =============================
def init_db():
    conn = sqlite3.connect("boiler_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weather_temp REAL,
            water_temp REAL,
            flow_rate REAL,
            prediction TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


# =============================
# HOME ROUTE (Dashboard Page)
# =============================
@app.route("/")
def home():
    return render_template("index.html")

# =============================
# API TO SEND LIVE DATA TO DASHBOARD
# =============================

    # Always update weather before sending
@app.route("/data")
def get_data():
    global weather_temp

    weather_temp = get_weather()
    return jsonify({
        "weather": weather_temp,
        "water": water_temp,
        "flow": flow_rate,
        "status": boiler_status
    })

# ===== SMART BOILER LOGIC =====

# Dynamic target temperature
target_temp = 60 - (weather_temp * 0.5)

# Safety limit
if water_temp > 80:
    boiler_status = "OFF"

else:
    if boiler_status == "OFF" and water_temp < (target_temp - 3):
        boiler_status = "ON"

    elif boiler_status == "ON" and water_temp > (target_temp + 3):
        boiler_status = "OFF"


# =============================
# UPDATE ROUTE (ESP32 SENDS DATA)
# =============================
@app.route("/update", methods=["POST"])
def update():
    global weather_temp, water_temp, flow_rate, boiler_status

    data = request.get_json()

    # Get values from ESP32
    water_temp = float(data["water_temp"])
    flow_rate = float(data["flow_rate"])

    print("Flow received:", flow_rate)

     # Update weather
    weather_temp = get_weather()

    # ML Prediction
    prediction = model.predict([[weather_temp, water_temp, flow_rate]])[0]

    if prediction == 1:
        boiler_status = "ON"
    else:
        boiler_status = "OFF"

    # Save to database
    conn = sqlite3.connect("boiler_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (weather_temp, water_temp, flow_rate, prediction, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (weather_temp, water_temp, flow_rate, boiler_status,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    return jsonify({"boiler": boiler_status})

# =============================
# RUN SERVER
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
