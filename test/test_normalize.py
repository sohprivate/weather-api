import sys
import os
import pprint

# LangGraph上で動作する想定のパス設定
sys.path.append(os.path.abspath("."))

from tools.normalizer import normalize

def test_normalize():
    raw_inputs = [
        {
            "source": "WeatherAPI",
            "max_temp": "13.3",
            "min_temp": "7.7",
            "pop": "88",
            "description": "雨が降るでしょう"
        },
        {
            "source": "OpenWeatherMap",
            "max_temp": 14.6,
            "min_temp": 5.2,
            "pop": None,
            "description": None
        },
        {
            "source": "BrokenAPI",
            "max_temp": "NaN",
            "min_temp": "oops",
            "pop": "xx",
            "description": 9999
        }
    ]

    print("\n🧪 Normalize Function Test Results:")
    for i, raw in enumerate(raw_inputs):
        print(f"\nCase {i+1} - {raw['source']}")
        normalized = normalize(raw)
        pprint.pprint(normalized)

if __name__ == "__main__":
    test_normalize()
