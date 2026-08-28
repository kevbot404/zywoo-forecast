const url = "https://air-quality-api.open-meteo.com/v1/air-quality";

const params = new URLSearchParams({
  latitude: 52.52,
  longitude: 13.41,

  hourly: [
    "ozone",
    "pm10",
    "pm2_5"
  ].join(","),

  past_days: 1
});

async function getAirQuality() {
  try {
    const response = await fetch(`${url}?${params}`);

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const data = await response.json();

    console.log(
      `Coordinates: ${data.latitude}°N ${data.longitude}°E`
    );

    console.log(
      `Elevation: ${data.elevation} m asl`
    );

    console.log(
      `Timezone: ${data.timezone}`
    );

    console.log(
      `UTC offset: ${data.utc_offset_seconds}s`
    );

    const hourly = data.hourly;

    // Convert Open-Meteo's column-based response
    // into an array of objects, similar to a pandas DataFrame.
    const hourlyData = hourly.time.map((date, index) => ({
      date,

      ozone:
        hourly.ozone[index],

      pm10:
        hourly.pm10[index],

      pm2_5:
        hourly.pm2_5[index]
    }));

    console.log("\nHourly air quality data:\n");
    console.table(hourlyData);

    return hourlyData;

  } catch (error) {
    console.error(
      "Failed to fetch air quality data:",
      error
    );

    throw error;
  }
}

// Run
getAirQuality();