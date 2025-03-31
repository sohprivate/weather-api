import requests
import logging
from datetime import datetime, timezone, timedelta
from agents.base import WeatherAgent  # 共通のインターフェースを継承

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JMAAgent(WeatherAgent):
    def fetch(self, location: dict) -> dict:
        """
        location: {
            "prefecture": "千葉県",
            "city": "千葉市",
            "lat": ...,
            "lon": ...
        }
        """
        pref_name = location["prefecture"]
        url = f"https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{self.get_area_code(pref_name)}.json"
        try:
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            return {
                "source": "JMA",
                "max_temp": None,
                "min_temp": None,
                "pop": None,
                "description": data.get("text", "（取得できませんでした）"),
            }
        except Exception as e:
            logger.error(f"[JMA データ取得エラー] {e}")
            return {
                "source": "JMA",
                "max_temp": None,
                "min_temp": None,
                "pop": None,
                "description": None,
            }

    def get_area_code(self, pref_name: str) -> str:
        area_codes = {
            "北海道": "016000",
            "青森県": "020000",
            "岩手県": "030000",
            "宮城県": "040000",
            "秋田県": "050000",
            "山形県": "060000",
            "福島県": "070000",
            "茨城県": "080000",
            "栃木県": "090000",
            "群馬県": "100000",
            "埼玉県": "110000",
            "千葉県": "120000",
            "東京都": "130000",
            "神奈川県": "140000",
            "新潟県": "150000",
            "富山県": "160000",
            "石川県": "170000",
            "福井県": "180000",
            "山梨県": "190000",
            "長野県": "200000",
            "岐阜県": "210000",
            "静岡県": "220000",
            "愛知県": "230000",
            "三重県": "240000",
            "滋賀県": "250000",
            "京都府": "260000",
            "大阪府": "270000",
            "兵庫県": "280000",
            "奈良県": "290000",
            "和歌山県": "300000",
            "鳥取県": "310000",
            "島根県": "320000",
            "岡山県": "330000",
            "広島県": "340000",
            "山口県": "350000",
            "徳島県": "360000",
            "香川県": "370000",
            "愛媛県": "380000",
            "高知県": "390000",
            "福岡県": "400000",
            "佐賀県": "410000",
            "長崎県": "420000",
            "熊本県": "430000",
            "大分県": "440000",
            "宮崎県": "450000",
            "鹿児島県": "461000",
            "沖縄県": "471000"
            
            # 他も追加可能
        }
        return area_codes.get(pref_name, "120000")

def get_jma_forecast():
    """
    気象庁（JMA）から天気予報を取得して返すサンプル関数。
    実際にはAPI呼び出しの処理や JSON パースを行い、
    max_temp, min_temp, pop, description などを抽出して返してください。
    """
    try:
        # ここに実際の気象庁API呼び出しなどの処理を実装
        # 例:
        # response = requests.get("https://www.jma.go.jp/bosai/forecast/data/forecast/...")
        # data = response.json()
        # max_temp = ...
        # etc...

        return {
            "source": "JMA",
            "max_temp": 20.5,
            "min_temp": 14.0,
            "pop": 60,
            "description": "晴れときどき雨"
        }

    except Exception as e:
        logger.error(f"[JMA Error] {e}")
        return {
            "source": "JMA",
            "max_temp": None,
            "min_temp": None,
            "pop": None,
            "description": None,
        }
