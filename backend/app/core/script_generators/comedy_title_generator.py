"""タイトル生成モジュール"""

from pathlib import Path
from typing import Any, Optional, Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from app.models.script_models import (
    ScriptMode,
    ComedyTitle,
    ComedyTitleBatch,
)
from app.utils_legacy.logger import get_logger

logger = get_logger(__name__)


class ComedyTitleGenerator:
    """タイトル生成クラス"""

    def __init__(self):
        self.title_batch_prompt_file = Path(
            "app/prompts/comedy/title_batch_generation.md"
        )

    def load_prompt(self, file_path: Path) -> str:
        """プロンプトファイルを読み込む"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(
                    f"プロンプトファイルが見つかりません: {file_path}"
                )

            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()

        except Exception as e:
            logger.error(f"プロンプト読み込みエラー: {str(e)}")
            raise

    def generate_title_batch(
        self,
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ComedyTitleBatch:
        """ランダムにタイトルを20-30個量産

        Args:
            llm: LLMインスタンス
            progress_callback: 進捗通知用コールバック関数

        Returns:
            ComedyTitleBatch: 生成されたタイトル候補リスト（20-30個）
        """
        logger.info("お笑いモード タイトル量産開始")

        try:
            if progress_callback:
                progress_callback("🎲 ランダムタイトルを量産中...")

            # プロンプト読み込み
            prompt_template = self.load_prompt(self.title_batch_prompt_file)

            # パーサー設定
            parser = PydanticOutputParser(pydantic_object=ComedyTitleBatch)
            format_instructions = parser.get_format_instructions()
            prompt_text = prompt_template.replace(
                "{format_instructions}", format_instructions
            )

            # システムメッセージ
            system_message = "あなたは、ずんだもん・めたん・つむぎの3名によるYouTube漫談の企画・タイトルを無限に生み出すプロの放送作家です。ユーザーからのテーマ入力なしに、お笑いの構造に基づいた斬新なタイトルを大量に生成します。"

            # LLM呼び出し
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text),
            ]

            logger.info("タイトル量産をLLMで生成中...")
            llm_response = llm.invoke(messages)

            # パース
            title_batch = parser.invoke(llm_response)

            logger.info(f"タイトル量産成功: {len(title_batch.titles)}個生成")
            for i, candidate in enumerate(title_batch.titles, 1):
                logger.info(f"  {i}. [{candidate.hook_pattern}] {candidate.title}")

            return title_batch

        except Exception as e:
            error_msg = f"タイトル量産エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def generate_title(
        self,
        theme: str,
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ComedyTitle:
        """テーマからバカバカしいタイトルを生成

        注意: themeパラメータは互換性のために残していますが、
        実際にはtitle_batch_generationを使ってランダム生成し、
        最初の候補を返します。

        Args:
            theme: 漫談のテーマ（使用されません）
            llm: LLMインスタンス
            progress_callback: 進捗通知用コールバック関数

        Returns:
            ComedyTitle: 生成されたタイトル
        """
        logger.info(f"お笑いモード タイトル生成開始（バッチ生成から1つ選択）")

        try:
            if progress_callback:
                progress_callback("📝 バカバカしいタイトルを生成中...")

            # バッチ生成を使用
            title_batch = self.generate_title_batch(llm, progress_callback)

            if not title_batch.titles:
                raise ValueError("タイトル候補が生成されませんでした")

            # 最初の候補を使用
            candidate = title_batch.titles[0]

            # ComedyTitleに変換
            title = ComedyTitle(
                title=candidate.title,
                theme=theme,  # 互換性のためthemeを保持
                clickbait_elements=[],  # バッチ生成にはclickbait_elementsがない
                mode=ScriptMode.COMEDY,
            )

            logger.info(f"タイトル生成成功: {title.title}")
            logger.info(f"フックパターン: {candidate.hook_pattern}")

            return title

        except Exception as e:
            error_msg = f"タイトル生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

