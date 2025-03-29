import requests

def get_tsukumi_forecast(location_code: str = "120010") -> dict:
    """
    Tsukumijima APIから指定地域コードの明日の天気予報を取得し、
    'max_temp', 'min_temp', 'pop'（降水確率）を含む辞書を返す。

    Args:
        location_code (str): 地域コード（例: 千葉市=120010）

    Returns:
        dict: {
            "source": "Tsukumijima",
            "max_temp": float,
            "min_temp": float,
            "pop": int（最大値％、0〜100）
        }
    """
    url = f"https://weather.tsukumijima.net/api/forecast/city/{location_code}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 明日の予報（index=1）を取得
        forecast = data["forecasts"][1]

        # 気温（摂氏）を取得（Noneの場合もあるのでチェック）
        max_temp = forecast["temperature"]["max"]["celsius"]
        min_temp = forecast["temperature"]["min"]["celsius"]

        # 降水確率（"06-12"などの時間帯ごとの文字列%をint平均に変換）
        rain_chances = forecast["chanceOfRain"]
        pop_values = [
            int(v.replace("%", "")) for v in rain_chances.values() if v != "--"
        ]
        avg_pop = int(sum(pop_values) / len(pop_values)) if pop_values else 0

        return {
            "source": "Tsukumijima",
            "max_temp": float(max_temp) if max_temp else None,
            "min_temp": float(min_temp) if min_temp else None,
            "pop": avg_pop
        }

    except Exception as e:
        print(f"[Tsukumijima Error] {e}")
        return {
            "source": "Tsukumijima",
            "max_temp": None,
            "min_temp": None,
            "pop": None
        }