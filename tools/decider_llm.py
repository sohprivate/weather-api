from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import logging

logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv
import boto3
from langchain_aws import ChatBedrock

load_dotenv()

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
)

llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    client=bedrock,
    region="us-east-1",
    model_kwargs={"temperature": 0.3},
)

prompt = ChatPromptTemplate.from_template("""
以下の天気予報データを参考にして、
"もっとも妥当と思われる"最高気温（max_temp）、最低気温（min_temp）、降水確率（pop）を1つずつ出力してください。

与えられるデータは、複数の天気予報ソースからの情報です。
- 値の中央値を意識しつつ
- 極端に外れた値は無視してもよく
- 信頼できそうな値を総合的に考えてください。

出力形式は以下のJSON形式にしてください：
{{
  "max_temp": float or null,
  "min_temp": float or null,
  "pop": int or null
}}

データ:
{forecasts}
""")

parser = JsonOutputParser()

chain = prompt | llm | parser

def decide_by_llm(forecasts: List[Dict]) -> Dict:
    if not forecasts:
        logger.warning("[LLM Decide] forecasts is empty.")
        return {
            "source": "LLM-Decider",
            "max_temp": None,
            "min_temp": None,
            "pop": None
        }

    try:
        response = chain.invoke({"forecasts": forecasts})
        return {
            "source": "LLM-Decider",
            **response
        }
    except Exception as e:
        logger.error(f"[LLM Decide エラー] {e}")
        return {
            "source": "LLM-Decider",
            "max_temp": None,
            "min_temp": None,
            "pop": None
        }

# テスト用:
if __name__ == "__main__":
    sample = [
        {"source": "A", "max_temp": 13.3, "min_temp": 7.7, "pop": 88},
        {"source": "B", "max_temp": 13.5, "min_temp": 8.0, "pop": 90},
        {"source": "C", "max_temp": 14.6, "min_temp": 5.2, "pop": 10},
        {"source": "D", "max_temp": 100.0, "min_temp": -20.0, "pop": 0},  # 外れ値
    ]
    print(decide_by_llm(sample))