let session;

async function loadModel(){
    session=await ort.InferenceSession.create("./model/model.onnx");
    console.log("Model loaded");
}

// ---------------------------------------------------------------------
// Exact feature order the model was trained on (from train.py's
// "Features used:" printout). ONNX input order must match this exactly.
// ---------------------------------------------------------------------
const FEATURE_ORDER = [
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
  "elevation"
];

// Per-feature medians computed from dataset.csv via get_medians.py,
// matching train.py's X.fillna(X.median(numeric_only=True)) imputation.
const FEATURE_MEDIANS = {
  "no2": 14.8,
  "o3": 48.1,
  "pm10": 19.3,
  "pm25": 10.25,
  "temperature_2m_max": 17.8,
  "apparent_temperature_max": 16.216,
  "apparent_temperature_min": 8.8955,
  "daylight_duration": 45048.285,
  "sunshine_duration": 35758.13,
  "rain_sum": 0.1,
  "snowfall_sum": 0.0,
  "precipitation_sum": 0.2,
  "precipitation_hours": 1.0,
  "wind_speed_10m_max": 18.3565,
  "wind_gusts_10m_max": 38.52,
  "wind_direction_10m_dominant": 218.418,
  "shortwave_radiation_sum": 14.84,
  "et0_fao_evapotranspiration": 2.7709,
  "apparent_temperature_mean": 12.1228,
  "cloud_cover_mean": 61.0417,
  "cloud_cover_max": 100.0,
  "cloud_cover_min": 1.0,
  "dew_point_2m_min": 6.225,
  "dew_point_2m_max": 10.95,
  "dew_point_2m_mean": 8.7292,
  "et0_fao_evapotranspiration_sum": 2.7709,
  "relative_humidity_2m_mean": 76.1223,
  "relative_humidity_2m_max": 92.0858,
  "relative_humidity_2m_min": 57.2869,
  "snowfall_water_equivalent_sum": 0.0,
  "pressure_msl_mean": 1015.25,
  "pressure_msl_max": 1017.8,
  "pressure_msl_min": 1012.4,
  "surface_pressure_mean": 1008.0655,
  "surface_pressure_max": 1010.8518,
  "surface_pressure_min": 1005.5605,
  "wind_gusts_10m_mean": 25.0275,
  "wind_speed_10m_mean": 11.875,
  "wind_gusts_10m_min": 11.16,
  "wind_speed_10m_min": 5.5489,
  "wet_bulb_temperature_2m_mean": 11.598,
  "wet_bulb_temperature_2m_max": 13.5789,
  "wet_bulb_temperature_2m_min": 8.7806,
  "vapour_pressure_deficit_max": 0.9111,
  "temperature_2m_min": 10.95,
  "temperature_2m_mean": 14.7281,
  "elevation": 43.0
};

// Daily weather variables to request (same list as the project's openmeteo.js)
const DAILY_WEATHER_VARS = [
  "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
  "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean",
  "daylight_duration", "sunshine_duration",
  "rain_sum", "snowfall_sum", "precipitation_sum", "precipitation_hours",
  "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
  "shortwave_radiation_sum",
  "et0_fao_evapotranspiration", "et0_fao_evapotranspiration_sum",
  "cloud_cover_mean", "cloud_cover_max", "cloud_cover_min",
  "dew_point_2m_mean", "dew_point_2m_max", "dew_point_2m_min",
  "relative_humidity_2m_mean", "relative_humidity_2m_max", "relative_humidity_2m_min",
  "snowfall_water_equivalent_sum",
  "pressure_msl_mean", "pressure_msl_max", "pressure_msl_min",
  "surface_pressure_mean", "surface_pressure_max", "surface_pressure_min",
  "wind_gusts_10m_mean", "wind_speed_10m_mean", "wind_gusts_10m_min", "wind_speed_10m_min",
  "wet_bulb_temperature_2m_mean", "wet_bulb_temperature_2m_max", "wet_bulb_temperature_2m_min",
  "vapour_pressure_deficit_max"
];

// Hourly AQ variables (Open-Meteo air-quality API names differ slightly
// from the training column names: nitrogen_dioxide -> no2, ozone -> o3,
// pm2_5 -> pm25)
const HOURLY_AQ_VARS = ["nitrogen_dioxide", "ozone", "pm10", "pm2_5"];

// Known event-location cities pulled from the historical location list,
// so the dropdown is pre-populated without needing a live geocode call.
const KNOWN_CITIES = [
  { name: "Porto", lat: 41.14850365, lon: -8.6109653 },
  { name: "Copenhagen", lat: 55.6867243, lon: 12.5700724 },
  { name: "Paris", lat: 48.8534951, lon: 2.3483915 },
  { name: "Cologne", lat: 50.938361, lon: 6.959974 },
  { name: "Atlanta", lat: 33.7544657, lon: -84.3898151 },
  { name: "Fort Worth", lat: 32.753177, lon: -97.3327459 },
  { name: "Rio de Janeiro", lat: -22.9110137, lon: -43.2093727 },
  { name: "Rotterdam", lat: 51.9244424, lon: 4.47775 },
  { name: "Cluj-Napoca", lat: 46.769379, lon: 23.5899542 },
  { name: "Kraków", lat: 50.0469432, lon: 19.9971534 },
  { name: "Valletta", lat: 35.8989979, lon: 14.5136607 },
  { name: "Budapest", lat: 47.4978789, lon: 19.0402383 },
  { name: "Chek Lap Kok", lat: 22.3154395, lon: 113.9351269 },
  { name: "Chengdu", lat: 30.659867, lon: 104.063315 },
  { name: "Stockholm", lat: 59.3251172, lon: 18.0710935 },
  { name: "London", lat: 51.5074456, lon: -0.1277653 },
  { name: "Riyadh", lat: 24.638916, lon: 46.7160104 },
  { name: "Austin", lat: 30.2711286, lon: -97.7436995 },
  { name: "Dallas", lat: 32.7762719, lon: -96.7968559 },
  { name: "Melbourne", lat: -37.8142454, lon: 144.9631732 },
  { name: "Lisbon", lat: 38.7077507, lon: -9.1365919 },
  { name: "Katowice", lat: 50.2137315, lon: 19.0058848 },
  { name: "Shanghai", lat: 31.2312707, lon: 121.4700152 },
  { name: "Sentosa", lat: 1.249689, lon: 103.8297534 },
  { name: "Bucharest", lat: 44.4361414, lon: 26.102684 },
  { name: "Abu Dhabi, UAE", lat: 24.4538352, lon: 54.3774014 },
  { name: "Sydney", lat: -33.8698439, lon: 151.2082848 },
  { name: "Washington, D.C., US", lat: 38.8950982, lon: -77.0363849 },
  { name: "Antwerp", lat: 51.2211097, lon: 4.3997081 },
  { name: "Düsseldorf", lat: 51.2254018, lon: 6.7763137 },
  { name: "Moscow", lat: 55.625578, lon: 37.6063916 },
  { name: "Beijing", lat: 39.9057136, lon: 116.3912972 },
  { name: "Belek", lat: 36.8633459, lon: 31.0578184 },
  { name: "Malmö", lat: 55.6052931, lon: 13.0001566 },
  { name: "Berlin", lat: 52.5173885, lon: 13.3951309 },
  { name: "Chicago", lat: 41.8755616, lon: -87.6244212 },
  { name: "Los Angeles", lat: 34.0536909, lon: -118.242766 },
  { name: "Charleroi", lat: 50.4116233, lon: 4.444528 },
  { name: "Champagne-au-Mont-d'Or", lat: 45.7954913, lon: 4.789458 },
  { name: "Saint-Amand-les-Eaux", lat: 50.4491519, lon: 3.4281142 }
];

let selectedLocation = null; // { name, lat, lon }
let selectedOffset = null;   // 0..4

// ---------------------------------------------------------------------
// UI wiring
// ---------------------------------------------------------------------

// Cut off long geocoded names instead of letting them overflow/wrap
function truncateName(str, maxLen = 55) {
  if (!str || str.length <= maxLen) return str;
  return str.slice(0, maxLen - 1).trimEnd() + "...";
}

function populateCityDropdown() {
  const select = document.getElementById("citySelect");
  KNOWN_CITIES
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach(city => {
      const opt = document.createElement("option");
      opt.value = city.name;
      opt.textContent = city.name;
      opt.dataset.lat = city.lat;
      opt.dataset.lon = city.lon;
      select.appendChild(opt);
    });

  select.addEventListener("change", () => {
    const opt = select.selectedOptions[0];
    if (!opt || !opt.value) {
      selectedLocation = null;
    } else {
      selectedLocation = {
        name: opt.value,
        lat: parseFloat(opt.dataset.lat),
        lon: parseFloat(opt.dataset.lon)
      };
    }
    document.getElementById("citySearch").value = "";
    document.getElementById("searchResults").innerHTML = "";
    updatePredictButtonState();
  });
}

async function geocodeCity(query) {
  const url = "https://nominatim.openstreetmap.org/search";
  const params = new URLSearchParams({ q: query, format: "json", limit: 5 });
  const response = await fetch(`${url}?${params}`);
  if (!response.ok) throw new Error(`Geocoding failed: ${response.status}`);
  return response.json();
}

function wireCitySearch() {
  const searchBtn = document.getElementById("searchBtn");
  const searchInput = document.getElementById("citySearch");
  const resultsBox = document.getElementById("searchResults");

  async function doSearch() {
    const query = searchInput.value.trim();
    if (!query) return;
    resultsBox.innerHTML = "Searching...";
    try {
      const results = await geocodeCity(query);
      resultsBox.innerHTML = "";
      if (!results.length) {
        resultsBox.innerHTML = "<div class='search-result-item'>No results found</div>";
        return;
      }
      results.forEach(r => {
        const item = document.createElement("div");
        item.className = "search-result-item";
        item.textContent = truncateName(r.display_name);
        item.title = r.display_name; // full name on hover
        item.addEventListener("click", () => {
          selectedLocation = {
            name: r.display_name,
            lat: parseFloat(r.lat),
            lon: parseFloat(r.lon)
          };
          document.getElementById("citySelect").value = "";
          // Show the picked city right in the search box, truncated if long
          searchInput.value = truncateName(r.display_name);
          searchInput.title = r.display_name;
          resultsBox.innerHTML = "";
          updatePredictButtonState();
        });
        resultsBox.appendChild(item);
      });
    } catch (err) {
      resultsBox.innerHTML = "<div class='search-result-item'>Search failed, try again</div>";
      console.error(err);
    }
  }

  searchBtn.addEventListener("click", doSearch);
  searchInput.addEventListener("keydown", e => {
    if (e.key === "Enter") { e.preventDefault(); doSearch(); }
  });
}

function wireDayButtons() {
  const buttons = document.querySelectorAll(".day-btn");
  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");
      selectedOffset = parseInt(btn.dataset.offset, 10);
      updatePredictButtonState();
    });
  });
}

function offsetToDateString(offset) {
  const d = new Date();
  d.setDate(d.getDate() + offset);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`; // local calendar date, not UTC
}

function updatePredictButtonState() {
  const predictBtn = document.getElementById("predictBtn");
  predictBtn.disabled = !(selectedLocation && selectedOffset !== null);
}

// ---------------------------------------------------------------------
// Forecast fetching
// ---------------------------------------------------------------------
async function fetchWeatherForecast(lat, lon, dayIndex) {
  const url = "https://api.open-meteo.com/v1/forecast";
  const params = new URLSearchParams({
    latitude: lat,
    longitude: lon,
    daily: DAILY_WEATHER_VARS.join(","),
    forecast_days: 5,
    timezone: "auto"
  });

  const response = await fetch(`${url}?${params}`);
  if (!response.ok) throw new Error(`Weather forecast failed: ${response.status}`);
  const data = await response.json();

  const daily = data.daily;
  const values = {};
  DAILY_WEATHER_VARS.forEach(name => {
    values[name] = daily[name] ? daily[name][dayIndex] : null;
  });
  values.elevation = data.elevation;

  return values;
}

async function fetchAirQualityForecast(lat, lon, dayIndex) {
  const url = "https://air-quality-api.open-meteo.com/v1/air-quality";
  const params = new URLSearchParams({
    latitude: lat,
    longitude: lon,
    hourly: HOURLY_AQ_VARS.join(","),
    forecast_days: 5,
    timezone: "auto"
  });

  const response = await fetch(`${url}?${params}`);
  if (!response.ok) throw new Error(`Air quality forecast failed: ${response.status}`);
  const data = await response.json();

  const hourly = data.hourly;

  // hourly.time always starts at hour 0 of "today" in the location's own
  // local timezone (timezone=auto), so day N is simply hours [N*24, N*24+24).
  // Matching by parsed date string is timezone-fragile (device tz vs venue
  // tz disagree near midnight), so we slice by index instead.
  const startIdx = dayIndex * 24;
  const endIdx = startIdx + 24;

  const dailyAverages = {};
  HOURLY_AQ_VARS.forEach(name => {
    const series = hourly[name] || [];
    const dayValues = series
      .slice(startIdx, endIdx)
      .filter(v => v !== null && v !== undefined && !Number.isNaN(v));

    dailyAverages[name] = dayValues.length
      ? dayValues.reduce((a, b) => a + b, 0) / dayValues.length
      : null;
  });

  return dailyAverages;
}

// ---------------------------------------------------------------------
// Feature assembly + inference
// ---------------------------------------------------------------------
function buildFeatureRows(weather, aq) {
  const lookup = {
    no2: aq.nitrogen_dioxide,
    o3: aq.ozone,
    pm10: aq.pm10,
    pm25: aq.pm2_5,
    ...weather
  };

  return FEATURE_ORDER.map(name => {
    const raw = lookup[name];
    const missing = raw === null || raw === undefined || Number.isNaN(raw);
    return {
      name,
      value: missing ? FEATURE_MEDIANS[name] : raw,
      source: missing ? "median" : "forecast"
    };
  });
}

function featureVectorFromRows(rows) {
  return rows.map(r => r.value);
}

async function runPrediction(featureVector) {
  const inputTensor = new ort.Tensor(
    "float32",
    Float32Array.from(featureVector),
    [1, featureVector.length]
  );

  const feeds = {};
  const inputName = session.inputNames[0];
  feeds[inputName] = inputTensor;

  const results = await session.run(feeds);
  const outputName = session.outputNames[0];
  const outputData = results[outputName].data;

  return outputData[0];
}

function renderDataPanel(rows) {
  const panel = document.getElementById("dataPanel");
  const body = document.getElementById("dataTableBody");
  body.innerHTML = "";

  rows.forEach(row => {
    const tr = document.createElement("tr");

    const nameTd = document.createElement("td");
    nameTd.textContent = row.name;

    const valueTd = document.createElement("td");
    valueTd.textContent = typeof row.value === "number" ? row.value.toFixed(3) : row.value;

    const sourceTd = document.createElement("td");
    const tag = document.createElement("span");
    tag.className = "source-tag" + (row.source === "median" ? " median" : "");
    tag.textContent = row.source === "median" ? "median fallback" : "forecast";
    sourceTd.appendChild(tag);

    tr.appendChild(nameTd);
    tr.appendChild(valueTd);
    tr.appendChild(sourceTd);
    body.appendChild(tr);
  });

  panel.classList.remove("hidden");
  panel.classList.add("visible");
}

function wireDataPanelToggle() {
  const toggle = document.getElementById("dataToggle");
  const wrap = document.getElementById("dataTableWrap");
  const icon = document.getElementById("dataToggleIcon");

  toggle.addEventListener("click", () => {
    const isOpen = wrap.classList.toggle("visible");
    icon.classList.toggle("open", isOpen);
  });
}

async function handlePredictClick() {
  const statusEl = document.getElementById("status");
  const resultBox = document.getElementById("resultBox");
  const resultValue = document.getElementById("resultValue");
  const predictBtn = document.getElementById("predictBtn");
  const dataPanel = document.getElementById("dataPanel");
  const dataTableWrap = document.getElementById("dataTableWrap");
  const dataToggleIcon = document.getElementById("dataToggleIcon");
  const sidePlaceholder = document.getElementById("sidePlaceholder");

  if (!selectedLocation || selectedOffset === null) return;

  predictBtn.disabled = true;
  resultBox.classList.remove("visible");
  dataPanel.classList.remove("visible");
  dataTableWrap.classList.remove("visible");
  dataToggleIcon.classList.remove("open");
  sidePlaceholder.classList.add("hidden");
  statusEl.textContent = "Fetching weather forecast...";

  try {
    const [weather, aq] = await Promise.all([
      fetchWeatherForecast(selectedLocation.lat, selectedLocation.lon, selectedOffset),
      fetchAirQualityForecast(selectedLocation.lat, selectedLocation.lon, selectedOffset)
    ]);

    statusEl.textContent = "Running model...";
    const rows = buildFeatureRows(weather, aq);
    const featureVector = featureVectorFromRows(rows);
    const prediction = await runPrediction(featureVector);

    resultValue.textContent = prediction.toFixed(2);
    resultBox.classList.add("visible");
    renderDataPanel(rows);
    statusEl.textContent = "";
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Prediction failed — see console for details.";
    sidePlaceholder.classList.remove("hidden");
  } finally {
    predictBtn.disabled = false;
  }
}

// ---------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------
window.addEventListener("DOMContentLoaded", async () => {
  populateCityDropdown();
  wireCitySearch();
  wireDayButtons();
  wireDataPanelToggle();
  document.getElementById("predictBtn").addEventListener("click", handlePredictClick);

  document.getElementById("status").textContent = "Loading model...";
  try {
    await loadModel();
    document.getElementById("status").textContent = "";
  } catch (err) {
    console.error(err);
    document.getElementById("status").textContent = "Failed to load model.onnx — check the ./model path.";
  }
});