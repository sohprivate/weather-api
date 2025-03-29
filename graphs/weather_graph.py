from langgraph.graph import StateGraph, END
from langgraph.pregel import Pregel
from typing import TypedDict, List, Optional, Dict, Any
import logging
from datetime import datetime
from tools.normalizer import normalize_forecast
from tools.comparator import compare_forecasts

# エージェント関数のインポート
from agents.tsukumi_agent import get_tsukumi_forecast
from agents.openweather_agent import get_openweather_forecast
from agents.weatherapi_agent import get_weatherapi_forecast
from agents.openmeteo_agent import get_openmeteo_forecast
from agents.jma_agent import get_jma_forecast

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- 状態の定義 ---
class WeatherState(TypedDict):
    raw_forecasts: Optional[List[Dict[str, Any]]]
    normalized: Optional[List[Dict[str, Any]]]
    comparison: Optional[Dict[str, Any]]
    final_decision: Optional[Dict[str, Any]]
    error: Optional[str]
    timestamp: Optional[str]


# --- 各ステップの関数定義 ---

def fetch_forecasts(state: WeatherState) -> WeatherState:
    logger.info("各エージェントの予報を取得中...")
    try:
        forecasts = [
            get_tsukumi_forecast(),
            get_openweather_forecast(),
            get_weatherapi_forecast(),
            get_openmeteo_forecast(),
            get_jma_forecast()
        ]
        return {
            **state,
            "raw_forecasts": forecasts,
            "timestamp": datetime.now().isoformat(),
            "error": None
        }
    except Exception as e:
        logger.error(f"予報の取得中にエラーが発生: {str(e)}")
        return {**state, "error": str(e)}

def normalize(state: WeatherState) -> WeatherState:
    if state.get("error"):
        return state
        
    logger.info("データを整形中...")
    try:
        normalized = [normalize_forecast(f) for f in state["raw_forecasts"]]
        return {**state, "normalized": normalized, "error": None}
    except Exception as e:
        logger.error(f"データの整形中にエラーが発生: {str(e)}")
        return {**state, "error": str(e)}

def compare(state: WeatherState) -> WeatherState:
    if state.get("error"):
        return state
        
    logger.info("ばらつきを評価中...")
    try:
        result = compare_forecasts(state["normalized"])
        return {**state, "comparison": result, "error": None}
    except Exception as e:
        logger.error(f"比較中にエラーが発生: {str(e)}")
        return {**state, "error": str(e)}

def decide(state: WeatherState) -> WeatherState:
    if state.get("error"):
        return state
        
    logger.info("最終決定を実行中...")
    try:
        valid = [f for f in state["normalized"] if f["max_temp"] is not None]
        if not valid:
            logger.warning("有効な予報データが見つかりません")
            return {**state, "final_decision": None, "error": "有効な予報データが見つかりません"}

        median = sorted([f["max_temp"] for f in valid])[len(valid) // 2]
        chosen = min(valid, key=lambda x: abs(x["max_temp"] - median))
        logger.info(f"最終決定: {chosen}")
        return {**state, "final_decision": chosen, "error": None}
    except Exception as e:
        logger.error(f"決定中にエラーが発生: {str(e)}")
        return {**state, "error": str(e)}


# --- LangGraphの定義 ---
def build_weather_graph() -> StateGraph:
    graph = StateGraph(WeatherState)

    graph.add_node("fetch", fetch_forecasts)
    graph.add_node("normalize", normalize)
    graph.add_node("compare", compare)
    graph.add_node("decide", decide)

    # 遷移を定義
    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "normalize")
    graph.add_edge("normalize", "compare")
    graph.add_edge("compare", "decide")
    graph.add_edge("decide", END)

    return graph.compile()