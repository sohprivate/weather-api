import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_openmeteo_forecast(lat: float = 35.632896, lon: float = 140.038996) -> dict:
    """
    Open-Meteo APIから明日の天気予報を取得し、
    max_temp, min_temp, pop（降水確率）を含む辞書を返す。

    Args:
        lat (float): 緯度
        lon (float): 経度

    Returns:
        dict: {
            "source": "Open-Meteo",
            "max_temp": float,
            "min_temp": float,
            "pop": int（%）
        }
    """
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

        max_temp = data["daily"]["temperature_2m_max"][1]
        min_temp = data["daily"]["temperature_2m_min"][1]
        pop = data["daily"]["precipitation_probability_max"][1]

        return {
            "source": "Open-Meteo",
            "max_temp": float(max_temp),
            "min_temp": float(min_temp),
            "pop": int(pop)
        }

    except Exception as e:
        logger.error(f"Open-Meteo API取得エラー: {e}")

    return {
        "source": "Open-Meteo",
        "max_temp": None,
        "min_temp": None,
        "pop": None
    }