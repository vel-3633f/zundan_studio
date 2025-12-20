from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from app.models.script_models import (
    ScriptMode,
    FoodTitle,
    FoodOutline,
    FoodScript,
    SectionDefinition,
)
from app.core.script_generators.generic_section_generator import GenericSectionGenerator, SectionContext
from app.core.script_generators.generate_food_over import (
    search_food_information,
    format_search_results_for_prompt,
)
from app.config.content_config.closing_section import create_closing_section
from app.utils_legacy.logger import get_logger

logger = get_logger(__name__)


class FoodScriptGenerator:
    """食べ物モード専用生成ロジック"""

    def __init__(self):
        self.mode = ScriptMode.FOOD
        self.title_prompt_file = Path("app/prompts/food/title_generation.md")
        self.outline_prompt_file = Path("app/prompts/food/outline_generation.md")

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

    def generate_title(
        self,
        food_name: str,
        search_results: Dict[str, List[str]],
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> FoodTitle:
        """食べ物名と検索結果から煽りタイトルを生成

        Args:
            food_name: 食べ物名
            search_results: Tavily検索結果
            llm: LLMインスタンス
            progress_callback: 進捗通知用コールバック関数

        Returns:
            FoodTitle: 生成されたタイトル
        """
        logger.info(f"食べ物モード タイトル生成開始: {food_name}")

        try:
            if progress_callback:
                progress_callback("📝 タイトルを生成中...")

            # プロンプト読み込み
            prompt_template = self.load_prompt(self.title_prompt_file)
            reference_info = format_search_results_for_prompt(search_results)

            # プロンプト構築
            prompt_text = prompt_template.replace("{food_name}", food_name)
            prompt_text = prompt_text.replace("{reference_information}", reference_info)

            # パーサー設定
            parser = PydanticOutputParser(pydantic_object=FoodTitle)
            format_instructions = parser.get_format_instructions()
            prompt_text = prompt_text.replace(
                "{format_instructions}", format_instructions
            )

            # システムメッセージ
            system_message = "あなたは、YouTube動画のタイトル作成のプロフェッショナルです。視聴者の興味を引き、クリックしたくなるタイトルを生成します。"

            # LLM呼び出し
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text),
            ]

            logger.info("タイトルをLLMで生成中...")
            llm_response = llm.invoke(messages)

            # パース
            title = parser.invoke(llm_response)
            title.mode = ScriptMode.FOOD

            logger.info(f"タイトル生成成功: {title.title}")
            return title

        except Exception as e:
            error_msg = f"タイトル生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def generate_outline(
        self,
        title: FoodTitle,
        reference_info: str,
        llm: Any,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> FoodOutline:
        """タイトルと参照情報から動的セクション構造のアウトラインを生成

        Args:
            title: 生成されたタイトル
            reference_info: 参照情報
            llm: LLMインスタンス
            progress_callback: 進捗通知用コールバック関数

        Returns:
            FoodOutline: 生成されたアウトライン
        """
        logger.info(f"食べ物モード アウトライン生成開始: {title.food_name}")

        try:
            if progress_callback:
                progress_callback("📋 アウトラインを生成中...")

            # プロンプト読み込み
            prompt_template = self.load_prompt(self.outline_prompt_file)

            # プロンプト構築
            prompt_text = prompt_template.replace("{food_name}", title.food_name)
            prompt_text = prompt_text.replace("{reference_information}", reference_info)

            # パーサー設定
            parser = PydanticOutputParser(pydantic_object=FoodOutline)
            format_instructions = parser.get_format_instructions()
            prompt_text = prompt_text.replace(
                "{format_instructions}", format_instructions
            )

            # システムメッセージ
            system_message = "あなたは、YouTube動画の脚本家です。視聴者を引きつける魅力的なストーリー構成を設計するプロフェッショナルです。"

            # LLM呼び出し
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt_text),
            ]

            logger.info("アウトラインをLLMで生成中...")
            llm_response = llm.invoke(messages)

            # パース
            outline = parser.invoke(llm_response)
            outline.mode = ScriptMode.FOOD
            outline.title = title.title

            logger.info(f"アウトライン生成成功: {len(outline.sections)}セクション構成")
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

    def generate_script(
        self,
        outline: FoodOutline,
        reference_info: str,
        llm: Any,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> FoodScript:
        """アウトラインから詳細台本を生成

        Args:
            outline: 生成されたアウトライン
            reference_info: 参照情報
            llm: LLMインスタンス
            progress_callback: 進捗通知用コールバック関数(message, progress)

        Returns:
            FoodScript: 生成された台本
        """
        logger.info(f"食べ物モード 台本生成開始: {outline.food_name}")

        try:
            if progress_callback:
                progress_callback("🎬 各セクションの詳細を生成中...", 0.0)

            generator = GenericSectionGenerator(ScriptMode.FOOD)
            sections = []
            previous_sections_summary = []

            # 各セクションを生成
            for i, section_def in enumerate(outline.sections):
                if progress_callback:
                    progress_callback(
                        f"📝 セクション {i+1}/{len(outline.sections)}: {section_def.section_name} を生成中... "
                        f"({section_def.min_lines}-{section_def.max_lines}セリフ)",
                        (i / len(outline.sections)),
                    )

                # コンテキスト構築
                context = SectionContext(
                    mode=ScriptMode.FOOD,
                    section_definition=section_def,
                    story_summary=outline.story_summary,
                    reference_information=reference_info,
                    previous_sections=previous_sections_summary,
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
                progress_callback("🔍 品質チェック中...", 0.9)

            all_segments = []
            for section in sections:
                all_segments.extend(section.segments)

            total_segments = len(all_segments)
            logger.info(f"全セグメント数（締めくくり前）: {total_segments}")

            if total_segments < 130:
                logger.warning(f"セリフ数が目標より少ない: {total_segments}/130")
            elif total_segments > 160:
                logger.warning(f"セリフ数が目標より多い: {total_segments}/160")
            else:
                logger.info(f"セリフ数が適正範囲: {total_segments}")

            # 締めくくりセクションを追加
            if progress_callback:
                progress_callback("🎬 締めくくりセクションを追加中...", 0.95)

            closing_section = create_closing_section()
            sections.append(closing_section)
            all_segments.extend(closing_section.segments)

            total_segments_with_closing = len(all_segments)
            logger.info(
                f"締めくくりセクション追加完了: +{len(closing_section.segments)}セリフ "
                f"(合計: {total_segments_with_closing})"
            )

            # 推定時間計算
            estimated_duration_sec = total_segments_with_closing * 4
            estimated_duration = (
                f"{estimated_duration_sec // 60}分{estimated_duration_sec % 60}秒"
            )

            # 台本作成
            script = FoodScript(
                title=outline.title,
                mode=ScriptMode.FOOD,
                food_name=outline.food_name,
                estimated_duration=estimated_duration,
                sections=sections,
                all_segments=all_segments,
            )

            if progress_callback:
                progress_callback("🎉 台本生成完了！", 1.0)

            logger.info(
                f"台本生成成功: {total_segments_with_closing}セリフ, "
                f"推定時間: {estimated_duration}"
            )

            return script

        except Exception as e:
            error_msg = f"台本生成エラー: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
