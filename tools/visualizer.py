from typing import List, Dict
import json
from datetime import datetime
import os
import tempfile


def visualizer_agent(state: Dict) -> Dict:
    """
    LangGraph用のvisualizerノード。
    各地点の信頼性スコアに基づいて、日本地図上に色分け表示するHTMLを生成。
    """
    logs = ["Visualizer: Generating HTML map visualization..."]

    # データ準備
    forecast_map = state.get("raw_forecasts", {})  # e.g. {"東京_新宿": [ ... ]}
    compare_results = state.get("comparison", {})  # e.g. {"東京_新宿": {"JMA": {...}, ...}}

    points = []
    for location_key, agents in compare_results.items():
        try:
            prefecture, city = location_key.split("_", 1) 
            forecasts = forecast_map.get(location_key, [])
            lat = forecasts[0].get("latitude") or forecasts[0].get("lat")
            lon = forecasts[0].get("longitude") or forecasts[0].get("lon")


            # 平均スコアを出す（全部足して平均）
            scores = [agent["score"] for agent in agents.values() if agent.get("score") is not None]
            avg_score = sum(scores) / len(scores) if scores else None

            points.append({
                "city": city,
                "prefecture": prefecture,
                "lat": lat,
                "lon": lon,
                "score": avg_score
            })
        except Exception as e:
            logs.append(f"[WARN] Skipped {location_key}: {e}")

    # HTML生成
    html = generate_leaflet_map(points)

    # 一時ファイル保存
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"forecast_map_{ts}.html"
    file_path = os.path.join(tempfile.gettempdir(), filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    logs.append(f"Visualizer: HTML saved to {file_path}")

    return {
        "logs": logs,
        "html_path": file_path,
        "html_content": html,
    }


def generate_leaflet_map(points: List[Dict]) -> str:
    """
    Leafletを使って、日本地図上に色分けした地点をプロットするHTMLを返す。
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Weather Forecast Deviation Map</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>#map {{ height: 100vh; }}</style>
</head>
<body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
    var map = L.map('map').setView([36.2048, 138.2529], 5);
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom: 18 }}).addTo(map);

    var data = {json.dumps(points)};


    function getColor(score) {{
        if (score === null || score === undefined) return 'gray';
        if (score < 5) return 'blue';
        if (score < 10) return 'green';
        if (score < 15) return 'yellow';
        if (score < 20) return 'orange';
        return 'red';
    }}



    data.forEach(function(p) {{
        var circle = L.circleMarker([p.lat, p.lon], {{
            radius: 8,
            fillColor: getColor(p.score),
            color: '#000',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }}).addTo(map);

        circle.bindPopup(`地点: ${{p.prefecture}} ${{p.city}}<br>スコア: ${{p.score ?? 'N/A'}}`);
    }});
</script>
</body>
</html>
    """
