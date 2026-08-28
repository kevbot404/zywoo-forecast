# zywoo-forecast

ML project exploring whether environmental conditions can help predict ZywOo's CS2 performance.

- CS2 dataset gathered from HLTV using private scraper.

- Historical air quality data gathered from OpenAQ.

- Historical weather data gathered from Open-Meteo.

- Forecast data gathered from Open-Meteo.

- Limitation: model wasn't trained on historical forecast data.

##

<p align="center">
  <img src="./media/tweet.png" alt="Interface" style="width: 70%;">
</p>

<p align="center">
  https://www.journals.uchicago.edu/doi/full/10.1086/698728
</p>

## Features Used for Prediction

The model uses the following features to predict rating:

- `map`
- `co`
- `no2`
- `o3`
- `pm10`
- `pm25`
- `so2`
- `temperature_2m_max`
- `apparent_temperature_max`
- `apparent_temperature_min`
- `daylight_duration`
- `sunshine_duration`
- `rain_sum`
- `snowfall_sum`
- `precipitation_sum`
- `precipitation_hours`
- `wind_speed_10m_max`
- `wind_gusts_10m_max`
- `wind_direction_10m_dominant`
- `shortwave_radiation_sum`
- `et0_fao_evapotranspiration`
- `apparent_temperature_mean`
- `cloud_cover_mean`
- `cloud_cover_max`
- `cloud_cover_min`
- `dew_point_2m_min`
- `dew_point_2m_max`
- `dew_point_2m_mean`
- `et0_fao_evapotranspiration_sum`
- `relative_humidity_2m_mean`
- `relative_humidity_2m_max`
- `relative_humidity_2m_min`
- `snowfall_water_equivalent_sum`
- `pressure_msl_mean`
- `pressure_msl_max`
- `pressure_msl_min`
- `surface_pressure_mean`
- `surface_pressure_max`
- `surface_pressure_min`
- `wind_gusts_10m_mean`
- `wind_speed_10m_mean`
- `wind_gusts_10m_min`
- `wind_speed_10m_min`
- `wet_bulb_temperature_2m_mean`
- `wet_bulb_temperature_2m_max`
- `wet_bulb_temperature_2m_min`
- `vapour_pressure_deficit_max`
- `temperature_2m_min`
- `temperature_2m_mean`
- `elevation`
