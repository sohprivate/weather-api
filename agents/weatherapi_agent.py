import os
import requests
from dotenv import load_dotenv
import logging
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from agents.base import WeatherAgent  # 共通インターフェース

# .env 読み込み
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAPIAgent(WeatherAgent):
    def fetch(self, location: dict) -> dict:
        """
        location: {
            "name": "千葉市",
            "lat": 35.6,
            "lon": 140.1
        }
        """
        api_key = os.getenv("WEATHERAPI_API_KEY")
        if not api_key:
            raise ValueError("WEATHERAPI_API_KEY が .env に設定されていません。")

        lat, lon = location["lat"], location["lon"]
        query = f"{lat},{lon}"

        url = "https://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": api_key,
            "q": query,
            "days": 3,  # 明日まで含める
            "lang": "ja"
        }

        try:
            res = requests.get(url, params=params)
            res.raise_for_status()
            data = res.json()

            forecast = data["forecast"]["forecastday"][1]  # 明日
            day = forecast["day"]
            max_temp = day["maxtemp_c"]
            min_temp = day["mintemp_c"]
            pop = day.get("daily_chance_of_rain", 0)

            return {
                "source": "WeatherAPI",
                "max_temp": float(max_temp),
                "min_temp": float(min_temp),
                "pop": int(pop)
            }

        except RequestException as e:
            logger.error(f"[WeatherAPI リクエストエラー] {e}")
        except JSONDecodeError as e:
            logger.error(f"[WeatherAPI JSONパースエラー] {e}")
        except Exception as e:
            logger.error(f"[WeatherAPI 予期せぬエラー] {e}")

        return {
            "source": "WeatherAPI",
            "max_temp": None,
            "min_temp": None,
            "pop": None
        }

def get_weatherapi_forecast():
    """
    WeatherAPI から予報を取得して返すサンプル関数。
    実際には API 呼び出しの処理や JSON パースを行い、
    max_temp, min_temp, pop, description などを抽出します。
    """
    try:
        # ここに実際の WeatherAPI 呼び出しロジックを実装する
        # 例:
        # response = requests.get("https://api.weatherapi.com/v1/forecast.json?...")
        # data = response.json()
        # max_temp = ...
        # min_temp = ...
        # pop = ...
        # など

        return {
            "source": "WeatherAPI",
            "max_temp": 19.5,
            "min_temp": 9.0,
            "pop": 55,
            "description": "晴れ時々曇り"
        }

    except Exception as e:
        logger.error(f"[WeatherAPI Error] {e}")
        return {
            "source": "WeatherAPI",
            "max_temp": None,
            "min_temp": None,
            "pop": None,
            "description": None
        }
