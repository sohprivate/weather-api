from typing import List, Dict
import statistics

def calculate_deviation(value, reference):
    if value is None:
        return None
    return abs(value - reference)

def compare_forecasts(forecasts: List[Dict]) -> Dict[str, Dict]:
    """
    正規化された予報データを比較し、各エージェントのばらつきスコアを算出。

    Args:
        forecasts (List[Dict]): normalize_forecast() 済みのリスト

    Returns:
        Dict[str, Dict]: エージェントごとのスコアと詳細
    """
    # データを抽出（Noneは除外）
    max_temps = [f["max_temp"] for f in forecasts if f["max_temp"] is not None]
    min_temps = [f["min_temp"] for f in forecasts if f["min_temp"] is not None]
    pops = [f["pop"] for f in forecasts if f["pop"] is not None]

    # 中央値を基準に
    ref_max = statistics.median(max_temps)
    ref_min = statistics.median(min_temps)
    ref_pop = statistics.median(pops)

    results = {}
    for f in forecasts:
        source = f["source"]
        dev_max = calculate_deviation(f["max_temp"], ref_max)
        dev_min = calculate_deviation(f["min_temp"], ref_min)
        dev_pop = calculate_deviation(f["pop"], ref_pop)

        # None の場合は0として加算しない
        total_score = sum(d for d in [dev_max, dev_min, dev_pop] if d is not None)

        results[source] = {
            "score": round(total_score, 2),
            "details": {
                "max_temp": round(dev_max, 2) if dev_max is not None else None,
                "min_temp": round(dev_min, 2) if dev_min is not None else None,
                "pop": round(dev_pop, 2) if dev_pop is not None else None
            }
        }

    return results