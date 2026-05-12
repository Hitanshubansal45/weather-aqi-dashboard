CREATE TABLE weatherdata (
    id SERIAL PRIMARY KEY,
    temperature FLOAT, humidity INT, pressure INT,
    wind_speed FLOAT, weather_desc VARCHAR(100),
    sunrise TEXT, sunset TEXT, city VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE aqidata (
    id SERIAL PRIMARY KEY,
    aqi INT, pm2_5 FLOAT, pm10 FLOAT, no2 FLOAT, o3 FLOAT,
    city VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE forecastdata (
    id SERIAL PRIMARY KEY,
    forecast_date DATE, day_name VARCHAR(20),
    temp FLOAT, weather_desc VARCHAR(100),
    pop FLOAT, city VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT NOW()
);