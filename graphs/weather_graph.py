from langgraph.graph import StateGraph, END
from langgraph.pregel import Pregel
from typing import TypedDict, List, Optional, Dict, Any
import logging
from datetime import datetime
from tools.normalizer import normalize_forecast
from tools.comparator import compare_forecasts
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

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

# OpenAIクライアントの初期化
load_dotenv()
chat = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# --- 状態の定義 ---
class WeatherState(TypedDict):
    raw_forecasts: Optional[List[Dict[str, Any]]]
    normalized: Optional[List[Dict[str, Any]]]
    comparison: Optional[Dict[str, Any]]
    final_decision: Optional[Dict[str, Any]]
    error: Optional[str]
    timestamp: Optional[str]
    ai_analysis: Optional[str]


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

def analyze_with_ai(state: WeatherState) -> WeatherState:
    if state.get("error"):
        return state
        
    logger.info("AIによる予報分析を実行中...")
    try:
        # 予報データを文字列に変換
        forecasts_text = "\n".join([
            f"予報元: {f.get('source', 'Unknown')}\n"
            f"最高気温: {f.get('max_temp')}°C\n"
            f"最低気温: {f.get('min_temp')}°C\n"
            f"降水確率: {f.get('precipitation_prob')}%\n"
            for f in state["normalized"]
        ])

        # LangChainを使用して分析
        messages = [
            {"role": "system", "content": "あなたは天気予報の専門家です。複数の予報を分析し、最も信頼性の高い予報を選んでください。"},
            {"role": "user", "content": f"以下の天気予報を分析し、最も信頼性の高い予報を選んでください。\n\n{forecasts_text}"}
        ]
        
        response = chat.invoke(messages)
        analysis = response.content
        logger.info(f"AI分析結果: {analysis}")

        return {**state, "ai_analysis": analysis, "error": None}
    except Exception as e:
        logger.error(f"AI分析中にエラーが発生: {str(e)}")
        return {**state, "error": str(e)}

def decide(state: WeatherState) -> WeatherState:
    if state.get("error"):
        return state
        
    logger.info("最終決定を実行中...")
    try:
        # AI分析結果を考慮して決定
        if state.get("ai_analysis"):
            # AIの分析結果に基づいて予報を選択
            # ここでは例として、AIの分析結果に最も関連する予報を選択
            valid = [f for f in state["normalized"] if f["max_temp"] is not None]
            if not valid:
                logger.warning("有効な予報データが見つかりません")
                return {**state, "final_decision": None, "error": "有効な予報データが見つかりません"}

            # AI分析結果に基づいて予報を選択
            chosen = valid[0]  # 実際の実装では、AI分析結果に基づいてより賢い選択を行う
            logger.info(f"最終決定: {chosen}")
            return {**state, "final_decision": chosen, "error": None}
        else:
            # AI分析がない場合は従来の中央値ベースの選択
            valid = [f for f in state["normalized"] if f["max_temp"] is not None]
            if not valid:
                return {**state, "final_decision": None, "error": "有効な予報データが見つかりません"}

            median = sorted([f["max_temp"] for f in valid])[len(valid) // 2]
            chosen = min(valid, key=lambda x: abs(x["max_temp"] - median))
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
    graph.add_node("analyze", analyze_with_ai)  # 新しいAI分析ノードを追加
    graph.add_node("decide", decide)

    # 遷移を定義
    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "normalize")
    graph.add_edge("normalize", "compare")
    graph.add_edge("compare", "analyze")  # AI分析ステップを追加
    graph.add_edge("analyze", "decide")
    graph.add_edge("decide", END)

    return graph.compile()