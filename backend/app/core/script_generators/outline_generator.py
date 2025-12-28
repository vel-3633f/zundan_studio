"""アウトライン生成モジュール"""

from pathlib import Path
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.models.food_over import StoryOutline
from app.utils_legacy.logger import get_logger

logger = get_logger(__name__)

OUTLINE_PROMPT_FILE = Path("app/prompts/sections/outline_template.md")


def load_outline_prompt() -> str:
    """アウトライン生成用プロンプトを読み込む"""
    try:
        if not OUTLINE_PROMPT_FILE.exists():
            raise FileNotFoundError(f"プロンプトファイルが見つかりません: {OUTLINE_PROMPT_FILE}")

        with open(OUTLINE_PROMPT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

        logger.info(f"アウトラインプロンプト読み込み成功: {OUTLINE_PROMPT_FILE}")
        return content

    except Exception as e:
        error_msg = f"アウトラインプロンプト読み込みエラー: {str(e)}"
        logger.error(error_msg)
        raise


def generate_outline(
    food_name: str,
    reference_information: str,
    llm: Any
) -> StoryOutline:
    """ストーリー全体のアウトラインを生成する

    Args:
        food_name: 食べ物名
        reference_information: Tavily検索結果のフォーマット済みテキスト
        llm: LLMインスタンス

    Returns:
        StoryOutline: 生成されたアウトライン
    """
    logger.info(f"アウトライン生成開始: {food_name}")

    try:
        # プロンプトテンプレート読み込み
        outline_template = load_outline_prompt()

        # パーサー設定
        parser = PydanticOutputParser(pydantic_object=StoryOutline)

        # プロンプト構築
        prompt = ChatPromptTemplate.from_messages([
            ("system", "あなたは、YouTube動画の脚本家です。視聴者を引きつけ、教育的価値のあるストーリーを設計するプロフェッショナルです。"),
            ("user", outline_template)
        ]).partial(format_instructions=parser.get_format_instructions())

        # LLMチェーン実行
        chain = prompt | llm | parser

        logger.info("アウトラインをLLMで生成中...")
        outline = chain.invoke({
            "food_name": food_name,
            "reference_information": reference_information
        })

        logger.info(f"アウトライン生成成功: タイトル={outline.title}")

        return outline

    except Exception as e:
        error_msg = f"アウトライン生成エラー: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise
