import pandas as pd
from pathlib import Path


MATCHES_FILE = "./data/matches_aq.csv"
WEATHER_FILE = "./data/weather_results.csv"
OUTPUT_FILE = "./data/matches_aq_weather.csv"


# ============================================================
# Output columns
# ============================================================

OUTPUT_COLUMNS = [
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
    "co",
    "no",
    "no2",
    "nox",
    "o3",
    "pm10",
    "pm25",
    "so2",

    "weather_code",
    "temperature_2m_max",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "sunrise",
    "sunset",
    "daylight_duration",
    "sunshine_duration",
    "rain_sum",
    "snowfall_sum",
    "precipitation_sum",
    "precipitation_hours",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "wind_direction_10m_dominant",
    "shortwave_radiation_sum",
    "et0_fao_evapotranspiration",
    "apparent_temperature_mean",
    "cloud_cover_mean",
    "cloud_cover_max",
    "cloud_cover_min",
    "dew_point_2m_min",
    "dew_point_2m_max",
    "dew_point_2m_mean",
    "et0_fao_evapotranspiration_sum",
    "relative_humidity_2m_mean",
    "relative_humidity_2m_max",
    "relative_humidity_2m_min",
    "snowfall_water_equivalent_sum",
    "pressure_msl_mean",
    "pressure_msl_max",
    "pressure_msl_min",
    "surface_pressure_mean",
    "surface_pressure_max",
    "surface_pressure_min",
    "wind_gusts_10m_mean",
    "wind_speed_10m_mean",
    "wind_gusts_10m_min",
    "wind_speed_10m_min",
    "wet_bulb_temperature_2m_mean",
    "wet_bulb_temperature_2m_max",
    "wet_bulb_temperature_2m_min",
    "vapour_pressure_deficit_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "elevation",
]


# ============================================================
# Main
# ============================================================

def main():

    # --------------------------------------------------------
    # Check input files
    # --------------------------------------------------------

    if not Path(MATCHES_FILE).exists():
        raise FileNotFoundError(
            f"Could not find matches file: {MATCHES_FILE}"
        )

    if not Path(WEATHER_FILE).exists():
        raise FileNotFoundError(
            f"Could not find weather file: {WEATHER_FILE}"
        )

    # --------------------------------------------------------
    # Read files
    # --------------------------------------------------------

    matches = pd.read_csv(MATCHES_FILE)
    weather = pd.read_csv(WEATHER_FILE)

    print(f"Loaded {len(matches):,} match rows")
    print(f"Loaded {len(weather):,} weather rows")

    # --------------------------------------------------------
    # Normalize MATCH date
    #
    # Example:
    # 2025-03-21
    # 2025-03-21T00:00:00
    #
    # both become:
    # 2025-03-21
    # --------------------------------------------------------

    matches["date"] = pd.to_datetime(
        matches["date"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Use weather.date as the actual weather date.
    #
    # DO NOT use datefrom.
    #
    # Example:
    #
    # datefrom = 2025-03-19
    # dateto   = 2025-03-25
    # date     = 2025-03-21
    #
    # A match on 2025-03-21 must match this weather row.
    # --------------------------------------------------------

    weather["weather_date"] = pd.to_datetime(
        weather["date"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # Normalize city names
    # --------------------------------------------------------

    matches["location_key"] = (
        matches["location_city"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    weather["location_key"] = (
        weather["location"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    # --------------------------------------------------------
    # Weather columns that we actually need
    # --------------------------------------------------------

    match_columns = {
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
        "co",
        "no",
        "no2",
        "nox",
        "o3",
        "pm10",
        "pm25",
        "so2",
    }

    weather_output_columns = [
        column
        for column in OUTPUT_COLUMNS
        if column not in match_columns
        and column in weather.columns
    ]

    # --------------------------------------------------------
    # Build weather dataframe
    #
    # Merge keys:
    #   location_key
    #   weather_date
    #
    # weather_date comes from weather.date
    # --------------------------------------------------------

    weather_for_merge = weather[
        ["location_key", "weather_date"] + weather_output_columns
    ].copy()

    # --------------------------------------------------------
    # Check duplicate city/date combinations
    # --------------------------------------------------------

    duplicate_mask = weather_for_merge.duplicated(
        subset=["location_key", "weather_date"],
        keep=False
    )

    duplicate_rows = weather_for_merge[duplicate_mask]

    if len(duplicate_rows) > 0:

        duplicate_keys = (
            duplicate_rows[
                ["location_key", "weather_date"]
            ]
            .drop_duplicates()
        )

        print()
        print(
            f"Warning: {len(duplicate_keys):,} "
            f"location/date combinations have multiple weather rows."
        )

        print(
            "Keeping the first weather row for each "
            "location/date combination."
        )

        weather_for_merge = weather_for_merge.drop_duplicates(
            subset=["location_key", "weather_date"],
            keep="first"
        )

    # --------------------------------------------------------
    # Show date range information
    # --------------------------------------------------------

    print()
    print(
        "Match date range:",
        matches["date"].min(),
        "to",
        matches["date"].max()
    )

    print(
        "Weather date range:",
        weather_for_merge["weather_date"].min(),
        "to",
        weather_for_merge["weather_date"].max()
    )

    # --------------------------------------------------------
    # MERGE
    #
    # Exact match:
    #
    # matches.location_city
    #       ==
    # weather.location
    #
    # AND
    #
    # matches.date
    #       ==
    # weather.date
    # --------------------------------------------------------

    combined = matches.merge(
        weather_for_merge,
        how="left",
        left_on=["location_key", "date"],
        right_on=["location_key", "weather_date"],
        validate="many_to_one"
    )

    # --------------------------------------------------------
    # Remove temporary merge columns
    # --------------------------------------------------------

    combined = combined.drop(
        columns=["location_key", "weather_date"],
        errors="ignore"
    )

    # --------------------------------------------------------
    # Make sure every requested output column exists
    # --------------------------------------------------------

    for column in OUTPUT_COLUMNS:

        if column not in combined.columns:
            combined[column] = pd.NA

    # --------------------------------------------------------
    # Exact requested column order
    # --------------------------------------------------------

    combined = combined[OUTPUT_COLUMNS]

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Calculate matching statistics
    # --------------------------------------------------------

    weather_columns = [
        column
        for column in weather_output_columns
        if column in combined.columns
    ]

    if weather_columns:

        rows_with_weather = (
            combined[weather_columns]
            .notna()
            .any(axis=1)
        )

    else:

        rows_with_weather = pd.Series(
            False,
            index=combined.index
        )

    matched_count = int(rows_with_weather.sum())
    unmatched_count = int((~rows_with_weather).sum())

    # --------------------------------------------------------
    # Show unmatched locations/dates
    # --------------------------------------------------------

    unmatched = combined.loc[
        ~rows_with_weather,
        ["location_city", "date"]
    ].drop_duplicates()

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print()
    print("=" * 65)
    print("COMBINATION COMPLETE")
    print("=" * 65)

    print(f"Match rows:              {len(matches):,}")
    print(f"Weather rows:            {len(weather):,}")
    print(f"Output rows:             {len(combined):,}")
    print(f"Rows with weather:       {matched_count:,}")
    print(f"Rows without weather:    {unmatched_count:,}")
    print(f"Output file:             {OUTPUT_FILE}")

    print("=" * 65)

    # --------------------------------------------------------
    # Print some unmatched examples
    # --------------------------------------------------------

    if len(unmatched) > 0:

        print()
        print("First 20 unmatched location/date combinations:")
        print("-" * 65)

        print(
            unmatched.head(20).to_string(index=False)
        )

    print()


if __name__ == "__main__":
    main()