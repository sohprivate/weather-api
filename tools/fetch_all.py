from agents.tsukumi_agent import TsukumiAgent
from agents.weatherapi_agent import WeatherAPIAgent
from agents.openweather_agent import OpenWeatherAgent
from agents.openmeteo_agent import OpenMeteoAgent
from agents.jma_agent import JMAAgent
import csv

# 地点の読み込み
def load_locations(filepath="data/locations.csv"):
    locations = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append({
                "prefecture": row["prefecture"],
                "city": row["city"],
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"]),
            })
    return locations

# エージェントの初期化
agents = [
    TsukumiAgent(),
    WeatherAPIAgent(),
    OpenWeatherAgent(),
    OpenMeteoAgent(),
    JMAAgent(),
]

def fetch_all():
    all_results = {}

    for loc in load_locations():
        key = f"{loc['prefecture']}_{loc['city']}"
        all_results[key] = []
        for agent in agents:
            try:
                result = agent.fetch(loc)

                # 🔽 ここで位置情報を付加！
                result["latitude"] = loc["lat"]
                result["longitude"] = loc["lon"]

                all_results[key].append(result)
            except Exception as e:
                print(f"[ERROR] {agent.__class__.__name__} @ {key}: {e}")
    return all_results

