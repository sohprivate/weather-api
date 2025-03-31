from tools.fetch_all import fetch_all  # 全地点のデータ取得
from tools.normalizer import normalize
from collections import defaultdict

def check_forecast_distribution(all_data):
    summary = defaultdict(int)

    for pref_city, forecasts in all_data.items():
        summary[len(forecasts)] += 1
        if len(forecasts) < 5:
            print(f"[WARN] {pref_city} has only {len(forecasts)} forecasts: {forecasts}")

    print("\n=== Summary ===")
    for count, num_locations in sorted(summary.items()):
        print(f"{num_locations} location(s) had {count} forecast(s)")

if __name__ == "__main__":
    raw_all = fetch_all()  # 全部のAPIから取得
    check_forecast_distribution(raw_all)  # ←ここで確認！
