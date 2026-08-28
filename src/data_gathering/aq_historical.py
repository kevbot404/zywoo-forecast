import sys
import csv

from openstreetmap import city_to_coordinates
from openaq import get_location_pollution


def main():
    if len(sys.argv) != 2:
        print("Usage: python historical.py <input.txt>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Output CSV file
    output_file = "historical.csv"

    # Store all results here
    rows = []

    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            # Expected format:
            # city_name, datetime_from, datetime_to
            parts = [part.strip() for part in line.split(",")]

            if len(parts) != 3:
                print(f"Invalid line: {line}")
                continue

            city = parts[0].strip('"\'')
            datetime_from = parts[1]
            datetime_to = parts[2]

            print(f"\nCity: {city}")
            print(f"From: {datetime_from}")
            print(f"To:   {datetime_to}")

            # -----------------------------------------
            # 1. Get coordinates from OpenStreetMap
            # -----------------------------------------

            coordinates = city_to_coordinates(city)

            latitude = coordinates["latitude"]
            longitude = coordinates["longitude"]

            print(f"Coordinates: {latitude}, {longitude}")

            # -----------------------------------------
            # 2. Get historical pollution data
            # -----------------------------------------

            result = get_location_pollution(
                latitude,
                longitude,
                datetime_from,
                datetime_to
            )

            if not result:
                print("No measurements found.")
                continue

            location_id = result["location_id"]
            location_name = result["location"]
            measurements = result["measurements"]

            print(f"Location ID: {location_id}")
            print(f"Location: {location_name}")

            # -----------------------------------------
            # 3. Print and collect results
            # -----------------------------------------

            print("Pollution measurements:")

            for measurement in measurements:

                print(
                    f"  {measurement['date']} | "
                    f"{measurement['parameter']} | "
                    f"{measurement['value']} "
                    f"{measurement['units']} | "
                    f"coverage: {measurement['coverage']}%"
                )

                rows.append({
                    "city": city,
                    "latitude": latitude,
                    "longitude": longitude,
                    "location_id": location_id,
                    "location": location_name,
                    "date": measurement["date"],
                    "parameter": measurement["parameter"],
                    "value": measurement["value"],
                    "coverage": measurement["coverage"],
                })

    # -----------------------------------------
    # 4. Save everything to CSV
    # -----------------------------------------

    fieldnames = [
        "city",
        "latitude",
        "longitude",
        "location_id",
        "location",
        "date",
        "parameter",
        "value",
        "coverage",
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"\nSaved {len(rows)} measurements to {output_file}"
    )


if __name__ == "__main__":
    main()

