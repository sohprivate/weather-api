import csv
from agents.jma_agent import JMAAgent
from agents.openmeteo_agent import OpenMeteoAgent
from agents.openweather_agent import OpenWeatherAgent
from agents.tsukumi_agent import TsukumiAgent
from agents.weatherapi_agent import WeatherAPIAgent

# CSVを読み込んで、location辞書のリストを作成
def load_locations(csv_path="data/locations.csv"):
    locations = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append({
                "city": row["city"],
                "prefecture": row["prefecture"],
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"]),
            })
    return locations

def main():
    locations = load_locations()
    
    agents = [
        JMAAgent(),
        OpenMeteoAgent(),
        OpenWeatherAgent(),
        TsukumiAgent(),
        WeatherAPIAgent(),
    ]

    for loc in locations:
        print(f"\n📍 {loc['prefecture']} {loc['city']} の予報:")
        for agent in agents:
            result = agent.fetch(loc)
            print(f" - {result['source']}: {result}")

if __name__ == "__main__":
    main()
