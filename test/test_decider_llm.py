import sys
import os
from dotenv import load_dotenv

# LangChainなどのパスを認識させる
sys.path.append(os.path.abspath("."))

from tools.decider_llm import decide_by_llm

load_dotenv()  # .env から APIキーを読み込み

sample_input = [
    {
        "source": "OpenWeatherMap",
        "max_temp": 12.5,
        "min_temp": 7.2,
        "pop": 70,
        "description": "晴れ時々曇りです。夜に雨の可能性があります。"
    },
    {
        "source": "WeatherAPI",
        "max_temp": 13.1,
        "min_temp": 8.0,
        "pop": 65,
        "description": "午前中は晴れ、午後は曇りのち一時雨となるでしょう。"
    },
    {
        "source": "Tsukumijima",
        "max_temp": 10.0,
        "min_temp": 6.0,
        "pop": 80,
        "description": "一日を通して曇り、夕方から弱い雨。"
    },
    {
        "source": "JMA",
        "max_temp": None,
        "min_temp": None,
        "pop": None,
        "description": "高気圧に覆われ、概ね晴れるでしょう。"
    }
]

if __name__ == "__main__":
    print("🧪 Running LLM-based Decider Test...\n")

    result = decide_by_llm(sample_input)
    print("✅ LLM Decision Result:")
    print(result)
