# openaq request methods

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY_AQ")

BASE_URL = "https://api.openaq.org/v3"

HEADERS = {
    "X-API-Key": API_KEY
}


def get_locations(latitude, longitude, radius=5000, limit=3):
    """Get nearby locations."""

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
    datetime_to,
    max_locations=3
):
    """
    Find the best nearby location based on the number
    of measurements available for the requested time period.

    Only the first 3 nearby locations are ever checked.

    1. Find nearby locations.
    2. Check at most 3 locations.
    3. Get sensors for each location.
    4. Get measurements from each sensor.
    5. Count measurements for each location.
    6. Select the location with the most measurements.
    7. Return measurements from the best location.
    """

    # -----------------------------------------
    # Safety limit:
    # Never check more than 3 locations.
    # -----------------------------------------

    max_locations = min(max_locations, 3)

    # -----------------------------------------
    # 1. Get nearby locations
    # -----------------------------------------

    locations = get_locations(
        latitude=latitude,
        longitude=longitude,
        limit=max_locations
    )

    if not locations:
        raise ValueError("No locations found.")

    # Extra safety in case the API returns more
    # locations than requested.
    locations = locations[:3]

    print(
        f"\nFound {len(locations)} locations to check "
        f"(maximum allowed: 3)."
    )

    # Store the best result
    best_location = None
    best_measurements = []

    # -----------------------------------------
    # 2. Check at most 3 locations
    # -----------------------------------------

    for location_number, location in enumerate(locations, start=1):

        location_id = location["id"]
        location_name = location.get("name")

        print("\n" + "=" * 50)
        print(
            f"Checking location #{location_number}: "
            f"{location_name} (ID: {location_id})"
        )
        print("=" * 50)

        # -----------------------------------------
        # Get sensors
        # -----------------------------------------

        try:
            sensors = get_sensors(location_id)

        except requests.exceptions.HTTPError as e:
            print(f"Could not get sensors: {e}")
            continue

        if not sensors:
            print("No sensors found.")
            continue

        print("\nSensors:")

        for sensor in sensors:
            print(
                f"ID: {sensor['id']} | "
                f"Parameter: {sensor['parameter']['name']} | "
                f"Units: {sensor['parameter']['units']}"
            )

        # -----------------------------------------
        # Get measurements
        # -----------------------------------------

        location_measurements = []

        for sensor in sensors:

            sensor_id = sensor["id"]

            try:
                measurements = get_daily_measurements(
                    sensor_id=sensor_id,
                    datetime_from=datetime_from,
                    datetime_to=datetime_to
                )

            except requests.exceptions.HTTPError as e:
                print(
                    f"Could not get measurements for "
                    f"sensor {sensor_id}: {e}"
                )
                continue

            for measurement in measurements:

                location_measurements.append({
                    "date": measurement["period"]["datetimeFrom"]["local"][:10],
                    "parameter": measurement["parameter"]["name"],
                    "value": measurement["value"],
                    "units": measurement["parameter"]["units"],
                    "coverage": measurement["coverage"]["percentCoverage"],
                })

        # -----------------------------------------
        # Count measurements
        # -----------------------------------------

        measurement_count = len(location_measurements)

        print(
            f"\nLocation {location_name} has "
            f"{measurement_count} measurements."
        )

        # -----------------------------------------
        # Is this the best location so far?
        # -----------------------------------------

        if measurement_count > len(best_measurements):

            best_location = location
            best_measurements = location_measurements

            print(
                f"New best location: {location_name} "
                f"({measurement_count} measurements)"
            )

    # -----------------------------------------
    # 3. Return best location
    # -----------------------------------------

    if best_location is None or not best_measurements:

        print(
            "\nNo measurements found at any nearby location."
        )

        return []

    print("\n" + "=" * 50)
    print("BEST LOCATION")
    print("=" * 50)

    print(f"Location ID: {best_location['id']}")
    print(f"Location: {best_location.get('name')}")
    print(f"Measurements: {len(best_measurements)}")

    return {
        "location_id": best_location["id"],
        "location": best_location.get("name"),
        "measurements": best_measurements
    }


# ==================================================
# Example
# ==================================================

# LATITUDE = 59.437242
# LONGITUDE = 24.7572693

# measurements = get_location_pollution(
#     latitude=LATITUDE,
#     longitude=LONGITUDE,
#     datetime_from="2026-08-01T00:00:00Z",
#     datetime_to="2026-08-02T00:00:00Z",
#     max_locations=3
# )


# Print final data
# print("\nDaily pollution:")

# for measurement in measurements:
#     print(measurement)
