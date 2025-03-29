from typing import Dict, Union, Optional

def normalize_forecast(forecast: Dict[str, Union[str, float, int, None]]) -> Dict[str, Optional[Union[str, float, int]]]:
    """
    各エージェントの天気予報データを共通形式に整える。

    Args:
        forecast (dict): エージェントからの生データ
            {
                "source": str,
                "max_temp": float|None,
                "min_temp": float|None,
                "pop": int|None,
                "description": str|None
            }

    Returns:
        dict: 正規化されたデータ（全ソース共通構造）
            {
                "source": str,
                "max_temp": float|None,  # 小数点1位まで
                "min_temp": float|None,  # 小数点1位まで
                "pop": int|None,         # 0-100の整数値
                "description": str|None  # 概況文
            }
    """
    def round_or_none(val: Union[float, int, str, None]) -> Optional[float]:
        """数値を小数点1位まで丸める。非数値やNoneの場合はNoneを返す"""
        if val is None:
            return None
        try:
            return round(float(val), 1)
        except (ValueError, TypeError):
            return None

    def normalize_pop(val: Union[float, int, str, None]) -> Optional[int]:
        """降水確率を0-100の整数値に正規化。変換できない場合はNone"""
        if val is None:
            return None
        try:
            pop = float(val)
            # 0-1の確率を%に変換
            if 0 <= pop <= 1:
                pop *= 100
            return int(round(pop))
        except (ValueError, TypeError):
            return None

    return {
        "source": str(forecast.get("source", "Unknown")),
        "max_temp": round_or_none(forecast.get("max_temp")),
        "min_temp": round_or_none(forecast.get("min_temp")),
        "pop": normalize_pop(forecast.get("pop")),
        "description": forecast.get("description")
    }