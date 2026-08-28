import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY_AQ")

BASE_URL = "https://api.openaq.org/v3"

HEADERS = {
    "X-API-Key": API_KEY
}


def get_locations(latitude, longitude, radius=25000, limit=100):
    """Get locations near the given coordinates."""

    url = f"{BASE_URL}/locations"

    params = {
        "coordinates": f"{latitude},{longitude}",
        "radius": radius,
        "limit": limit,
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params
    )

    response.raise_for_status()

    return response.json()["results"]


def get_sensors(location_id):
    """Get all sensors belonging to a location."""

    url = f"{BASE_URL}/locations/{location_id}/sensors"

    response = requests.get(
        url,
        headers=HEADERS
    )

    response.raise_for_status()

    return response.json()["results"]


def get_daily_measurements(
    sensor_id,
    datetime_from,
    datetime_to,
    limit=100
):
    """Get daily measurements for a sensor."""

    url = f"{BASE_URL}/sensors/{sensor_id}/measurements/daily"

    params = {
        "datetime_from": datetime_from,
        "datetime_to": datetime_to,
        "limit": limit,
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params
    )

    response.raise_for_status()

    return response.json()["results"]


def get_location_pollution(
    latitude,
    longitude,
    datetime_from,
    datetime_to
):
    """
    1. Find locations near coordinates.
    2. Select the first location.
    3. Get all sensors for that location.
    4. Get daily measurements from every sensor.
    """

    # -----------------------------------------
    # 1. Get locations
    # -----------------------------------------

    locations = get_locations(
        latitude=latitude,
        longitude=longitude
    )

    if not locations:
        raise ValueError("No locations found.")

    # Pick the first location
    location = locations[0]
    location_id = location["id"]

    print(f"Location ID: {location_id}")
    print(f"Location: {location.get('name')}")


    # -----------------------------------------
    # 2. Get all sensors for the location
    # -----------------------------------------

    sensors = get_sensors(location_id)

    if not sensors:
        raise ValueError(
            f"No sensors found for location {location_id}."
        )

    print("\nSensors:")

    for sensor in sensors:
        print(
            f"ID: {sensor['id']} | "
            f"Parameter: {sensor['parameter']['name']} | "
            f"Units: {sensor['parameter']['units']}"
        )


    # -----------------------------------------
    # 3. Get daily data from every sensor
    # -----------------------------------------

    all_measurements = []

    for sensor in sensors:

        sensor_id = sensor["id"]

        measurements = get_daily_measurements(
            sensor_id=sensor_id,
            datetime_from=datetime_from,
            datetime_to=datetime_to
        )

        for measurement in measurements:

            all_measurements.append({
                "date": measurement["period"]["datetimeFrom"]["local"][:10],
                "parameter": measurement["parameter"]["name"],
                "value": measurement["value"],
                "units": measurement["parameter"]["units"],
                "coverage": measurement["coverage"]["percentCoverage"],
            })

    return all_measurements


# ==================================================
# Example
# ==================================================

LATITUDE = 59.4370
LONGITUDE = 24.7536

measurements = get_location_pollution(
    latitude=LATITUDE,
    longitude=LONGITUDE,
    datetime_from="2026-08-01T00:00:00Z",
    datetime_to="2026-08-02T00:00:00Z"
)


# Print final data
print("\nDaily pollution:")

for measurement in measurements:
    print(measurement)
