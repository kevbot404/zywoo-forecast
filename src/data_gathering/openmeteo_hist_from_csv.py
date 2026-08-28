# Read locations and date ranges from loc_cords_date.csv,
# retrieve Open-Meteo historical daily weather data,
# and write the results to weather_results.csv.

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import time


INPUT_CSV = "./data/loc_cords_date.csv"
OUTPUT_CSV = "./data/weather_results.csv"

URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_VARIABLES = [
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
]


# ---------------------------------------------------------
# Open-Meteo client
# ---------------------------------------------------------

cache_session = requests_cache.CachedSession(
    ".cache",
    expire_after=-1
)

retry_session = retry(
    cache_session,
    retries=5,
    backoff_factor=0.2
)

openmeteo = openmeteo_requests.Client(
    session=retry_session
)


# ---------------------------------------------------------
# Function to retrieve weather for one input row
# ---------------------------------------------------------

def get_weather(row):
    location = row["location"]
    latitude = float(row["latitude"])
    longitude = float(row["longitude"])

    # Convert timestamps to dates.
    date_from = pd.to_datetime(row["datefrom"])
    date_to = pd.to_datetime(row["dateto"])

    # dateto is treated as EXCLUSIVE.
    # Open-Meteo accepts YYYY-MM-DD dates.
    start_date = date_from.strftime("%Y-%m-%d")
    end_date = (date_to - pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    # Handle an empty/invalid date range.
    if date_from >= date_to:
        print(
            f"Skipping {location}: "
            f"datefrom ({date_from}) >= dateto ({date_to})"
        )
        return pd.DataFrame()

    print(
        f"Requesting {location}: "
        f"{start_date} -> {end_date} "
        f"({latitude}, {longitude})"
    )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": DAILY_VARIABLES,
    }

    try:
        responses = openmeteo.weather_api(URL, params=params)

        if not responses:
            print(f"No response for {location}")
            return pd.DataFrame()

        response = responses[0]

        daily = response.Daily()

        # -------------------------------------------------
        # Build date column
        # -------------------------------------------------

        dates = pd.date_range(
            start=pd.to_datetime(
                daily.Time(),
                unit="s",
                utc=True
            ),
            end=pd.to_datetime(
                daily.TimeEnd(),
                unit="s",
                utc=True
            ),
            freq=pd.Timedelta(
                seconds=daily.Interval()
            ),
            inclusive="left"
        )

        # -------------------------------------------------
        # Build dataframe dynamically
        #
        # This avoids having to manually write:
        # daily.Variables(0)
        # daily.Variables(1)
        # etc.
        # -------------------------------------------------

        daily_data = {
            "date": dates
        }

        for i, variable in enumerate(DAILY_VARIABLES):

            values = daily.Variables(i).ValuesAsNumpy()

            # Sunrise and sunset are Unix timestamps.
            if variable in ["sunrise", "sunset"]:
                values = pd.to_datetime(
                    values,
                    unit="s",
                    utc=True
                )

            daily_data[variable] = values

        weather_df = pd.DataFrame(daily_data)

        # -------------------------------------------------
        # Add original location/date information
        # -------------------------------------------------

        weather_df.insert(
            0,
            "location",
            location
        )

        weather_df.insert(
            1,
            "datefrom",
            row["datefrom"]
        )

        weather_df.insert(
            2,
            "dateto",
            row["dateto"]
        )

        weather_df.insert(
            3,
            "latitude",
            latitude
        )

        weather_df.insert(
            4,
            "longitude",
            longitude
        )

        # Add actual coordinates/model information returned
        # by Open-Meteo.
        weather_df["api_latitude"] = response.Latitude()
        weather_df["api_longitude"] = response.Longitude()
        weather_df["elevation"] = response.Elevation()
        weather_df["utc_offset_seconds"] = response.UtcOffsetSeconds()

        print(
            f"  Retrieved {len(weather_df)} daily records"
        )

        return weather_df

    except Exception as e:
        print(
            f"ERROR retrieving {location}: {e}"
        )
        return pd.DataFrame()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print(f"Reading {INPUT_CSV}...")

    locations_df = pd.read_csv(INPUT_CSV)

    required_columns = [
        "location",
        "datefrom",
        "dateto",
        "latitude",
        "longitude",
    ]

    missing_columns = [
        col
        for col in required_columns
        if col not in locations_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print(
        f"Found {len(locations_df)} location/date ranges."
    )

    all_weather = []

    for index, row in locations_df.iterrows():

        print(
            f"\n[{index + 1}/{len(locations_df)}]"
        )

        weather_df = get_weather(row)

        if not weather_df.empty:
            all_weather.append(weather_df)

        # Small delay between API requests.
        # The cache means repeated requests will not be
        # downloaded again.
        time.sleep(0.2)

    # -----------------------------------------------------
    # Combine all locations
    # -----------------------------------------------------

    if not all_weather:
        print("No weather data was retrieved.")
        return

    result_df = pd.concat(
        all_weather,
        ignore_index=True
    )

    # -----------------------------------------------------
    # Convert timestamps to readable CSV values
    # -----------------------------------------------------

    for column in ["sunrise", "sunset"]:
        if column in result_df.columns:
            result_df[column] = result_df[column].apply(
                lambda x: (
                    x.isoformat()
                    if pd.notna(x)
                    else ""
                )
            )

    # -----------------------------------------------------
    # Write output
    # -----------------------------------------------------

    result_df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    print(
        f"\nFinished."
        f"\nWritten {len(result_df)} rows to {OUTPUT_CSV}"
    )


if __name__ == "__main__":
    main()
