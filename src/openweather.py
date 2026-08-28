import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

def get_air_pollution_history(lat, lon, start, end, api_key):
    url = "https://api.openweathermap.org/data/2.5/air_pollution/history"

    params = {
        "lat": lat,
        "lon": lon,
        "start": start,
        "end": end,
        "appid": api_key
    }

    response = requests.get(url, params=params, timeout=10)

    print("Status:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()

    return response.json()

def get_air_pollution_forecast(lat, lon, api_key):
    url = "http://api.openweathermap.org/data/2.5/air_pollution/forecast"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key
    }

    response = requests.get(url, params=params, timeout=10)

    print("Status:", response.status_code)
    print("Response:", response.text)
    
    response.raise_for_status()

    return response.json()









now = int(time.time())
yesterday = now - 24 * 60 * 60

data = get_air_pollution_history(
    lat=59.437,
    lon=24.7536,
    start=yesterday,
    end=now,
    api_key=api_key
)

print(data)

data = get_air_pollution_forecast(
    lat=59.437,
    lon=24.7536,
    api_key=api_key
)

print(data)