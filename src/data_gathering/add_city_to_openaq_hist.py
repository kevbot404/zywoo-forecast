import csv

# Input files
LOCATIONS_FILE = "./data/loc_cords_date.csv"
OPENAQ_FILE = "./data/openaq_historical.csv"

# Output file
OUTPUT_FILE = "./data/openaq_historical_with_city.csv"


def normalize_coordinate(value):
    """Convert coordinates to a consistent value for matching."""
    try:
        return round(float(value), 7)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------
# Read loc_cords_date.csv and build coordinate -> city map
# ---------------------------------------------------------

location_map = {}

with open(LOCATIONS_FILE, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        latitude = normalize_coordinate(row.get("latitude"))
        longitude = normalize_coordinate(row.get("longitude"))

        if latitude is not None and longitude is not None:
            location_map[(latitude, longitude)] = row.get("location", "")


# ---------------------------------------------------------
# Read OpenAQ CSV and create the new output CSV
# ---------------------------------------------------------

with open(OPENAQ_FILE, "r", encoding="utf-8-sig", newline="") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as outfile:

    reader = csv.DictReader(infile)

    # Desired output column order
    fieldnames = [
        "location_city",
        "latitude",
        "longitude",
        "location_id",
        "location",
        "date",
        "parameter",
        "value",
        "units",
        "coverage"
    ]

    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        latitude = normalize_coordinate(row.get("latitude"))
        longitude = normalize_coordinate(row.get("longitude"))

        # Find matching city
        location_city = location_map.get(
            (latitude, longitude),
            ""
        )

        # Create output row
        output_row = {
            "location_city": location_city,
            "latitude": row.get("latitude", ""),
            "longitude": row.get("longitude", ""),
            "location_id": row.get("location_id", ""),
            "location": row.get("location", ""),
            "date": row.get("date", ""),
            "parameter": row.get("parameter", ""),
            "value": row.get("value", ""),
            "units": row.get("units", ""),
            "coverage": row.get("coverage", "")
        }

        writer.writerow(output_row)


print(f"Done! Output saved as: {OUTPUT_FILE}")