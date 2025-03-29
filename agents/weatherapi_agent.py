import os
import requests
from dotenv import load_dotenv
import logging
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError

# .env 読み込み
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_weatherapi_forecast(location: str = "Chiba") -> dict:
    """
    WeatherAPI.com から指定地域の明日の天気予報を取得し、
    max_temp, min_temp, pop（降水確率）を含む辞書を返す。

    Args:
        location (str): 都市名や緯度経度（例: "Chiba" or "35.6,140.1"）

    Returns:
        dict: {
            "source": "WeatherAPI",
            "max_temp": float,
            "min_temp": float,
            "pop": int（%）
        }
    """
    api_key = os.getenv("WEATHERAPI_API_KEY")
    if not api_key:
        raise ValueError("WEATHERAPI_API_KEY が .env に設定されていません。")

    url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": location,
        "days": 3,       # 今日＋2日分（明日 = index 1）
        "lang": "ja"
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()

        forecast = data["forecast"]["forecastday"][1]  # 明日のデータ
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
        logger.error(f"WeatherAPI リクエストエラー: {e}")
    except JSONDecodeError as e:
        logger.error(f"JSONパースエラー: {e}")
    except Exception as e:
        logger.error(f"予期せぬエラー: {e}")

    return {
        "source": "WeatherAPI",
        "max_temp": None,
        "min_temp": None,
        "pop": None
    }