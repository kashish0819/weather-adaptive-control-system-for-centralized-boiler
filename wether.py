import requests

API_KEY = "0ad599cd40f18c7ae785f7563b0f5d5e"
CITY = "ahmedabad"

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print("Error:", data)
        return None

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    weather_condition = data["weather"][0]["description"]

    print("Weather Data:")
    print("Temperature:", temperature, "°C")
    print("Humidity:", humidity, "%")
    print("Condition:", weather_condition)

    return temperature

if __name__ == "__main__":
    get_weather()
