import math

def normalize(raw: dict) -> dict:
    """
    各天気APIの出力を統一フォーマットに変換する。

    Input:
    {
        "source": "WeatherAPI",
        "max_temp": 13.3,
        "min_temp": 7.7,
        "pop": 88,
        "description": "雨が降るでしょう"
    }

    Output:
    {
        "source": "WeatherAPI",
        "max_temp": float or None,
        "min_temp": float or None,
        "pop": int or None,
        "description": str or None
    }
    """
    def to_float(value):
        try:
            val = float(value)
            return None if math.isnan(val) else val
        except (TypeError, ValueError):
            return None

    def to_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    return {
        "source": raw.get("source"),
        "max_temp": to_float(raw.get("max_temp")),
        "min_temp": to_float(raw.get("min_temp")),
        "pop": to_int(raw.get("pop")),
        "description": raw.get("description") if isinstance(raw.get("description"), str) else None,
    }
