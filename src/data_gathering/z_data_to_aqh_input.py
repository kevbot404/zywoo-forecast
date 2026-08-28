# transform zywoo data with datetime ranges to location,datetime_From,datetime_to for openaq pipeline

import csv
from pathlib import Path

input_file = Path("./data/zywoo_data_event_datetimes.csv")
output_file = Path("./data/event_location_daterange.csv")

columns_to_keep = ["location", "datetime_from", "datetime_to"]

seen = set()

with open(input_file, "r", newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=columns_to_keep)
        writer.writeheader()

        for row in reader:
            values = tuple(row[column] for column in columns_to_keep)

            # Skip duplicate combinations
            if values in seen:
                continue

            seen.add(values)

            writer.writerow({
                column: row[column]
                for column in columns_to_keep
            })

print(f"Done! Saved filtered, deduplicated CSV to {output_file}")