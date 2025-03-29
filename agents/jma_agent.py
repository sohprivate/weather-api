import requests
import xml.etree.ElementTree as ET
import logging
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_jma_forecast(pref_name: str = "千葉県") -> dict:
    """
    気象庁の防災情報XMLフィードから、指定府県の天気概況を取得。
    
    Args:
        pref_name (str): 取得対象の府県名（例: "千葉県"）

    Returns:
        dict: {
            "source": "JMA",
            "max_temp": None,
            "min_temp": None,
            "pop": None,
            "description": str（概況文）
        }
    """
    # 現在の日本時間を取得
    jst = timezone(timedelta(hours=+9))
    now = datetime.now(jst)
    today = now.strftime("%Y%m%d")

    # 地方概況発表用のURL
    url = f"https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{get_area_code(pref_name)}.json"

    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()

        # 正規化された形式に合わせて返却
        return {
            "source": "JMA",
            "max_temp": None,  # 数値データは別APIで取得可能
            "min_temp": None,  # 数値データは別APIで取得可能
            "pop": None,      # 数値データは別APIで取得可能
            "description": data.get("text", "（取得できませんでした）")
        }

    except Exception as e:
        logger.error(f"[JMA データ取得エラー] {e}")
        return {
            "source": "JMA",
            "max_temp": None,
            "min_temp": None,
            "pop": None,
            "description": None
        }

def get_area_code(pref_name: str) -> str:
    """都道府県名から気象庁コードを返す"""
    area_codes = {
        "千葉県": "120000",  # 千葉県
        "東京都": "130000",  # 東京都
        "神奈川県": "140000",  # 神奈川県
        # 必要に応じて他の都道府県を追加
    }
    return area_codes.get(pref_name, "120000")  # デフォルトは千葉県