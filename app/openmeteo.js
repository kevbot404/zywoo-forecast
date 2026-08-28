const url = "https://api.open-meteo.com/v1/forecast";

const params = new URLSearchParams({
  latitude: 52.52,
  longitude: 13.41,

  daily: [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "apparent_temperature_max",
    "apparent_temperature_min",
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
    "dew_point_2m_mean",
    "dew_point_2m_max",
    "dew_point_2m_min",
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
    "vapour_pressure_deficit_max"
  ].join(",")
});

async function getWeather() {
  try {
    const response = await fetch(`${url}?${params}`);

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const data = await response.json();

    console.log(
      `Coordinates: ${data.latitude}°N ${data.longitude}°E`
    );

    console.log(`Elevation: ${data.elevation} m asl`);

    console.log(
      `Timezone: ${data.timezone}`
    );

    console.log(
      `UTC offset: ${data.utc_offset_seconds}s`
    );

    const daily = data.daily;

    // Convert Open-Meteo's column-based response
    // into an array of objects, similar to a pandas DataFrame.
    const dailyData = daily.time.map((date, index) => ({
      date,

      temperature_2m_max:
        daily.temperature_2m_max[index],

      temperature_2m_min:
        daily.temperature_2m_min[index],

      temperature_2m_mean:
        daily.temperature_2m_mean[index],

      apparent_temperature_max:
        daily.apparent_temperature_max[index],

      apparent_temperature_min:
        daily.apparent_temperature_min[index],

      daylight_duration:
        daily.daylight_duration[index],

      sunshine_duration:
        daily.sunshine_duration[index],

      rain_sum:
        daily.rain_sum[index],

      snowfall_sum:
        daily.snowfall_sum[index],

      precipitation_sum:
        daily.precipitation_sum[index],

      precipitation_hours:
        daily.precipitation_hours[index],

      wind_speed_10m_max:
        daily.wind_speed_10m_max[index],

      wind_gusts_10m_max:
        daily.wind_gusts_10m_max[index],

      wind_direction_10m_dominant:
        daily.wind_direction_10m_dominant[index],

      shortwave_radiation_sum:
        daily.shortwave_radiation_sum[index],

      et0_fao_evapotranspiration:
        daily.et0_fao_evapotranspiration[index],

      apparent_temperature_mean:
        daily.apparent_temperature_mean[index],

      cloud_cover_mean:
        daily.cloud_cover_mean[index],

      cloud_cover_max:
        daily.cloud_cover_max[index],

      cloud_cover_min:
        daily.cloud_cover_min[index],

      dew_point_2m_mean:
        daily.dew_point_2m_mean[index],

      dew_point_2m_max:
        daily.dew_point_2m_max[index],

      dew_point_2m_min:
        daily.dew_point_2m_min[index],

      et0_fao_evapotranspiration_sum:
        daily.et0_fao_evapotranspiration_sum[index],

      relative_humidity_2m_mean:
        daily.relative_humidity_2m_mean[index],

      relative_humidity_2m_max:
        daily.relative_humidity_2m_max[index],

      relative_humidity_2m_min:
        daily.relative_humidity_2m_min[index],

      snowfall_water_equivalent_sum:
        daily.snowfall_water_equivalent_sum[index],

      pressure_msl_mean:
        daily.pressure_msl_mean[index],

      pressure_msl_max:
        daily.pressure_msl_max[index],

      pressure_msl_min:
        daily.pressure_msl_min[index],

      surface_pressure_mean:
        daily.surface_pressure_mean[index],

      surface_pressure_max:
        daily.surface_pressure_max[index],

      surface_pressure_min:
        daily.surface_pressure_min[index],

      wind_gusts_10m_mean:
        daily.wind_gusts_10m_mean[index],

      wind_speed_10m_mean:
        daily.wind_speed_10m_mean[index],

      wind_gusts_10m_min:
        daily.wind_gusts_10m_min[index],

      wind_speed_10m_min:
        daily.wind_speed_10m_min[index],

      wet_bulb_temperature_2m_mean:
        daily.wet_bulb_temperature_2m_mean[index],

      wet_bulb_temperature_2m_max:
        daily.wet_bulb_temperature_2m_max[index],

      wet_bulb_temperature_2m_min:
        daily.wet_bulb_temperature_2m_min[index],

      vapour_pressure_deficit_max:
        daily.vapour_pressure_deficit_max[index]
    }));

    console.log("\nDaily data:\n");
    console.table(dailyData);

    return dailyData;

  } catch (error) {
    console.error("Failed to fetch weather data:", error);
    throw error;
  }
}

// Run
getWeather();