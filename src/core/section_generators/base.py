"""セクション生成の基底クラス"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.models.food_over import VideoSection, StoryOutline, ConversationSegment
from config.bgm_library import format_bgm_choices_for_prompt, get_section_bgm
from src.utils.logger import get_logger

logger = get_logger(__name__)

COMMON_RULES_FILE = Path("src/prompts/sections/common_rules.md")

# セクションごとに必要なアウトライン変数のマッピング
SECTION_OUTLINE_VARIABLES = {
    "hook": ["critical_event"],  # 決定的イベントの一部
    "background": [],  # 食品解説なのでアウトライン情報は不要
    "daily": ["eating_reason"],  # 毎日食べる理由
    "honeymoon": ["eating_reason"],  # 継続
    "deterioration": ["symptom_progression"],  # 症状の進行
    "crisis": ["critical_event"],  # 決定的イベントの完全版
    "learning": ["medical_mechanism"],  # 医学的メカニズム
    "recovery": ["solution"],  # 解決策
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
        self.prompt_file = Path(f"src/prompts/sections/section_{section_key}.md")

    def load_common_rules(self) -> str:
        """共通ルールを読み込む"""
        try:
            if not COMMON_RULES_FILE.exists():
                raise FileNotFoundError(
                    f"共通ルールファイルが見つかりません: {COMMON_RULES_FILE}"
                )

            with open(COMMON_RULES_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()

        except Exception as e:
            logger.error(f"共通ルール読み込みエラー: {str(e)}")
            raise

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
        """コンテキスト情報をテキスト化"""
        context_text = f"""
## 全体のアウトライン
- YouTubeタイトル: {context.outline.title}
- 食べ物: {context.food_name}
- 毎日食べる理由: {context.outline.eating_reason}
- 症状の進行: {', '.join(context.outline.symptom_progression)}
- 決定的イベント: {context.outline.critical_event}
- 医学的メカニズム: {context.outline.medical_mechanism}
- 解決策: {context.outline.solution}
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
        """プロンプト内のアウトライン変数を実際の値で置換

        Args:
            prompt_text: プロンプトテキスト
            context: セクションコンテキスト

        Returns:
            str: 置換後のプロンプトテキスト
        """
        replacements = {
            "{{food_name}}": context.food_name,
            "{{outline_title}}": context.outline.title,
            "{{outline_eating_reason}}": context.outline.eating_reason,
            "{{outline_symptom_progression}}": "\n".join(
                f"- {symptom}" for symptom in context.outline.symptom_progression
            ),
            "{{outline_critical_event}}": context.outline.critical_event,
            "{{outline_medical_mechanism}}": context.outline.medical_mechanism,
            "{{outline_solution}}": context.outline.solution,
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
            common_rules = self.load_common_rules()
            section_prompt_raw = self.load_section_prompt()
            context_text = self.build_context_text(context)

            parser = PydanticOutputParser(pydantic_object=VideoSection)
            format_instructions = parser.get_format_instructions()

            # アウトライン変数を置換（{{format_instructions}}を除く）
            section_prompt = self.replace_outline_variables(section_prompt_raw, context)

            # {{format_instructions}}を削除
            section_prompt = section_prompt.replace("{{format_instructions}}", "")

            full_prompt = f"""
                {common_rules}

                ---

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
