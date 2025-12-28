"""セクション生成の基底クラス"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.models.scripts.common import VideoSection, ConversationSegment

# StoryOutlineは古いモデルで、現在は存在しないためAnyとして扱う
StoryOutline = Any
from app.config.resource_config.bgm_library import format_bgm_choices_for_prompt, get_section_bgm
from app.utils_legacy.logger import get_logger

logger = get_logger(__name__)

# セクションごとに必要なアウトライン変数のマッピング（8セクション構造）
SECTION_OUTLINE_VARIABLES = {
    "hook": ["hook_content"],  # 冒頭フックで見せる決定的シーン
    "background": ["background_content"],  # 食品の特性・成分・一般的な効果
    "daily": ["daily_content"],  # 毎日食べる理由・状況
    "honeymoon": ["honeymoon_content"],  # 楽観期の様子・ポジティブな面
    "deterioration": ["deterioration_content"],  # 異変期の症状進行・段階的悪化
    "crisis": ["crisis_content"],  # 決定的イベントの具体的内容
    "learning": ["learning_content"],  # 医学的メカニズム・真相
    "recovery": ["recovery_content"],  # 回復のための解決策
}


@dataclass
class SectionContext:
    """セクション生成時のコンテキスト情報"""

    outline: StoryOutline
    food_name: str
    reference_information: str
    previous_sections: List[Dict[str, Any]]


class SectionGeneratorBase:
    """セクション生成の基底クラス"""

    def __init__(
        self,
        section_key: str,
        section_name: str,
        min_lines: int,
        max_lines: int,
        fixed_background: Optional[str] = None,
    ):
        """
        Args:
            section_key: セクションのキー（例: "hook", "background"）
            section_name: セクションの表示名（例: "冒頭フック・危機の予告"）
            min_lines: 最低セリフ数
            max_lines: 最大セリフ数
            fixed_background: 固定背景（Noneの場合は動的選択）
        """
        self.section_key = section_key
        self.section_name = section_name
        self.min_lines = min_lines
        self.max_lines = max_lines
        self.fixed_background = fixed_background
        self.prompt_file = Path(f"app/prompts/sections/section_{section_key}.md")

    def load_section_prompt(self) -> str:
        """セクション固有のプロンプトを読み込む"""
        try:
            if not self.prompt_file.exists():
                raise FileNotFoundError(
                    f"プロンプトファイルが見つかりません: {self.prompt_file}"
                )

            with open(self.prompt_file, "r", encoding="utf-8") as f:
                return f.read().strip()

        except Exception as e:
            logger.error(
                f"セクションプロンプト読み込みエラー ({self.section_key}): {str(e)}"
            )
            raise

    def build_context_text(self, context: SectionContext) -> str:
        """コンテキスト情報をテキスト化（8セクション構造対応）"""
        context_text = f"""
## 全体のアウトライン
- YouTubeタイトル: {context.outline.title}
- 食べ物: {context.outline.food_name}

### セクション別コンテンツ
1. 冒頭フック: {context.outline.hook_content}
2. 食品解説: {context.outline.background_content}
3. 日常導入: {context.outline.daily_content}
4. 楽観期: {context.outline.honeymoon_content}
5. 異変期: {', '.join(context.outline.deterioration_content)}
6. 危機: {context.outline.crisis_content}
7. 真相解明: {context.outline.learning_content}
8. 回復: {context.outline.recovery_content}
"""

        if context.previous_sections:
            context_text += "\n## 前のセクションまでの流れ\n"
            for prev in context.previous_sections:
                context_text += f"""
### {prev['section_name']}（{prev['segment_count']}セリフ）
- 最後の話者: {prev['last_speaker']}
- 最後のセリフ: {prev['last_text']}
- 要約: {prev['summary']}
"""

        return context_text

    def replace_outline_variables(
        self, prompt_text: str, context: SectionContext
    ) -> str:
        """プロンプト内のアウトライン変数を実際の値で置換（8セクション構造対応）

        Args:
            prompt_text: プロンプトテキスト
            context: セクションコンテキスト

        Returns:
            str: 置換後のプロンプトテキスト
        """
        replacements = {
            "{{food_name}}": context.food_name,
            "{{outline_title}}": context.outline.title,
            "{{outline_hook_content}}": context.outline.hook_content,
            "{{outline_background_content}}": context.outline.background_content,
            "{{outline_daily_content}}": context.outline.daily_content,
            "{{outline_honeymoon_content}}": context.outline.honeymoon_content,
            "{{outline_deterioration_content}}": "\n".join(
                f"- {symptom}" for symptom in context.outline.deterioration_content
            ),
            "{{outline_crisis_content}}": context.outline.crisis_content,
            "{{outline_learning_content}}": context.outline.learning_content,
            "{{outline_recovery_content}}": context.outline.recovery_content,
        }

        result = prompt_text
        for var, value in replacements.items():
            result = result.replace(var, value)

        return result

    def generate(self, context: SectionContext, llm: Any) -> VideoSection:
        """セクションを生成する

        Args:
            context: セクションコンテキスト
            llm: LLMインスタンス

        Returns:
            VideoSection: 生成されたセクション
        """
        logger.info(
            f"セクション生成開始: {self.section_name} ({self.min_lines}-{self.max_lines}セリフ)"
        )

        try:
            section_prompt_raw = self.load_section_prompt()
            context_text = self.build_context_text(context)

            parser = PydanticOutputParser(pydantic_object=VideoSection)
            format_instructions = parser.get_format_instructions()

            # アウトライン変数を置換（{{format_instructions}}を除く）
            section_prompt = self.replace_outline_variables(section_prompt_raw, context)

            # {{format_instructions}}を削除
            section_prompt = section_prompt.replace("{{format_instructions}}", "")

            full_prompt = f"""
                {section_prompt}

                ---

                {context_text}

                ## 参考情報
                {context.reference_information}

                ## 出力形式

                {format_instructions}
                """

            # システムメッセージ
            system_message = "あなたは、YouTube動画の脚本家です。視聴者を引きつける魅力的な会話劇を生成するプロフェッショナルです。"

            # LLMを直接呼び出す（ChatPromptTemplateの変数参照問題を回避）
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=full_prompt),
            ]

            logger.info(f"{self.section_name} をLLMで生成中...")
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
            section.section_key = self.section_key

            # セクションタイプに応じた固定BGMを設定
            bgm_config = get_section_bgm(self.section_key)
            section.bgm_id = bgm_config["bgm_id"]
            section.bgm_volume = bgm_config["volume"]
            logger.info(
                f"BGM設定: {bgm_config['bgm_id']} (volume: {bgm_config['volume']})"
            )

            # 固定背景が指定されている場合は上書き
            if self.fixed_background:
                section.scene_background = self.fixed_background
                logger.info(f"背景を固定設定で上書き: {self.fixed_background}")

            segment_count = len(section.segments)
            logger.info(
                f"セクション生成成功: {self.section_name} - {segment_count}セリフ"
            )

            # セリフ数チェック
            if segment_count < self.min_lines:
                logger.warning(f"セリフ数が少なめ: {segment_count}/{self.min_lines}")
            elif segment_count > self.max_lines:
                logger.warning(f"セリフ数が多め: {segment_count}/{self.max_lines}")

            return section

        except Exception as e:
            error_msg = f"セクション生成エラー ({self.section_name}): {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    @staticmethod
    def summarize_section(section: VideoSection) -> str:
        """セクションを要約（次のセクションへの引き継ぎ用）"""
        summary_parts = []

        summary_parts.append(f"主な内容: {section.section_name}")

        zundamon_segments = [s for s in section.segments if s.speaker == "zundamon"]
        if zundamon_segments:
            last_zundamon = zundamon_segments[-1]
            summary_parts.append(f"ずんだもんの状態: {last_zundamon.text[:30]}...")

        if "異変" in section.section_name or "危機" in section.section_name:
            symptoms = SectionGeneratorBase._extract_symptoms(section.segments)
            if symptoms:
                summary_parts.append(f"現れた症状: {', '.join(symptoms[:3])}")

        return " / ".join(summary_parts)

    @staticmethod
    def _extract_symptoms(segments: List[ConversationSegment]) -> List[str]:
        """セグメントから症状キーワードを抽出"""
        symptoms = []
        symptom_keywords = [
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
        ]

        for seg in segments:
            for keyword in symptom_keywords:
                if keyword in seg.text and keyword not in symptoms:
                    symptoms.append(keyword)

        return symptoms
