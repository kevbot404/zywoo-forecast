# sort dataset.csv by date

import pandas as pd

input_file = "./data/dataset.csv"
output_file = "./data/dataset_sorted.csv"

df = pd.read_csv(input_file)

# Parse date so sorting is chronological rather than alphabetical
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Sort:
# 1. date descending
# 2. event_name ascending
# 3. location_city ascending
df = df.sort_values(
    by=["date", "event_name", "location_city"],
    ascending=[False, True, True],
    na_position="last"
)

# Save without the pandas index
df.to_csv(output_file, index=False)

print(f"Sorted dataset saved to: {output_file}")