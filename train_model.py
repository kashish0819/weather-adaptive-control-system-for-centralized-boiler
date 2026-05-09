import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle

# Sample training data
data = {
    "weather_temp": [20, 25, 30, 15, 10, 35, 40, 18],
    "water_temp":   [30, 40, 50, 25, 20, 60, 70, 28],
    "flow_rate":    [1, 2, 3, 1, 1, 4, 5, 2],
    "boiler_status": [1, 1, 0, 1, 1, 0, 0, 1]
}

df = pd.DataFrame(data)

X = df[["weather_temp", "water_temp", "flow_rate"]]
y = df["boiler_status"]

model = LogisticRegression()
model.fit(X, y)

# Save model
pickle.dump(model, open("boiler_model.pkl", "wb"))

print("Model trained and saved successfully!")
