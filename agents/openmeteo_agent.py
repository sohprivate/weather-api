import requests
import logging
from agents.base import WeatherAgent  # 共通インターフェース

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenMeteoAgent(WeatherAgent):
    def fetch(self, location: dict) -> dict:
        lat = location["lat"]
        lon = location["lon"]
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "Asia/Tokyo"
        }

        try:
            res = requests.get(url, params=params)
            res.raise_for_status()
            data = res.json()

            return {
                "source": "Open-Meteo",
                "max_temp": float(data["daily"]["temperature_2m_max"][1]),
                "min_temp": float(data["daily"]["temperature_2m_min"][1]),
                "pop": int(data["daily"]["precipitation_probability_max"][1]),
                "description": None,
            }
        except Exception as e:
            logger.error(f"[Open-Meteo エラー] {e}")
            return {
                "source": "Open-Meteo",
                "max_temp": None,
                "min_temp": None,
                "pop": None,
                "description": None,
            }

def get_openmeteo_forecast():
    """
    Open-Meteo API から予報を取得して返すサンプル関数。
    実際にはAPI呼び出しの処理や JSON パースを行い、
    max_temp, min_temp, pop, description などを抽出して返してください。
    """
    try:
        # ここに実際の呼び出し処理などを実装する
        # 例:
        # response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=....")
        # data = response.json()
        # max_temp = ...
        # min_temp = ...
        # pop = ...
        # など

        return {
            "source": "OpenMeteo",
            "max_temp": 18.0,
            "min_temp": 11.0,
            "pop": 40,
            "description": "曇り時々晴れ"
        }

    except Exception as e:
        logger.error(f"[OpenMeteo Error] {e}")
        return {
            "source": "OpenMeteo",
            "max_temp": None,
            "min_temp": None,
            "pop": None,
            "description": None
        }
