from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional, Dict, Any
import logging
from datetime import datetime
from tools.normalizer import normalize
from tools.comparator import compare_forecasts
from langchain_aws import ChatBedrock
import os
import boto3
from dotenv import load_dotenv

# エージェント関数のインポート
from agents.tsukumi_agent import get_tsukumi_forecast
from agents.openweather_agent import get_openweather_forecast
from agents.weatherapi_agent import get_weatherapi_forecast
from agents.openmeteo_agent import get_openmeteo_forecast
from agents.jma_agent import get_jma_forecast

# ▼ 追加でインポートするモジュール
from tools.normalizer import normalize
from tools.comparator import compare_forecasts
from tools.decider_llm import decide_by_llm
from tools.fetch_all import fetch_all
from tools.visualizer import visualizer_agent

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Claude（Bedrock）クライアントの初期化
load_dotenv()
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN")
)

chat = ChatBedrock(
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    client=bedrock,
    temperature=0.7,
    region="us-east-1"
)

# --- 状態の定義 ---
class WeatherState(TypedDict):
    raw_forecasts: Optional[Dict[str, List[Dict[str, Any]]]]
    normalized: Optional[List[Dict[str, Any]]]
    comparison: Optional[Dict[str, Any]]
    final_decision: Optional[Dict[str, Any]]
    error: Optional[str]
    timestamp: Optional[str]
    ai_analysis: Optional[str]
    logs: List[str]
    html_path: Optional[str]
    html_content: Optional[str]

# --- 各ステップの関数定義 ---
def fetch_forecasts(state: WeatherState) -> WeatherState:
    logs = ["[fetch] 全地点の予報をまとめて取得中..."]
    try:
        all_data = fetch_all()
        logs.append(f"[fetch] {len(all_data)} 地点の予報を取得しました")
        return {
            **state,
            "raw_forecasts": all_data,
            "timestamp": datetime.now().isoformat(),
            "error": None,
            "logs": state.get("logs", []) + logs
        }
    except Exception as e:
        logs.append(f"[fetch] エラー: {str(e)}")
        return {**state, "error": str(e), "logs": state.get("logs", []) + logs}

def normalize_node(state: WeatherState):
    logs = state["logs"] + ["Normalize Node: 正規化処理を実行..."]
    all_data = state.get("raw_forecasts", {})
    all_normalized = []
    for forecasts in all_data.values():
        all_normalized.extend([normalize(f) for f in forecasts])
    logs.append(f"Normalize Node: {len(all_normalized)} 件を正規化完了。")
    return {
        **state,
        "logs": logs,
        "normalized": all_normalized
    }

def compare_node(state: WeatherState):
    logs = state["logs"] + ["Compare Node: ばらつきスコアを計算..."]
    all_data = state.get("raw_forecasts", {})
    comparison_result = {}
    for location, forecasts in all_data.items():
        normalized = [normalize(f) for f in forecasts]
        comparison_result[location] = compare_forecasts(normalized)
    logs.append("Compare Node: スコア計算完了。")
    return {
        **state,
        "logs": logs,
        "comparison": comparison_result
    }

def decider_node(state: WeatherState):
    logs = state["logs"] + ["Decider Node: LLMで最終的な予報を合成..."]
    normalized_forecasts = state.get("normalized", [])
    final_decision = decide_by_llm(normalized_forecasts)
    logs.append("Decider Node: LLM合成完了。 → " + str(final_decision))
    return {
        **state,
        "logs": logs,
        "final_decision": final_decision
    }

def analyze_with_ai(state: WeatherState) -> WeatherState:
    logs = ["[analyze] ClaudeでAI分析中..."]
    if state.get("error"):
        return state
    try:
        forecasts_text = "\n".join([
            f"予報元: {f.get('source', 'Unknown')}\n"
            f"最高気温: {f.get('max_temp')}°C\n"
            f"最低気温: {f.get('min_temp')}°C\n"
            f"降水確率: {f.get('pop')}%\n"
            for f in state["normalized"]
        ])
        messages = [
            {"role": "system", "content": "あなたは天気予報の専門家です。複数の予報を分析し、最も信頼性の高い予報を選んでください。"},
            {"role": "user", "content": forecasts_text}
        ]
        response = chat.invoke(messages)
        logs.append("[analyze] 分析完了")
        return {**state, "ai_analysis": response.content, "error": None, "logs": state.get("logs", []) + logs}
    except Exception as e:
        logs.append(f"[analyze] エラー: {str(e)}")
        return {**state, "error": str(e), "logs": state.get("logs", []) + logs}

def decide(state: WeatherState) -> WeatherState:
    logs = ["[decide] 最終予報を決定中..."]
    if state.get("error"):
        return state
    try:
        valid = [f for f in state["normalized"] if f["max_temp"] is not None]
        if not valid:
            logs.append("[decide] 有効なデータがありません")
            return {**state, "final_decision": None, "error": "有効なデータなし", "logs": state.get("logs", []) + logs}

        chosen = valid[0]
        logs.append(f"[decide] 最終予報: {chosen}")
        return {**state, "final_decision": chosen, "error": None, "logs": state.get("logs", []) + logs}
    except Exception as e:
        logs.append(f"[decide] エラー: {str(e)}")
        return {**state, "error": str(e), "logs": state.get("logs", []) + logs}

# --- LangGraphの定義 ---
def build_weather_graph() -> StateGraph:
    graph = StateGraph(WeatherState)
    graph.add_node("fetch", fetch_forecasts)
    graph.add_node("normalizer", normalize_node)
    graph.add_node("comparator", compare_node)
    graph.add_node("decider_llm", decider_node)
    graph.add_node("analyze", analyze_with_ai)
    graph.add_node("decide", decide)
    graph.add_node("visualizer", visualizer_agent)

    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "normalizer")
    graph.add_edge("normalizer", "comparator")
    graph.add_edge("comparator", "decider_llm")
    graph.add_edge("decider_llm", "analyze")
    graph.add_edge("analyze", "decide")
    graph.add_edge("decide", "visualizer")
    graph.add_edge("visualizer", END)

    return graph.compile()
