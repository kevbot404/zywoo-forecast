# match each event to latitude and longitude

import csv
import requests
import time
import json
import os

from openstreetmap import city_to_coordinates

def locations_file_to_csv(input_file, output_file, cache_file="geocode_cache.json"):
    """
    Input file format, one location per row:

    Copenhagen,2026-08-27T00:00:00,2026-08-28T00:00:00
    Berlin,2026-08-27T00:00:00,2026-08-28T00:00:00
    Copenhagen,2026-08-29T00:00:00,2026-08-30T00:00:00

    Output:

    location,datefrom,dateto,latitude,longitude
    Copenhagen,2026-08-27T00:00:00,2026-08-28T00:00:00,55.6867243,12.5700724
    ...

    Coordinates are cached by location, so Copenhagen is only
    requested from Nominatim once.
    """

    # Load existing cache
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
    else:
        cache = {}

    output_rows = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Remove surrounding [ ] if present
            line = line.strip("[]")

            # Parse CSV-style row
            row = next(csv.reader([line]))

            if len(row) < 3:
                print(f"Skipping invalid row: {line}")
                continue

            location = row[0].strip()
            datefrom = row[1].strip()
            dateto = row[2].strip()

            # Check cache first
            if location in cache:
                print(f"Cache hit: {location}")
                coords = cache[location]

            else:
                print(f"Geocoding: {location}")

                try:
                    coords = city_to_coordinates(location)

                    if coords is None:
                        print(f"  Could not find coordinates for: {location}")
                        coords = {
                            "latitude": "",
                            "longitude": ""
                        }

                    # Save result to cache
                    cache[location] = coords

                    # Small delay to be respectful to Nominatim
                    time.sleep(1)

                    # Save cache immediately so progress isn't lost
                    with open(cache_file, "w", encoding="utf-8") as cache_f:
                        json.dump(cache, cache_f, indent=2)

                except requests.RequestException as e:
                    print(f"  Error geocoding {location}: {e}")

                    coords = {
                        "latitude": "",
                        "longitude": ""
                    }

            output_rows.append([
                location,
                datefrom,
                dateto,
                coords["latitude"],
                coords["longitude"]
            ])

    # Write new output CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "location",
            "datefrom",
            "dateto",
            "latitude",
            "longitude"
        ])

        writer.writerows(output_rows)

    print(f"\nDone. Output written to: {output_file}")
    print(f"Cache written to: {cache_file}")


# Example
locations_file_to_csv(
    "./data/input2.txt",
    "output.csv"
)