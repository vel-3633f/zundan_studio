"""タイトル生成モジュール"""

import json
import re
from pathlib import Path
from typing import Any, Optional, Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

from app.models.script_models import (
    ScriptMode,
    ComedyTitle,
    ComedyTitleBatch,
    ThemeBatch,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ComedyTitleGenerator:
    """タイトル生成クラス"""

    def __init__(self):
        self.title_batch_prompt_file = Path(
            "app/prompts/comedy/long/title_batch_generation.md"
        )
        self.theme_prompt_file = Path("app/prompts/comedy/long/theme_generation.md")

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

    def fix_json_quotes(self, text: str) -> str:
        """JSON文字列内の未エスケープされた二重引用符を修正する"""
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)
        text = text.strip()

        result = []
        i = 0
        in_string = False
        escaped = False

        while i < len(text):
            char = text[i]

            if escaped:
                result.append(char)
                escaped = False
            elif char == "\\":
                result.append(char)
                escaped = True
            elif char == '"':
                if not in_string:
                    in_string = True
                    result.append(char)
                else:
                    if i + 1 < len(text):
                        next_char = text[i + 1]
                        if next_char in [",", "}", "]", ":", " ", "\t", "\n", "\r"]:
                            in_string = False
                            result.append(char)
                        else:
                            result.append('\\"')
                    else:
                        in_string = False
                        result.append(char)
            else:
                result.append(char)

            i += 1

        return "".join(result)

    def parse_with_retry(
        self, parser: PydanticOutputParser, llm_response: Any, max_retries: int = 2
    ) -> Any:
        """パースをリトライ付きで実行する（汎用版）"""
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                if attempt == 0:
                    return parser.invoke(llm_response)
                else:
                    if hasattr(llm_response, "content"):
                        content = llm_response.content
                    else:
                        content = str(llm_response)

                    logger.warning(
                        f"JSONパースエラー、修正を試みます (試行 {attempt + 1}/{max_retries + 1})"
                    )
                    fixed_content = self.fix_json_quotes(content)

                    from langchain_core.messages import AIMessage

                    fixed_response = AIMessage(content=fixed_content)
                    return parser.invoke(fixed_response)

            except (OutputParserException, json.JSONDecodeError, ValueError) as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(f"パースエラー (試行 {attempt + 1}): {str(e)}")
                    continue
                else:
                    logger.error(f"パースエラー: 最大試行回数に達しました")
                    raise

        if last_error:
            raise last_error
        raise ValueError("パースに失敗しました")

    def generate_title_batch(
        self,
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ComedyTitleBatch:
        """ランダムにタイトルを20-30個量産する"""
        logger.info("お笑いモード タイトル量産開始")

        try:
            if progress_callback:
                progress_callback("🎲 ランダムタイトルを量産中...")

            prompt_template = self.load_prompt(self.title_batch_prompt_file)

            parser = PydanticOutputParser(pydantic_object=ComedyTitleBatch)
            format_instructions = parser.get_format_instructions()
            prompt_text = prompt_template.replace(
                "{format_instructions}", format_instructions
            )

            system_message = (
                "あなたは、ずんだもん・めたん・つむぎの3名によるYouTube漫談の企画・タイトルを無限に生み出すプロの放送作家です。"
                "ユーザーからのテーマ入力なしに、お笑いの構造に基づいた斬新なタイトルを大量に生成します。"
                "重要: タイトルは必ず30文字以内で生成してください。"
                '重要: JSON出力時、文字列値内で二重引用符（"）を使用する場合は必ずバックスラッシュでエスケープしてください（\\"）。'
            )

            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text),
            ]

            logger.info("タイトル量産をLLMで生成中...")
            llm_response = llm.invoke(messages)

            title_batch = self.parse_with_retry(parser, llm_response)

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
        """テーマからバカバカしいタイトルを生成する（バッチ生成から1つ選択）"""
        logger.info(f"お笑いモード タイトル生成開始（バッチ生成から1つ選択）")

        try:
            if progress_callback:
                progress_callback("📝 バカバカしいタイトルを生成中...")

            title_batch = self.generate_title_batch(llm, progress_callback)

            if not title_batch.titles:
                raise ValueError("タイトル候補が生成されませんでした")

            candidate = title_batch.titles[0]

            title = ComedyTitle(
                title=candidate.title,
                theme=theme,
                clickbait_elements=[],
                mode=ScriptMode.COMEDY,
            )

            logger.info(f"タイトル生成成功: {title.title}")
            logger.info(f"フックパターン: {candidate.hook_pattern}")

            return title

        except Exception as e:
            error_msg = f"タイトル生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def generate_theme_batch(
        self,
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ThemeBatch:
        """テーマ候補を15-20個生成する"""
        logger.info("テーマ候補生成開始")

        try:
            if progress_callback:
                progress_callback("🎯 テーマ候補を生成中...")

            prompt_template = self.load_prompt(self.theme_prompt_file)

            parser = PydanticOutputParser(pydantic_object=ThemeBatch)
            format_instructions = parser.get_format_instructions()
            prompt_text = prompt_template.replace(
                "{format_instructions}", format_instructions
            )

            system_message = (
                "あなたは、テーマを単語で考える人です。"
                '重要: JSON出力時、文字列値内で二重引用符（"）を使用する場合は必ずバックスラッシュでエスケープしてください（\\"）。'
            )

            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text),
            ]

            logger.info("テーマ候補をLLMで生成中...")
            llm_response = llm.invoke(messages)

            theme_batch = self.parse_with_retry(parser, llm_response)

            logger.info(f"テーマ候補生成成功: {len(theme_batch.themes)}個生成")
            for i, theme in enumerate(theme_batch.themes, 1):
                logger.info(f"  {i}. {theme}")

            return theme_batch

        except Exception as e:
            error_msg = f"テーマ候補生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def generate_title_from_theme(
        self,
        theme: str,
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ComedyTitleBatch:
        """テーマからタイトルを20個生成する"""
        logger.info(f"テーマベース タイトル生成開始: {theme}")

        try:
            if progress_callback:
                progress_callback(f"📝 「{theme}」のタイトルを生成中...")

            prompt_template = self.load_prompt(self.title_batch_prompt_file)

            parser = PydanticOutputParser(pydantic_object=ComedyTitleBatch)
            format_instructions = parser.get_format_instructions()
            prompt_text = prompt_template.replace(
                "{format_instructions}", format_instructions
            )

            # テーマをプロンプトに追加
            theme_instruction = f"\n\n## 重要: 生成するタイトルは必ず「{theme}」をテーマとして含めてください。"
            prompt_text = prompt_text + theme_instruction

            system_message = (
                "あなたは、ずんだもん・めたん・つむぎの3名によるYouTube漫談の企画・タイトルを無限に生み出すプロの放送作家です。"
                f"ユーザーが指定したテーマ「{theme}」を基に、お笑いの構造に基づいた斬新なタイトルを大量に生成します。"
                "重要: タイトルは必ず30文字以内で生成してください。"
                '重要: JSON出力時、文字列値内で二重引用符（"）を使用する場合は必ずバックスラッシュでエスケープしてください（\\"）。'
            )

            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text),
            ]

            logger.info(f"テーマ「{theme}」でタイトル量産をLLMで生成中...")
            llm_response = llm.invoke(messages)

            title_batch = self.parse_with_retry(parser, llm_response)

            logger.info(
                f"テーマベース タイトル生成成功: {len(title_batch.titles)}個生成"
            )
            for i, candidate in enumerate(title_batch.titles, 1):
                logger.info(f"  {i}. [{candidate.hook_pattern}] {candidate.title}")

            return title_batch

        except Exception as e:
            error_msg = f"テーマベース タイトル生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
