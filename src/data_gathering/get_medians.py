# get medians for js, so it can replace nan with them.

import pandas as pd
from src.preprocess import preprocess_features

DATA_PATH = "./data/dataset.csv"
TARGET = "rating"

FEATURE_ORDER = [
    "no2", "o3", "pm10", "pm25",
    "temperature_2m_max", "apparent_temperature_max", "apparent_temperature_min",
    "daylight_duration", "sunshine_duration",
    "rain_sum", "snowfall_sum", "precipitation_sum", "precipitation_hours",
    "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
    "shortwave_radiation_sum", "et0_fao_evapotranspiration", "apparent_temperature_mean",
    "cloud_cover_mean", "cloud_cover_max", "cloud_cover_min",
    "dew_point_2m_min", "dew_point_2m_max", "dew_point_2m_mean",
    "et0_fao_evapotranspiration_sum",
    "relative_humidity_2m_mean", "relative_humidity_2m_max", "relative_humidity_2m_min",
    "snowfall_water_equivalent_sum",
    "pressure_msl_mean", "pressure_msl_max", "pressure_msl_min",
    "surface_pressure_mean", "surface_pressure_max", "surface_pressure_min",
    "wind_gusts_10m_mean", "wind_speed_10m_mean", "wind_gusts_10m_min", "wind_speed_10m_min",
    "wet_bulb_temperature_2m_mean", "wet_bulb_temperature_2m_max", "wet_bulb_temperature_2m_min",
    "vapour_pressure_deficit_max",
    "temperature_2m_min", "temperature_2m_mean",
    "elevation",
]

df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=[TARGET])

X = preprocess_features(df)
X = X.drop(columns=[TARGET], errors="ignore")

medians = X.median(numeric_only=True)

print("const FEATURE_MEDIANS = {")
for name in FEATURE_ORDER:
    val = medians.get(name)
    val = 0 if pd.isna(val) else round(float(val), 4)
    print(f'  "{name}": {val},')
print("};")
