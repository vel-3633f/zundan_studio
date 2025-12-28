"""汎用セクションジェネレーター（両モード共通）"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from app.models.script_models import VideoSection, SectionDefinition, ScriptMode
from app.config.resource_config.bgm_library import get_section_bgm
from app.core.script_generators.section_context import SectionContext
from app.core.script_generators.context.section_context_builder import build_context_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GenericSectionGenerator:
    """汎用セクション生成クラス（両モード対応）"""

    def __init__(self, mode: ScriptMode):
        """
        Args:
            mode: 生成モード（FOOD or COMEDY）
        """
        self.mode = mode
        self.section_prompt_file = Path(
            f"app/prompts/{mode.value}/section_generation.md"
        )

    def load_section_prompt(self) -> str:
        """セクション生成プロンプトを読み込む"""
        try:
            if not self.section_prompt_file.exists():
                raise FileNotFoundError(
                    f"セクションプロンプトファイルが見つかりません: {self.section_prompt_file}"
                )

            with open(self.section_prompt_file, "r", encoding="utf-8") as f:
                return f.read().strip()

        except Exception as e:
            logger.error(f"セクションプロンプト読み込みエラー: {str(e)}")
            raise

    def build_context_text(self, context: SectionContext) -> str:
        """コンテキスト情報をテキスト化する"""
        return build_context_text(context, self.mode)

    def generate(self, context: SectionContext, llm: Any) -> VideoSection:
        """セクションを生成する

        Args:
            context: セクションコンテキスト
            llm: LLMインスタンス

        Returns:
            VideoSection: 生成されたセクション
        """
        logger.info(
            f"セクション生成開始 ({self.mode.value}): {context.section_definition.section_name} "
            f"({context.section_definition.min_lines}-{context.section_definition.max_lines}セリフ)"
        )

        try:
            section_prompt_template = self.load_section_prompt()
            context_text = self.build_context_text(context)

            parser = PydanticOutputParser(pydantic_object=VideoSection)
            format_instructions = parser.get_format_instructions()

            # プロンプト構築
            full_prompt = f"""
{section_prompt_template}

---

{context_text}

## 参考情報
{context.reference_information}

## 出力形式

{format_instructions}
"""

            # システムメッセージ（Comedy専用）
            system_message = "あなたは、お笑い台本の脚本家です。バカバカしく面白い会話劇を生成するプロフェッショナルです。教育的要素は一切排除してください。"

            # LLMを直接呼び出す
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=full_prompt),
            ]

            logger.info(f"{context.section_definition.section_name} をLLMで生成中...")
            llm_response = llm.invoke(messages)

            # LLMの応答内のタイポを修正（text_for_voivevox → text_for_voicevox）
            if isinstance(llm_response.content, str):
                llm_response.content = llm_response.content.replace(
                    "text_for_voivevox", "text_for_voicevox"
                )
                llm_response.content = llm_response.content.replace(
                    '"text_for_voivevox"', '"text_for_voicevox"'
                )

            # LLMの応答をパース
            section = parser.invoke(llm_response)

            # セクションキーを設定
            section.section_key = context.section_definition.section_key

            # BGM設定
            bgm_config = get_section_bgm(context.section_definition.section_key)
            section.bgm_id = bgm_config["bgm_id"]
            section.bgm_volume = bgm_config["volume"]
            logger.info(
                f"BGM設定: {bgm_config['bgm_id']} (volume: {bgm_config['volume']})"
            )

            # 背景が指定されている場合は上書き
            if context.section_definition.background:
                section.scene_background = context.section_definition.background
                logger.info(
                    f"背景を設定で上書き: {context.section_definition.background}"
                )

            segment_count = len(section.segments)
            logger.info(
                f"セクション生成成功: {context.section_definition.section_name} - {segment_count}セリフ"
            )

            # セリフ数チェック
            if segment_count < context.section_definition.min_lines:
                logger.warning(
                    f"セリフ数が少なめ: {segment_count}/{context.section_definition.min_lines}"
                )
            elif segment_count > context.section_definition.max_lines:
                logger.warning(
                    f"セリフ数が多め: {segment_count}/{context.section_definition.max_lines}"
                )

            return section

        except Exception as e:
            error_msg = f"セクション生成エラー ({context.section_definition.section_name}): {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    @staticmethod
    def summarize_section(section: VideoSection) -> str:
        """セクションを要約（次のセクションへの引き継ぎ用）"""
        summary_parts = []

        summary_parts.append(f"主な内容: {section.section_name}")

        # ずんだもんの最後のセリフ
        zundamon_segments = [s for s in section.segments if s.speaker == "zundamon"]
        if zundamon_segments:
            last_zundamon = zundamon_segments[-1]
            summary_parts.append(f"ずんだもんの状態: {last_zundamon.text[:30]}...")

        # 重要なキーワード抽出
        if (
            "異変" in section.section_name
            or "危機" in section.section_name
            or "カオス" in section.section_name
        ):
            keywords = GenericSectionGenerator._extract_keywords(section.segments)
            if keywords:
                summary_parts.append(f"キーワード: {', '.join(keywords[:3])}")

        return " / ".join(summary_parts)

    @staticmethod
    def _extract_keywords(segments: List) -> List[str]:
        """セグメントからキーワードを抽出"""
        keywords = []
        keyword_patterns = [
            "痛",
            "だるい",
            "眠れない",
            "集中できない",
            "肌荒れ",
            "頭痛",
            "吐き気",
            "疲労",
            "動悸",
            "めまい",
            "不眠",
            "イライラ",
            "怒",
            "喧嘩",
            "爆発",
            "崩壊",
            "終わ",
            "やばい",
            "最悪",
        ]

        for seg in segments:
            for keyword in keyword_patterns:
                if keyword in seg.text and keyword not in keywords:
                    keywords.append(keyword)

        return keywords
