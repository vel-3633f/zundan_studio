"""ショート動画（60秒）専用の台本生成ロジック"""

import json
from pathlib import Path
from typing import Any, Optional, Callable

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

from app.models.script_models import (
    ScriptMode,
    ScriptDuration,
    ComedyTitle,
    ComedyScript,
    ComedyTitleBatch,
)
from .comedy_mood_generator import ComedyMoodGenerator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ComedyShortGenerator:
    """ショート動画（60秒）専用生成ロジック"""

    def __init__(self):
        self.mode = ScriptMode.COMEDY
        self.duration_type = ScriptDuration.SHORT
        self.script_prompt_file = Path("app/prompts/comedy/short/script_generation.md")
        self.title_prompt_file = Path("app/prompts/comedy/short/title_generation.md")
        self.mood_generator = ComedyMoodGenerator()

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
        import re
        
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
        """パースをリトライ付きで実行する"""
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

    def generate_short_titles(
        self,
        theme: str,
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ComedyTitleBatch:
        """テーマからショート動画用タイトルを20個生成
        
        Args:
            theme: テーマ（単語・フレーズ）
            llm: LLMインスタンス
            progress_callback: 進捗通知用コールバック関数
            
        Returns:
            ComedyTitleBatch: 生成されたタイトル候補（20個）
        """
        logger.info(f"ショート動画タイトル生成開始: {theme}")

        try:
            if progress_callback:
                progress_callback("🎬 ショート動画タイトルを生成中...")

            # プロンプト読み込み
            prompt_template = self.load_prompt(self.title_prompt_file)

            # プロンプト構築
            prompt_text = prompt_template.replace("{theme}", theme)

            # パーサー設定
            parser = PydanticOutputParser(pydantic_object=ComedyTitleBatch)
            format_instructions = parser.get_format_instructions()
            prompt_text = prompt_text.replace(
                "{format_instructions}", format_instructions
            )

            # システムメッセージ
            system_message = (
                "あなたは、ショート動画のタイトル作成のプロフェッショナルです。"
                "テーマから、一瞬で視聴者を引き込むインパクトのあるタイトルを20個生成してください。"
                "タイトルは15-25文字程度で、具体的で分かりやすいものにしてください。"
            )

            # LLM呼び出し
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text),
            ]

            logger.info("ショート動画タイトルをLLMで生成中...")
            llm_response = llm.invoke(messages)

            # パース（リトライ付き）
            title_batch = self.parse_with_retry(parser, llm_response)

            logger.info(f"ショート動画タイトル生成成功: {len(title_batch.titles)}個")

            if progress_callback:
                progress_callback("✅ タイトル生成完了")

            return title_batch

        except Exception as e:
            error_msg = f"ショート動画タイトル生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def generate_short_script(
        self,
        title: ComedyTitle,
        llm: Any,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> ComedyScript:
        """タイトルから60秒のショート台本を直接生成
        
        Args:
            title: 生成されたタイトル
            llm: LLMインスタンス
            progress_callback: 進捗通知用コールバック関数(message, progress)
            
        Returns:
            ComedyScript: 生成された60秒台本
        """
        logger.info(f"ショート動画台本生成開始: {title.theme}")

        try:
            if progress_callback:
                progress_callback("🎬 60秒ショート台本を生成中...", 0.0)

            # ランダム機嫌レベル生成
            character_moods = self.mood_generator.generate_random_moods()

            # プロンプト読み込み
            prompt_template = self.load_prompt(self.script_prompt_file)

            # プロンプト構築
            prompt_text = prompt_template.replace("{title}", title.title)
            prompt_text = prompt_text.replace("{theme}", title.theme)
            
            # clickbait_elementsをカンマ区切りで結合
            clickbait_str = "、".join(title.clickbait_elements)
            prompt_text = prompt_text.replace("{clickbait_elements}", clickbait_str)

            prompt_text = prompt_text.replace(
                "{zundamon_mood}", str(character_moods.zundamon)
            )
            prompt_text = prompt_text.replace(
                "{metan_mood}", str(character_moods.metan)
            )
            prompt_text = prompt_text.replace(
                "{tsumugi_mood}", str(character_moods.tsumugi)
            )

            # パーサー設定
            parser = PydanticOutputParser(pydantic_object=ComedyScript)
            format_instructions = parser.get_format_instructions()
            prompt_text = prompt_text.replace(
                "{format_instructions}", format_instructions
            )

            # システムメッセージ
            system_message = (
                "あなたは、60秒ショート動画のお笑い台本作家です。"
                "テンポが速く、最初の3秒で視聴者を引き込む短尺漫談を作成してください。"
                "総セリフ数は12-18セリフ厳守。教育的要素は一切排除してください。"
            )

            # LLM呼び出し
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text),
            ]

            if progress_callback:
                progress_callback("🤖 AIが台本を生成中...", 0.3)

            logger.info("ショート台本をLLMで生成中...")
            logger.info(f"タイトル: {title.title}")
            logger.info(f"フック要素: {title.clickbait_elements}")
            llm_response = llm.invoke(messages)

            if progress_callback:
                progress_callback("📝 台本を解析中...", 0.7)

            # パース（リトライ付き）
            script = self.parse_with_retry(parser, llm_response)
            
            # メタデータ設定
            script.mode = ScriptMode.COMEDY
            script.title = title.title
            script.theme = title.theme
            script.character_moods = character_moods
            script.duration_type = ScriptDuration.SHORT

            # 全セグメント統合
            all_segments = []
            for section in script.sections:
                all_segments.extend(section.segments)
            script.all_segments = all_segments

            # 品質チェック
            total_segments = len(all_segments)
            logger.info(f"全セグメント数: {total_segments}")

            if total_segments < 12:
                logger.warning(f"セリフ数が少なめ: {total_segments}/12")
            elif total_segments > 18:
                logger.warning(f"セリフ数が多め: {total_segments}/18")
            else:
                logger.info(f"セリフ数が適正範囲: {total_segments}")

            # 推定時間計算（1セリフ=約4秒）
            estimated_duration_sec = total_segments * 4
            script.estimated_duration = f"{estimated_duration_sec}秒"

            if progress_callback:
                progress_callback("🎉 ショート台本生成完了！", 1.0)

            logger.info(
                f"ショート台本生成成功: {total_segments}セリフ, "
                f"推定時間: {estimated_duration_sec}秒, "
                f"オチ: {script.ending_type}"
            )

            return script

        except Exception as e:
            error_msg = f"ショート台本生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
