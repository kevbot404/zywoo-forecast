import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


INPUT_FILE = Path("./data/zywoo_data.csv")
OUTPUT_FILE = Path("./data/zywoo_data_event_datetimes.csv")


def parse_date(date_string):
    return datetime.strptime(date_string, "%d/%m/%y")


with INPUT_FILE.open("r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)

    rows = list(reader)
    fieldnames = reader.fieldnames


# Find date range for each exact event + location

event_ranges = defaultdict(list)

for row in rows:
    key = (
        row["event_name"],
        row["location"]
    )

    event_date = parse_date(row["date"])

    event_ranges[key].append(event_date)


# Calculate datetime_from / datetime_to
event_datetimes = {}

for key, dates in event_ranges.items():

    earliest_date = min(dates)
    latest_date = max(dates)

    datetime_from = earliest_date.strftime(
        "%Y-%m-%dT00:00:00"
    )

    # datetime_to is the day AFTER the final event date
    datetime_to = (
        latest_date + timedelta(days=1)
    ).strftime(
        "%Y-%m-%dT00:00:00"
    )

    event_datetimes[key] = (
        datetime_from,
        datetime_to
    )



# Add datetime columns to every row

fieldnames = list(fieldnames)

fieldnames.append("datetime_from")
fieldnames.append("datetime_to")


for row in rows:

    key = (
        row["event_name"],
        row["location"]
    )

    datetime_from, datetime_to = event_datetimes[key]

    row["datetime_from"] = datetime_from
    row["datetime_to"] = datetime_to



# Write NEW CSV

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)


print(f"Created: {OUTPUT_FILE}")