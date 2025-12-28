"""お笑いモード専用の台本生成ロジック"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from app.models.script_models import (
    ScriptMode,
    ComedyTitle,
    ComedyOutline,
    ComedyScript,
)
from app.core.script_generators.generic_section_generator import GenericSectionGenerator
from app.core.script_generators.section_context import SectionContext
from .comedy_mood_generator import ComedyMoodGenerator
from .comedy_title_generator import ComedyTitleGenerator
from app.utils_legacy.logger import get_logger

logger = get_logger(__name__)


class ComedyScriptGenerator:
    """お笑いモード専用生成ロジック"""

    def __init__(self):
        self.mode = ScriptMode.COMEDY
        self.outline_prompt_file = Path("app/prompts/comedy/outline_generation.md")
        self.mood_generator = ComedyMoodGenerator()
        self.title_generator = ComedyTitleGenerator()

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

    def generate_random_moods(self):
        """ランダムな機嫌レベルを生成（後方互換性のため）"""
        return self.mood_generator.generate_random_moods()

    def get_mood_description(self, character: str, mood: int) -> str:
        """機嫌レベルから説明文を生成（後方互換性のため）"""
        return self.mood_generator.get_mood_description(character, mood)

    def generate_script(
        self,
        outline: ComedyOutline,
        llm: Any,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> ComedyScript:
        """アウトラインから詳細台本を生成

        Args:
            outline: 生成されたアウトライン
            llm: LLMインスタンス
            progress_callback: 進捗通知用コールバック関数(message, progress)

        Returns:
            ComedyScript: 生成された台本
        """
        logger.info(f"お笑いモード 台本生成開始: {outline.theme}")

        try:
            if progress_callback:
                progress_callback("🎬 各セクションの詳細を生成中...", 0.0)

            generator = GenericSectionGenerator(ScriptMode.COMEDY)
            sections = []
            previous_sections_summary = []

            # 機嫌レベルを辞書形式に変換
            character_moods_dict = {
                "zundamon": outline.character_moods.zundamon,
                "metan": outline.character_moods.metan,
                "tsumugi": outline.character_moods.tsumugi,
            }

            # 各セクションを生成
            for i, section_def in enumerate(outline.sections):
                is_final = i == len(outline.sections) - 1

                if progress_callback:
                    progress_callback(
                        f"📝 セクション {i+1}/{len(outline.sections)}: {section_def.section_name} を生成中... "
                        f"({section_def.min_lines}-{section_def.max_lines}セリフ)",
                        (i / len(outline.sections)),
                    )

                # コンテキスト構築
                context = SectionContext(
                    mode=ScriptMode.COMEDY,
                    section_definition=section_def,
                    story_summary=outline.story_summary,
                    reference_information="",  # お笑いモードでは参照情報不要
                    previous_sections=previous_sections_summary,
                    character_moods=character_moods_dict,
                    forced_ending_type=outline.ending_type,
                    is_final_section=is_final,
                )

                try:
                    section = generator.generate(context, llm)
                    sections.append(section)

                    # 次のセクション用の要約を作成
                    section_summary = {
                        "section_name": section.section_name,
                        "segment_count": len(section.segments),
                        "last_speaker": (
                            section.segments[-1].speaker if section.segments else ""
                        ),
                        "last_text": (
                            section.segments[-1].text if section.segments else ""
                        ),
                        "summary": generator.summarize_section(section),
                    }
                    previous_sections_summary.append(section_summary)

                    if progress_callback:
                        progress_callback(
                            f"✅ {section_def.section_name} 完了 ({len(section.segments)}セリフ)",
                            ((i + 1) / len(outline.sections)),
                        )

                    logger.info(
                        f"セクション {i+1}/{len(outline.sections)} 完了: "
                        f"{section_def.section_name} - {len(section.segments)}セリフ"
                    )

                except Exception as e:
                    logger.error(
                        f"セクション生成エラー ({section_def.section_name}): {str(e)}",
                        exc_info=True,
                    )
                    raise

            # 品質チェック
            if progress_callback:
                progress_callback("🔍 品質チェック中...", 0.95)

            all_segments = []
            for section in sections:
                all_segments.extend(section.segments)

            total_segments = len(all_segments)
            logger.info(f"全セグメント数: {total_segments}")

            if total_segments < 60:
                logger.warning(f"セリフ数が少なめ: {total_segments}/60")
            elif total_segments > 120:
                logger.warning(f"セリフ数が多め: {total_segments}/120")
            else:
                logger.info(f"セリフ数が適正範囲: {total_segments}")

            # 推定時間計算
            estimated_duration_sec = total_segments * 4
            estimated_duration = (
                f"{estimated_duration_sec // 60}分{estimated_duration_sec % 60}秒"
            )

            # 台本作成
            script = ComedyScript(
                title=outline.title,
                mode=ScriptMode.COMEDY,
                theme=outline.theme,
                estimated_duration=estimated_duration,
                character_moods=outline.character_moods,
                sections=sections,
                all_segments=all_segments,
                ending_type=outline.ending_type,
            )

            if progress_callback:
                progress_callback("🎉 台本生成完了！", 1.0)

            logger.info(
                f"台本生成成功: {total_segments}セリフ, "
                f"推定時間: {estimated_duration}, "
                f"オチ: {outline.ending_type}"
            )

            return script

        except Exception as e:
            error_msg = f"台本生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def generate_title_batch(
        self, llm: Any, progress_callback: Optional[Callable[[str], None]] = None
    ):
        """ランダムにタイトルを20-30個量産（後方互換性のため）"""
        return self.title_generator.generate_title_batch(llm, progress_callback)

    def generate_title(
        self,
        theme: str,
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ComedyTitle:
        """テーマからバカバカしいタイトルを生成（後方互換性のため）"""
        return self.title_generator.generate_title(theme, llm, progress_callback)

    def generate_outline(
        self,
        title: ComedyTitle,
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ComedyOutline:
        """タイトルから動的セクション構造のアウトラインを生成

        Args:
            title: 生成されたタイトル
            llm: LLMインスタンス
            progress_callback: 進捗通知用コールバック関数

        Returns:
            ComedyOutline: 生成されたアウトライン
        """
        logger.info(f"お笑いモード アウトライン生成開始: {title.theme}")

        try:
            if progress_callback:
                progress_callback("📋 アウトラインを生成中...")

            # ランダム機嫌レベル生成
            character_moods = self.generate_random_moods()

            # プロンプト読み込み
            prompt_template = self.load_prompt(self.outline_prompt_file)

            # プロンプト構築
            prompt_text = prompt_template.replace("{theme}", title.theme)
            prompt_text = prompt_text.replace("{title}", title.title)

            # clickbait_elementsを個別に渡す
            # 最大3つのフック要素を想定（足りない場合は空文字）
            for i in range(1, 4):
                element_key = f"{{clickbait_element_{i}}}"
                if i <= len(title.clickbait_elements):
                    prompt_text = prompt_text.replace(
                        element_key, title.clickbait_elements[i - 1]
                    )
                else:
                    # フック要素が3つ未満の場合は空文字で置換
                    prompt_text = prompt_text.replace(element_key, "（なし）")

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
            parser = PydanticOutputParser(pydantic_object=ComedyOutline)
            format_instructions = parser.get_format_instructions()
            prompt_text = prompt_text.replace(
                "{format_instructions}", format_instructions
            )

            # システムメッセージ
            system_message = (
                "あなたは、お笑い台本の脚本家です。"
                "バカバカしく面白いストーリー構成を設計するプロフェッショナルです。"
                "教育的要素は一切排除してください。"
                "重要: 与えられたタイトルとフック要素を必ずストーリーに反映させ、"
                "視聴者の期待を裏切らない展開を作成してください。"
            )

            # LLM呼び出し
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text),
            ]

            logger.info("アウトラインをLLMで生成中...")
            logger.info(f"タイトル: {title.title}")
            logger.info(f"フック要素: {title.clickbait_elements}")
            llm_response = llm.invoke(messages)

            # パース
            outline = parser.invoke(llm_response)
            outline.mode = ScriptMode.COMEDY
            outline.title = title.title
            outline.character_moods = character_moods

            logger.info(f"アウトライン生成成功: {len(outline.sections)}セクション構成")
            logger.info(f"オチのタイプ: {outline.ending_type}")
            logger.info(
                f"機嫌レベル: ずんだもん={character_moods.zundamon}, "
                f"めたん={character_moods.metan}, つむぎ={character_moods.tsumugi}"
            )
            for i, section in enumerate(outline.sections, 1):
                logger.info(
                    f"  セクション{i}: {section.section_name} "
                    f"({section.min_lines}-{section.max_lines}セリフ)"
                )

            return outline

        except Exception as e:
            error_msg = f"アウトライン生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
