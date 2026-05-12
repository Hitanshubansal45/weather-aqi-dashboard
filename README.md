# Live Weather & Air Quality Dashboard

A real-time end-to-end data pipeline that fetches weather and air quality data for 5 Indian cities every 10 minutes and visualizes it in Power BI. Built with serverless architecture on Azure Functions, PostgreSQL on Supabase, and Power BI Desktop.

![Dashboard Preview](dashboard-screenshots/chandigarh.png)

## Architecture

![Architecture](architecture.png)

Data flows from three weather APIs through a Python Azure Function (timer-triggered every 10 minutes) into a Supabase PostgreSQL database. Power BI Desktop connects to the database via REST API and renders the interactive dashboard with multi-city slicer support.

## Tech Stack

- **Azure Functions** — Python 3.11 on Consumption (Flex) plan, timer-triggered every 10 minutes
- **Supabase** — Free-tier PostgreSQL with REST API and session pooler for IPv4 compatibility
- **Power BI Desktop** — Web connector with custom DAX measures and conditional formatting
- **APIs**:
  - Visual Crossing — accurate Indian city temperatures and 7-day forecast
  - WAQI — real Indian AQI from CPCB monitoring stations
  - Open-Meteo — sunrise / sunset times (no API key needed)

## Features

- Real-time weather monitoring for 5 Indian cities
- Multi-city slicer — instantly switch between Chandigarh, Delhi, Mumbai, Bengaluru, Shillong
- 7-day weather forecast with rain probability
- Indian AQI gauge (0-500 scale) with color-coded health alerts
- Dynamic weather icons that change based on conditions
- Pollutant tracking — PM2.5, PM10, NO2, O3 with WHO-standard color thresholds
- Auto-refreshing pipeline running 144 times per day per city
- Sunrise/sunset cards with IST timezone conversion

## Database Schema

Three tables in Supabase PostgreSQL, all linked to a CityList dimension table in Power BI:

```sql
weatherdata    -- current weather snapshots
aqidata        -- pollutant concentrations
forecastdata   -- 7-day forecast (refreshed every cycle)
```

See `supabase-schema.sql` for full DDL.

## Setup

### Prerequisites
- Azure account (free tier works)
- Supabase account (free)
- Visual Crossing API key (free, 1000 calls/day)
- WAQI token (free, 1000 calls/day)
- Power BI Desktop

### 1. Database setup
Run `supabase-schema.sql` in Supabase SQL Editor to create the three tables.

### 2. Deploy Azure Function
```bash
cd azure-function
# Update environment variables in Azure Portal:
# WAQI_TOKEN, VC_KEY, DATABASE_URL
func azure functionapp publish <your-function-app-name>
```

### 3. Open Power BI dashboard
Open `powerbi/LiveWeatherDashboard.pbix` in Power BI Desktop. Update the Supabase URLs and anon keys in the Web data sources.

## DAX Measures

Key custom measures used in the dashboard:

```dax
Latest AQI = MAXX(TOPN(1, AQIData, AQIData[recorded_at], DESC), AQIData[aqi])

AQI Status = SWITCH(TRUE(),
    [Latest AQI] <= 50, "Good",
    [Latest AQI] <= 100, "Satisfactory",
    [Latest AQI] <= 200, "Moderate",
    [Latest AQI] <= 300, "Poor",
    [Latest AQI] <= 400, "Very Poor",
    "Severe")

Last Updated = "Last Updated, " & FORMAT(MAX(WeatherData[recorded_at]) + (330/1440), "DD MMM, hh:mm AM/PM")
```

## Project Structure

```
live-weather-dashboard/
├── README.md
├── architecture.png
├── dashboard-screenshots/
│   ├── chandigarh.png
│   ├── delhi.png
│   └── mumbai.png
├── azure-function/
│   ├── function_app.py
│   ├── requirements.txt
│   └── host.json
├── powerbi/
│   └── LiveWeatherDashboard.pbix
└── supabase-schema.sql
```

## Challenges & Solutions

- **Azure SQL free tier vCore exhaustion** — migrated to Supabase PostgreSQL (no vCore limits)
- **IPv6 connection failures** — switched from direct connection to Supabase session pooler (IPv4)
- **Linux ODBC driver mismatch** — switched from pyodbc to psycopg2 for PostgreSQL
- **Inaccurate Indian AQI** — replaced OpenWeather AQI (European scale) with WAQI station-specific data (CPCB)
- **Cached old data in Power BI** — added `limit=1` parameter to URLs and DateTime type casting

## Roadmap

- [ ] Deploy to Power BI Service for live public URL
- [ ] Add city comparison view (side-by-side metrics)
- [ ] Historical trend analysis (7-day, 30-day views)
- [ ] Email alerts for severe AQI conditions
- [ ] Mobile-responsive layout

## License

MIT

## Author

Hitanshu Bansal — B.Tech student, aspiring data analyst.
