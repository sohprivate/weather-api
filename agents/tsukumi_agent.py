import requests
import logging
from agents.base import WeatherAgent  # 共通のインターフェースを継承

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TsukumiAgent(WeatherAgent):
    def fetch(self, location: dict) -> dict:
        """
        location: {
            "name": "千葉県",
            "lat": 35.6,
            "lon": 140.1,
            "city_code": "120010" ←これが必要！
        }
        """
        city_code = location.get("city_code", "120010")  # デフォルト千葉市
        url = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            forecast = data["forecasts"][1]  # 明日

            max_temp = forecast["temperature"]["max"]["celsius"]
            min_temp = forecast["temperature"]["min"]["celsius"]

            rain_chances = forecast["chanceOfRain"]
            pop_values = [
                int(v.replace("%", "")) for v in rain_chances.values() if v != "--"
            ]
            avg_pop = int(sum(pop_values) / len(pop_values)) if pop_values else 0

            return {
                "source": "Tsukumijima",
                "max_temp": float(max_temp) if max_temp else None,
                "min_temp": float(min_temp) if min_temp else None,
                "pop": avg_pop,
            }

        except Exception as e:
            logger.error(f"[Tsukumijima Error] {e}")
            return {
                "source": "Tsukumijima",
                "max_temp": None,
                "min_temp": None,
                "pop": None,
            }

def get_tsukumi_forecast():
    """
    津久見エリアの天気予報を返す処理 (仮の例)
    ここで実際のAPI呼び出し処理などを行う
    """
    return {
        "source": "TsukumiAPI",
        "max_temp": 18.0,
        "min_temp": 10.0,
        "pop": 70,
        "description": "晴れのち曇り"
    }
