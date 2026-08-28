# flatten openaq parameters into columns

import pandas as pd

INPUT_FILE = "./data/openaq_zywoo_merged.csv"
OUTPUT_FILE = "./data/openaq_zywoo_flattened.csv"

input = pd.read_csv(INPUT_FILE)

id_columns = [
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
]

# Flatten parameter into columns, using value as the cell value.
output = (
    input
    .pivot_table(
        index=id_columns,
        columns="parameter",
        values="value",
        aggfunc="first"
    )
    .reset_index()
)

output.columns.name = None

output.to_csv(OUTPUT_FILE, index=False)

print(f"Saved: {OUTPUT_FILE}")