# OpenAQ request methods

import os
import csv
import time
import requests
from dotenv import load_dotenv


# ==================================================
# Configuration
# ==================================================

load_dotenv()

API_KEY = os.getenv("API_KEY_AQ")

BASE_URL = "https://api.openaq.org/v3"

HEADERS = {
    "X-API-Key": API_KEY
}

OUTPUT_FILE = "openaq_results.csv"

# How long a normal request is allowed to wait.
REQUEST_TIMEOUT = 30

# Maximum number of retries after 429 / connection errors.
MAX_RETRIES = 5

# Default wait if Retry-After is not supplied.
DEFAULT_RETRY_WAIT = 10


# ==================================================
# Request helper
# ==================================================

def request_with_retry(
    url,
    params=None,
    max_retries=MAX_RETRIES,
    timeout=REQUEST_TIMEOUT
):
    """
    Make an OpenAQ API request.

    Handles:
        - HTTP 429 Too Many Requests
        - Request timeouts
        - Connection errors

    For HTTP 429:
        Uses Retry-After if provided.
        Otherwise uses exponential backoff.

    Returns:
        requests.Response

    Raises:
        requests.exceptions.RequestException
        after all retries are exhausted.
    """

    for attempt in range(max_retries + 1):

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=timeout
            )

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError
        ) as e:

            if attempt == max_retries:
                raise

            wait = DEFAULT_RETRY_WAIT * (
                2 ** attempt
            )

            print(
                f"\nRequest error: {e}"
            )

            print(
                f"Retrying in {wait:.0f} seconds "
                f"({attempt + 1}/{max_retries})..."
            )

            time.sleep(wait)

            continue

        # -----------------------------------------
        # Success
        # -----------------------------------------

        if response.status_code != 429:

            response.raise_for_status()

            return response

        # -----------------------------------------
        # 429 Too Many Requests
        # -----------------------------------------

        if attempt == max_retries:

            print(
                "\nMaximum retries reached for "
                "HTTP 429."
            )

            response.raise_for_status()

        # OpenAQ may tell us exactly how long to wait.
        retry_after = response.headers.get(
            "Retry-After"
        )

        if retry_after is not None:

            try:

                wait = float(retry_after)

            except ValueError:

                wait = DEFAULT_RETRY_WAIT

        else:

            # Exponential backoff:
            #
            # 10
            # 20
            # 40
            # 80
            # 160

            wait = DEFAULT_RETRY_WAIT * (
                2 ** attempt
            )

        print(
            f"\n429 Too Many Requests."
        )

        print(
            f"Waiting {wait:.0f} seconds "
            f"before retry "
            f"{attempt + 1}/{max_retries}..."
        )

        time.sleep(wait)

    raise RuntimeError(
        "Request retry loop failed unexpectedly."
    )


# ==================================================
# API methods
# ==================================================

def get_locations(
    latitude,
    longitude,
    radius=10000,
    limit=3
):
    """Get nearby locations."""

    url = f"{BASE_URL}/locations"

    params = {
        "coordinates": f"{latitude},{longitude}",
        "radius": radius,
        "limit": limit,
    }

    response = request_with_retry(
        url,
        params=params
    )

    return response.json()["results"]


def get_sensors(location_id):
    """Get all sensors belonging to a location."""

    url = (
        f"{BASE_URL}/locations/"
        f"{location_id}/sensors"
    )

    response = request_with_retry(
        url
    )

    return response.json()["results"]


def get_daily_measurements(
    sensor_id,
    datetime_from,
    datetime_to,
    limit=100
):
    """Get daily measurements for a sensor."""

    url = (
        f"{BASE_URL}/sensors/"
        f"{sensor_id}/measurements/daily"
    )

    params = {
        "datetime_from": datetime_from,
        "datetime_to": datetime_to,
        "limit": limit,
    }

    response = request_with_retry(
        url,
        params=params
    )

    return response.json()["results"]


# ==================================================
# Save final result
# ==================================================

def save_result(
    latitude,
    longitude,
    location,
    measurements
):
    """
    Append the final best-location result to CSV.

    Existing results are NEVER overwritten.

    The CSV contains only the intended final output.
    """

    fieldnames = [
        "latitude",
        "longitude",
        "location_id",
        "location",
        "date",
        "parameter",
        "value",
        "units",
        "coverage",
    ]

    file_exists = os.path.exists(
        OUTPUT_FILE
    )

    with open(
        OUTPUT_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        # Only write header for a new file.
        if not file_exists:

            writer.writeheader()

        # Write the final best location.
        for measurement in measurements:

            writer.writerow({

                "latitude": latitude,

                "longitude": longitude,

                "location_id": location["id"],

                "location": location.get(
                    "name"
                ),

                "date": measurement[
                    "date"
                ],

                "parameter": measurement[
                    "parameter"
                ],

                "value": measurement[
                    "value"
                ],

                "units": measurement[
                    "units"
                ],

                "coverage": measurement[
                    "coverage"
                ],
            })

        # Make sure everything is physically
        # written before continuing.
        f.flush()
        os.fsync(f.fileno())

    print(
        f"\nSaved {len(measurements)} "
        f"measurements to "
        f"{OUTPUT_FILE}"
    )


# ==================================================
# Main function
# ==================================================

def get_location_pollution(
    latitude,
    longitude,
    datetime_from,
    datetime_to,
    max_locations=3
):
    """
    Find the best nearby location based on the
    number of measurements available.

    Only the first 3 nearby locations are checked.

    The final best location and its measurements
    are appended to the CSV after the search is
    complete.
    """

    # -----------------------------------------
    # Safety limit
    # -----------------------------------------

    max_locations = min(
        max_locations,
        3
    )

    # -----------------------------------------
    # 1. Get nearby locations
    # -----------------------------------------

    locations = get_locations(
        latitude=latitude,
        longitude=longitude,
        limit=max_locations
    )

    if not locations:

        raise ValueError(
            "No locations found."
        )

    # Extra safety in case API returns more.
    locations = locations[:3]

    print(
        f"\nFound {len(locations)} locations "
        f"to check "
        f"(maximum allowed: 3)."
    )

    # -----------------------------------------
    # Best result
    # -----------------------------------------

    best_location = None
    best_measurements = []

    # -----------------------------------------
    # 2. Check locations
    # -----------------------------------------

    for location_number, location in enumerate(
        locations,
        start=1
    ):

        location_id = location["id"]
        location_name = location.get(
            "name"
        )

        print("\n" + "=" * 50)

        print(
            f"Checking location "
            f"#{location_number}: "
            f"{location_name} "
            f"(ID: {location_id})"
        )

        print("=" * 50)

        # -----------------------------------------
        # Get sensors
        # -----------------------------------------

        try:

            sensors = get_sensors(
                location_id
            )

        except requests.exceptions.RequestException as e:

            print(
                f"Could not get sensors "
                f"for location "
                f"{location_id}: {e}"
            )

            continue

        if not sensors:

            print(
                "No sensors found."
            )

            continue

        print(
            f"\nFound {len(sensors)} sensors."
        )

        # -----------------------------------------
        # Get measurements
        # -----------------------------------------

        location_measurements = []

        for sensor_number, sensor in enumerate(
            sensors,
            start=1
        ):

            sensor_id = sensor["id"]

            print(
                f"\nSensor "
                f"{sensor_number}/"
                f"{len(sensors)}: "
                f"{sensor_id}"
            )

            print(
                f"Parameter: "
                f"{sensor['parameter']['name']}"
            )

            print(
                f"Units: "
                f"{sensor['parameter']['units']}"
            )

            try:

                measurements = (
                    get_daily_measurements(
                        sensor_id=sensor_id,
                        datetime_from=datetime_from,
                        datetime_to=datetime_to
                    )
                )

            except requests.exceptions.RequestException as e:

                print(
                    f"Could not get measurements "
                    f"for sensor {sensor_id}: "
                    f"{e}"
                )

                continue

            # -----------------------------------------
            # Convert API response
            # -----------------------------------------

            for measurement in measurements:

                location_measurements.append({

                    "date": (
                        measurement[
                            "period"
                        ][
                            "datetimeFrom"
                        ][
                            "local"
                        ][:10]
                    ),

                    "parameter": (
                        measurement[
                            "parameter"
                        ][
                            "name"
                        ]
                    ),

                    "value": measurement[
                        "value"
                    ],

                    "units": (
                        measurement[
                            "parameter"
                        ][
                            "units"
                        ]
                    ),

                    "coverage": (
                        measurement[
                            "coverage"
                        ][
                            "percentCoverage"
                        ]
                    ),
                })

        # -----------------------------------------
        # Count measurements
        # -----------------------------------------

        measurement_count = len(
            location_measurements
        )

        print(
            f"\nLocation {location_name} "
            f"has {measurement_count} "
            f"measurements."
        )

        # -----------------------------------------
        # Is this the best location?
        # -----------------------------------------

        if measurement_count > len(
            best_measurements
        ):

            best_location = location

            best_measurements = (
                location_measurements.copy()
            )

            print(
                f"New best location: "
                f"{location_name} "
                f"({measurement_count} "
                f"measurements)"
            )

    # -----------------------------------------
    # 3. No result
    # -----------------------------------------

    if (
        best_location is None
        or not best_measurements
    ):

        print(
            "\nNo measurements found at "
            "any nearby location."
        )

        return []

    # -----------------------------------------
    # 4. Final best location
    # -----------------------------------------

    print("\n" + "=" * 50)
    print("BEST LOCATION")
    print("=" * 50)

    print(
        f"Location ID: "
        f"{best_location['id']}"
    )

    print(
        f"Location: "
        f"{best_location.get('name')}"
    )

    print(
        f"Measurements: "
        f"{len(best_measurements)}"
    )

    # -----------------------------------------
    # 5. Save final result
    # -----------------------------------------

    save_result(
        latitude=latitude,
        longitude=longitude,
        location=best_location,
        measurements=best_measurements
    )

    # -----------------------------------------
    # 6. Return final result
    # -----------------------------------------

    return {
        "location_id": best_location["id"],
        "location": best_location.get(
            "name"
        ),
        "measurements": best_measurements
    }


# ==================================================
# Example
# ==================================================

# LATITUDE = 48.8566
# LONGITUDE = 2.3522

# measurements = get_location_pollution(
#     latitude=LATITUDE,
#     longitude=LONGITUDE,
#     datetime_from="2026-08-01T00:00:00Z",
#     datetime_to="2026-08-02T00:00:00Z",
#     max_locations=3
# )

# print("\nDaily pollution:")

# for measurement in measurements:
#     print(measurement)
