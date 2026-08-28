# merge cs2 match data with openaq air quality data

import pandas as pd

OPENAQ_FILE = "./data/openaq_historical_with_city.csv"
ZYWOO_FILE = "./data/zywoo_data.csv"
OUTPUT_FILE = "./data/openaq_zywoo_merged.csv"

openaq = pd.read_csv(OPENAQ_FILE)
zywoo = pd.read_csv(ZYWOO_FILE)

# ============================================================
# Convert dates to the same format
# ============================================================

# OpenAQ date example: 2026-08-27
openaq["date"] = pd.to_datetime(
    openaq["date"],
    format="%Y-%m-%d",
    errors="coerce"
)

# ZywOo date example: 27/08/26
zywoo["date"] = pd.to_datetime(
    zywoo["date"],
    format="%d/%m/%y",
    errors="coerce"
)


# ============================================================
# Rename OpenAQ location column for the final output
# ============================================================

openaq = openaq.rename(columns={
    "location": "location_openaq"
})


# ============================================================
# Merge:
#   OpenAQ location_city == ZywOo location
#   OpenAQ date == ZywOo date
# ============================================================

merged = zywoo.merge(
    openaq,
    left_on=["location", "date"],
    right_on=["location_city", "date"],
    how="inner"
)


# ============================================================
# Select columns for the output
# ============================================================

output_columns = [
    "event_name",
    "location_city",
    "date",
    "player_team",
    "opponent",
    "map",
    "kd",
    "plus_minus",
    "rating",
    "location_openaq",
    "parameter",
    "value",
    "units",
    "coverage"
]

result = merged[output_columns].copy()


# ============================================================
# Format date as YYYY-MM-DD
# ============================================================

result["date"] = result["date"].dt.strftime("%Y-%m-%d")


# ============================================================
# Save output CSV
# ============================================================

result.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"Done! Created: {OUTPUT_FILE}")
print(f"Rows matched: {len(result)}")