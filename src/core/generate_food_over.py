import streamlit as st
import os
from pathlib import Path
from typing import Dict, List, Any, Union
from src.models.food_over import FoodOverconsumptionScript
from src.utils.utils import process_conversation_segments
from config.app import SYSTEM_PROMPT_FILE, USER_PROMPT_FILE, TAVILY_SEARCH_RESULTS_COUNT

from dotenv import load_dotenv

load_dotenv()
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_community.retrievers import TavilySearchAPIRetriever
from src.models.food_over import FoodOverconsumptionScript

_prompt_cache = {}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# モジュール専用ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# ハンドラーが既に追加されていない場合のみ追加
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)


def load_prompt_from_file(file_path: Path, cache_key: str = None) -> str:
    """プロンプトファイルを読み込む（キャッシュ機能付き）"""
    if cache_key and cache_key in _prompt_cache:
        logger.debug(f"プロンプトキャッシュからロード: {cache_key}")
        return _prompt_cache[cache_key]

    try:
        if not file_path.exists():
            raise FileNotFoundError(f"プロンプトファイルが見つかりません: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if cache_key:
            _prompt_cache[cache_key] = content
            logger.debug(f"プロンプトファイルをキャッシュに保存: {cache_key}")

        logger.info(f"プロンプトファイル読み込み成功: {file_path}")
        return content

    except Exception as e:
        error_msg = f"プロンプトファイル読み込みエラー ({file_path}): {str(e)}"
        logger.error(error_msg)


def search_food_information(food_name: str) -> Dict[str, List[str]]:
    """TavilyAPIを使用して食べ物の情報を検索する"""
    logger.info(f"食べ物情報検索開始: {food_name}")

    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            error_msg = "TAVILY_API_KEY が設定されていません"
            logger.error(error_msg)
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
            logger.info(f"検索実行: {query}")
            try:
                docs = retriever.invoke(query)
                content_list = []
                for doc in docs:
                    if hasattr(doc, "page_content") and doc.page_content:
                        content_list.append(doc.page_content.strip())

                search_results[result_keys[i]] = content_list
                logger.info(f"検索結果取得: {query} - {len(content_list)}件")

            except Exception as e:
                logger.error(f"検索エラー: {query} - {str(e)}")
                search_results[result_keys[i]] = []

        return search_results

    except Exception as e:
        error_msg = f"Tavily検索で予期せぬエラー: {str(e)}"
        logger.error(error_msg)
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


def generate_food_overconsumption_script(
    food_name: str, model: str = "gpt-4.1", temperature: float = 0.8
) -> Union[FoodOverconsumptionScript, Dict[str, Any]]:
    """食べ物摂取過多動画脚本を生成する"""
    logger.info(
        f"脚本生成開始: 食べ物={food_name}, モデル={model}, temperature={temperature}"
    )

    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            error_msg = "OPENAI_API_KEY が設定されていません"
            logger.error(error_msg)
            return {
                "error": "API Key Error",
                "details": error_msg,
            }

        # Tavily検索を実行
        search_results = search_food_information(food_name)
        reference_information = format_search_results_for_prompt(search_results)

        # 検索結果をセッション状態に保存（デバッグ用）
        st.session_state.last_search_results = search_results

        # プロンプトファイルから読み込み
        system_template = load_prompt_from_file(SYSTEM_PROMPT_FILE, "system")
        user_template = load_prompt_from_file(USER_PROMPT_FILE, "user")

        llm = ChatOpenAI(model=model, temperature=temperature, api_key=openai_api_key)
        parser = PydanticOutputParser(pydantic_object=FoodOverconsumptionScript)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("user", user_template),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        chain = prompt | llm | parser

        logger.info(f"{food_name}の摂取過多動画脚本をLLMで生成中...")
        response_object = chain.invoke(
            {"food_name": food_name, "reference_information": reference_information}
        )

        # all_segmentsを作成
        all_segments = []
        for section in response_object.sections:
            all_segments.extend(section.segments)

        logger.info(f"LLMから受信したセグメント数: {len(all_segments)}")

        # 文字数チェックと分割処理
        processed_segments = process_conversation_segments(all_segments)
        response_object.all_segments = processed_segments

        # セクション内のセグメントも更新
        segment_index = 0
        for section in response_object.sections:
            section_segments = []
            for _ in section.segments:
                if segment_index < len(processed_segments):
                    section_segments.append(processed_segments[segment_index])
                    segment_index += 1
            section.segments = section_segments

        logger.info("食べ物摂取過多動画脚本の生成に成功")

        st.session_state.last_generated_json = response_object
        st.session_state.last_llm_output = "パース成功: 構造化データに変換済み"

        return response_object

    except OutputParserException as e:
        error_msg = "パースエラー: LLMの出力形式が不正です"
        logger.error(f"{error_msg}. LLM出力: {e.llm_output}")

        st.session_state.last_llm_output = e.llm_output
        st.session_state.last_generated_json = None

        return {
            "error": "Pydantic Parse Error",
            "details": str(e),
            "raw_output": e.llm_output,
        }
    except Exception as e:
        error_msg = f"予期せぬエラーが発生しました: {e}"
        logger.error(error_msg, exc_info=True)

        st.session_state.last_llm_output = f"予期せぬエラー: {str(e)}"
        st.session_state.last_generated_json = None

        return {"error": "Unexpected Error", "details": str(e)}
