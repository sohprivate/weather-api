from agents.tsukumi_agent import get_tsukumi_forecast
from agents.openweather_agent import get_openweather_forecast
from agents.weatherapi_agent import get_weatherapi_forecast
from agents.openmeteo_agent import get_openmeteo_forecast
from agents.jma_agent import get_jma_forecast
from tools.normalizer import normalize_forecast
from tools.comparator import compare_forecasts
import json

def main():
    print("\n--- Tsukumijima Forecast ---")
    tsukumi = get_tsukumi_forecast()

    print("\n--- OpenWeatherMap Forecast ---")
    openweather = get_openweather_forecast()

    print("\n--- WeatherAPI Forecast ---")
    weatherapi = get_weatherapi_forecast()

    print("\n--- Open-Meteo Forecast ---")
    openmeteo = get_openmeteo_forecast()

    print("\n--- JMA Forecast (概況文のみ) ---")
    jma = get_jma_forecast()

    # すべてを1つのリストにまとめる
    all_results = [tsukumi, openweather, weatherapi, openmeteo, jma]

    print("\n===== 全予報まとめ（生データ）=====")
    print(json.dumps(all_results, indent=2, ensure_ascii=False))

    # 正規化されたデータを表示
    normalized = [normalize_forecast(f) for f in all_results]
    print("\n===== 正規化された予報まとめ =====")
    print(json.dumps(normalized, indent=2, ensure_ascii=False))

    # ばらつきスコアの計算と表示
    deviation_result = compare_forecasts(normalized)
    print("\n===== ばらつきスコア =====")
    print(json.dumps(deviation_result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()