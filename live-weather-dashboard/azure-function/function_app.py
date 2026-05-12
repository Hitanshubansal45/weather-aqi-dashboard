import azure.functions as func
import requests
import psycopg2
import logging
import datetime

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */10 * * * *", arg_name="mytimer")
def weather_function(mytimer: func.TimerRequest) -> None:

    logging.info("Function started")

    WAQI_TOKEN = ["WAQI_TOKEN"]
    VC_KEY = ["VC_KEY"]
    DATABASE_URL = ["DATABASE_URL"]

    cities = [
        {"name": "Chandigarh", "waqi": "@10412"},
        {"name": "Delhi", "waqi": "@11320"},
        {"name": "Mumbai", "waqi": "@11284"},
        {"name": "Bengaluru", "waqi": "@8686"},
        {"name": "Shillong", "waqi": "@11242"}
    ]

    def vc_icon_to_desc(icon):
        mapping = {
            "clear-day": "clear sky", "clear-night": "clear sky",
            "partly-cloudy-day": "few clouds", "partly-cloudy-night": "few clouds",
            "cloudy": "broken clouds", "wind": "broken clouds",
            "rain": "rain", "showers-day": "shower rain", "showers-night": "shower rain",
            "thunder-rain": "thunderstorm", "thunder-showers-day": "thunderstorm",
            "snow": "snow", "snow-showers-day": "snow",
            "fog": "fog"
        }
        return mapping.get(icon, "clear sky")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM forecastdata")

        for city in cities:
            CITY = city["name"]
            WAQI_STATION = city["waqi"]

            # Visual Crossing — accurate weather + 7-day forecast
            vc_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{CITY},India?unitGroup=metric&key={VC_KEY}&include=current,days&iconSet=icons2"
            weather = requests.get(vc_url).json()

            current = weather["currentConditions"]
            temp = current["temp"]
            humidity = int(current["humidity"])
            pressure = int(current["pressure"])
            wind = current["windspeed"] / 3.6  # km/h → m/s
            desc = vc_icon_to_desc(current["icon"])
            sunrise_str = datetime.datetime.strptime(current["sunrise"], "%H:%M:%S").strftime("%I:%M %p")
            sunset_str = datetime.datetime.strptime(current["sunset"], "%H:%M:%S").strftime("%I:%M %p")

            # WAQI station-specific = real CPCB data
            aqi_url = f"https://api.waqi.info/feed/{WAQI_STATION}/?token={WAQI_TOKEN}"
            aqi_data = requests.get(aqi_url).json()

            if aqi_data["status"] == "ok":
                aqi_value = aqi_data["data"]["aqi"]
                iaqi = aqi_data["data"].get("iaqi", {})
                pm2_5 = iaqi.get("pm25", {}).get("v", 0)
                pm10 = iaqi.get("pm10", {}).get("v", 0)
                no2 = iaqi.get("no2", {}).get("v", 0)
                o3 = iaqi.get("o3", {}).get("v", 0)
            else:
                aqi_value = pm2_5 = pm10 = no2 = o3 = 0

            cursor.execute("""
            INSERT INTO weatherdata (temperature, humidity, pressure, wind_speed, weather_desc, sunrise, sunset, city)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (temp, humidity, pressure, wind, desc, sunrise_str, sunset_str, CITY))

            cursor.execute("""
            INSERT INTO aqidata (aqi, pm2_5, pm10, no2, o3, city)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (aqi_value, pm2_5, pm10, no2, o3, CITY))

            # 7-day forecast from Visual Crossing
            for day in weather["days"][:7]:
                forecast_date = datetime.date.fromisoformat(day["datetime"])
                day_name = forecast_date.strftime("%A")
                day_temp = day["tempmax"]
                day_desc = vc_icon_to_desc(day["icon"])
                day_pop = day.get("precipprob", 0) or 0

                cursor.execute("""
                INSERT INTO forecastdata (forecast_date, day_name, temp, weather_desc, pop, city)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (forecast_date, day_name, day_temp, day_desc, day_pop, CITY))

        conn.commit()
        conn.close()
        logging.info("Data inserted successfully")

    except Exception as e:
        logging.error(f"Error: {e}")