from agents.jma_agent import get_jma_forecast
import json

result = get_jma_forecast()
print(json.dumps(result, indent=2, ensure_ascii=False))