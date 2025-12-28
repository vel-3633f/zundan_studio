import os
from pathlib import Path
from typing import Dict, List, Any, Union
from app.config.app import TAVILY_SEARCH_RESULTS_COUNT
from app.utils.logger import get_logger

from dotenv import load_dotenv

load_dotenv()

from langchain_community.retrievers import TavilySearchAPIRetriever
from app.utils.llm_factory import create_llm_from_model_config

_prompt_cache = {}

logger = get_logger(__name__)


def load_prompt_from_file(file_path: Path, cache_key: str = None) -> str:
    """プロンプトファイルを読み込む（キャッシュ機能付き）"""
    if cache_key and cache_key in _prompt_cache:
        return _prompt_cache[cache_key]

    try:
        if not file_path.exists():
            raise FileNotFoundError(f"プロンプトファイルが見つかりません: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if cache_key:
            _prompt_cache[cache_key] = content

        return content

    except Exception as e:
        error_msg = f"プロンプトファイル読み込みエラー ({file_path}): {str(e)}"
        logger.error(error_msg)


def search_food_information(food_name: str) -> Dict[str, List[str]]:
    """TavilyAPIを使用して食べ物の情報を検索する"""
    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            logger.error("TAVILY_API_KEY が設定されていません")
            return {"overeating": [], "benefits": [], "disadvantages": []}

        retriever = TavilySearchAPIRetriever(k=TAVILY_SEARCH_RESULTS_COUNT)

        search_queries = [
            f"{food_name} 食べ過ぎ",
            f"{food_name} メリット",
            f"{food_name} デメリット",
        ]

        search_results = {"overeating": [], "benefits": [], "disadvantages": []}
        result_keys = ["overeating", "benefits", "disadvantages"]

        for i, query in enumerate(search_queries):
            try:
                docs = retriever.invoke(query)
                content_list = []
                for doc in docs:
                    if hasattr(doc, "page_content") and doc.page_content:
                        content_list.append(doc.page_content.strip())

                search_results[result_keys[i]] = content_list

            except Exception as e:
                logger.error(f"検索エラー: {query} - {str(e)}")
                search_results[result_keys[i]] = []

        return search_results

    except Exception as e:
        logger.error(f"Tavily検索で予期せぬエラー: {str(e)}")
        return {"overeating": [], "benefits": [], "disadvantages": []}


def format_search_results_for_prompt(search_results: Dict[str, List[str]]) -> str:
    """検索結果をプロンプト用にフォーマットする"""
    formatted_text = "## 参考情報\n\n"

    sections = [
        ("overeating", "食べ過ぎに関する情報"),
        ("benefits", "メリットに関する情報"),
        ("disadvantages", "デメリットに関する情報"),
    ]

    for key, title in sections:
        formatted_text += f"### {title}\n"
        if search_results[key]:
            for i, content in enumerate(search_results[key], 1):
                formatted_text += f"{i}. {content}\n\n"
        else:
            formatted_text += "情報が見つかりませんでした。\n\n"

    return formatted_text


def create_llm_instance(model: str, temperature: float, model_config: Dict[str, Any]):
    """モデル設定に基づいてLLMインスタンスを生成する（AWS Bedrock専用）

    注: この関数は後方互換性のために残されています。
    新しいコードでは src.utils.llm_factory.create_llm_from_model_config を使用してください。
    """
    return create_llm_from_model_config(model_config, temperature)


def generate_food_overconsumption_script(
    food_name: str, model: str = None, temperature: float = None
) -> Dict[str, Any]:
    """食べ物摂取過多動画脚本を生成する

    注: この関数は後方互換性のために残されています。
    新しいコードでは unified_script_generator を使用してください。
    """
    logger.warning(
        "generate_food_overconsumption_script は非推奨です。"
        "unified_script_generator の使用を推奨します。"
    )

    return {
        "error": "Deprecated Function",
        "details": "この関数は非推奨です。unified_script_generatorを使用してください。",
    }
