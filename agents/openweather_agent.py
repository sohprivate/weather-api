import os
import requests
from dotenv import load_dotenv
import logging
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from datetime import datetime, timedelta

# .env 読み込み
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_openweather_forecast(lat: float = 35.632896, lon: float = 140.038996) -> dict:
    """
    OpenWeatherMap One Call API 3.0 を使って、明日の天気（max_temp, min_temp, pop）を取得。
    
    Args:
        lat (float): 緯度
        lon (float): 経度

    Returns:
        dict: {
            "source": "OpenWeatherMap",
            "max_temp": float,
            "min_temp": float,
            "pop": int（%）
        }
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY が .env に設定されていません。")

    # URLを2.5のAPIに変更
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

        # 明日の日付を計算
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 明日の天気データを取得（3時間ごとのデータから必要なものを抽出）
        tomorrow_forecasts = [
            forecast for forecast in data["list"]
            if forecast["dt_txt"].startswith(tomorrow)  # 動的に明日の日付をチェック
        ]

        if not tomorrow_forecasts:
            raise ValueError("明日の天気データが見つかりません")

        # 最高気温と最低気温を計算
        max_temp = max(f["main"]["temp_max"] for f in tomorrow_forecasts)
        min_temp = min(f["main"]["temp_min"] for f in tomorrow_forecasts)
        # 降水確率の最大値を取得
        pop = max(forecast.get("pop", 0) for forecast in tomorrow_forecasts)

        return {
            "source": "OpenWeatherMap",
            "max_temp": float(max_temp),
            "min_temp": float(min_temp),
            "pop": int(pop * 100)
        }

    except RequestException as e:
        logger.error(f"OpenWeatherMap APIリクエストエラー: {e}")
    except JSONDecodeError as e:
        logger.error(f"JSONパースエラー: {e}")
    except Exception as e:
        logger.error(f"予期せぬエラー: {e}")

    return {
        "source": "OpenWeatherMap",
        "max_temp": None,
        "min_temp": None,
        "pop": None
    }