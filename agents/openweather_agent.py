from agents.base import WeatherAgent
import os
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenWeatherAgent(WeatherAgent):
    def fetch(self, location: dict) -> dict:
        """
        location: {
            "name": "千葉市",
            "lat": 35.6,
            "lon": 140.1
        }
        """
        lat = location["lat"]
        lon = location["lon"]
        api_key = os.getenv("OPENWEATHER_API_KEY")

        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "lang": "ja",
            "appid": api_key
        }

        try:
            res = requests.get(url, params=params)
            res.raise_for_status()
            data = res.json()

            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            tomorrow_forecasts = [
                forecast for forecast in data["list"]
                if forecast["dt_txt"].startswith(tomorrow)
            ]

            if not tomorrow_forecasts:
                raise ValueError("明日の天気データが見つかりません")

            max_temp = max(f["main"]["temp_max"] for f in tomorrow_forecasts)
            min_temp = min(f["main"]["temp_min"] for f in tomorrow_forecasts)
            pop = max(forecast.get("pop", 0) for forecast in tomorrow_forecasts)

            return {
                "source": "OpenWeatherMap",
                "max_temp": float(max_temp),
                "min_temp": float(min_temp),
                "pop": int(pop * 100)
            }

        except Exception as e:
            logger.error(f"[OpenWeather APIエラー] {e}")
            return {
                "source": "OpenWeatherMap",
                "max_temp": None,
                "min_temp": None,
                "pop": None
            }

def get_openweather_forecast():
    """
    OpenWeatherMap から予報を取得して返すサンプル関数。
    実際にはAPIキーや location パラメータを受け取るなどの処理を実装してください。
    """
    try:
        # サンプルとして APIリクエストを行う例
        # url = "https://api.openweathermap.org/data/2.5/forecast?lat=...&lon=...&appid=..."
        # response = requests.get(url)
        # response.raise_for_status()
        # data = response.json()
        # ここで data から max_temp, min_temp, pop などを抽出する

        return {
            "source": "OpenWeather",
            "max_temp": 20.0,
            "min_temp": 12.0,
            "pop": 30,
            "description": "晴れのち雨"
        }

    except Exception as e:
        logger.error(f"[OpenWeather Error] {e}")
        return {
            "source": "OpenWeather",
            "max_temp": None,
            "min_temp": None,
            "pop": None,
            "description": None
        }
