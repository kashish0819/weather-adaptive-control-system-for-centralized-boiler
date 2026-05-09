import sqlite3
from datetime import datetime
import random

conn = sqlite3.connect("boiler_data.db")
cursor = conn.cursor()

for i in range(300):

    weather = random.randint(5, 35)
    water = random.randint(30, 80)
    flow = random.randint(0, 5)

    if weather < 20:
        status = "ON"
    else:
        status = "OFF"

    cursor.execute("""
        INSERT INTO logs (weather_temp, water_temp, flow_rate, boiler_status, time)
        VALUES (?, ?, ?, ?, ?)
    """, (weather, water, flow, status, datetime.now()))

conn.commit()
conn.close()

print("Dummy data inserted")
