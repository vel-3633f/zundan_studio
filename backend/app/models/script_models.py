"""統合台本生成システムのデータモデル"""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict


class ScriptMode(str, Enum):
    """台本生成モード"""

    FOOD = "food"  # 食べ物摂取過多モード
    COMEDY = "comedy"  # お笑い漫談モード


# === 共通基底モデル ===


class BaseTitleModel(BaseModel):
    """タイトル基底モデル"""

    title: str = Field(description="YouTubeタイトル")
    mode: ScriptMode = Field(description="生成モード")


class BaseOutlineModel(BaseModel):
    """アウトライン基底モデル"""

    title: str = Field(description="YouTubeタイトル")
    mode: ScriptMode = Field(description="生成モード")


class BaseScriptModel(BaseModel):
    """台本基底モデル"""

    title: str = Field(description="YouTubeタイトル")
    mode: ScriptMode = Field(description="生成モード")
    estimated_duration: str = Field(description="推定動画時間")


# === 共通セクション定義 ===


class SectionDefinition(BaseModel):
    """セクション定義（動的生成用）"""

    section_key: str = Field(
        description="セクションのキー（例: hook, background, introduction）"
    )
    section_name: str = Field(description="セクションの表示名")
    purpose: str = Field(description="このセクションの目的・役割")
    content_summary: str = Field(description="このセクションで扱う内容の要約")
    min_lines: int = Field(ge=5, le=50, description="最低セリフ数")
    max_lines: int = Field(ge=5, le=50, description="最大セリフ数")
    fixed_background: Optional[str] = Field(
        None, description="固定背景（指定がない場合は動的選択）"
    )

    @field_validator("section_key")
    @classmethod
    def validate_section_key(cls, v: str) -> str:
        """セクションキーが英数字とアンダースコアのみであることを確認"""
        if not v or not v.strip():
            raise ValueError("セクションキーは空にできません")
        if not v.replace("_", "").isalnum():
            raise ValueError("セクションキーは英数字とアンダースコアのみ使用できます")
        return v.strip().lower()

    @field_validator("min_lines", "max_lines")
    @classmethod
    def validate_line_range(cls, v: int) -> int:
        """セリフ数が有効範囲内か確認"""
        if v < 5 or v > 50:
            raise ValueError("セリフ数は5-50の範囲である必要があります")
        return v


class ConversationSegment(BaseModel):
    """会話セグメントのモデル"""

    speaker: str = Field(description="話者名")
    text: str = Field(description="セリフ内容（字幕表示用・漢字カタカナ含む）")
    text_for_voicevox: str = Field(
        description="VOICEVOX読み上げ用テキスト（完全ひらがな）"
    )
    expression: str = Field(description="話者の表情名（後方互換性のため維持）")
    visible_characters: List[str] = Field(description="表示するキャラクターのリスト")
    character_expressions: Dict[str, str] = Field(
        default_factory=dict,
        description="各キャラクターの表情を個別に指定 {キャラクター名: 表情名}",
    )
    display_item: Optional[str] = Field(
        default=None, description="このセリフで表示する教育アイテム画像のID"
    )

    @field_validator("speaker", "text", "text_for_voicevox", "expression")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        """文字列フィールドが空でないことを確認"""
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("visible_characters")
    @classmethod
    def validate_visible_characters_not_empty(cls, v: List[str]) -> List[str]:
        """表示キャラクターリストが空でないことを確認"""
        if not v:
            raise ValueError("表示するキャラクターリストは空にできません")
        cleaned = [char.strip() for char in v if char and char.strip()]
        if not cleaned:
            raise ValueError("有効な表示キャラクターが必要です")
        return cleaned


class VideoSection(BaseModel):
    """動画セクションのモデル"""

    section_name: str = Field(description="セクション名")
    section_key: Optional[str] = Field(
        default=None,
        description="セクションのキー（例: hook, background, introduction）",
    )
    scene_background: str = Field(description="このセクションで使用する背景シーン")
    bgm_id: str = Field(default="none", description="このセクションで使用するBGMのID")
    bgm_volume: float = Field(default=0.25, description="BGMの音量（0.0〜1.0）")
    segments: List[ConversationSegment] = Field(
        description="このセクションの会話セグメント"
    )

    @field_validator("section_name", "scene_background", "bgm_id")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        """文字列フィールドが空でないことを確認"""
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("bgm_volume")
    @classmethod
    def validate_bgm_volume_range(cls, v: float) -> float:
        """BGM音量が0.0～1.0の範囲内か確認"""
        if not (0.0 <= v <= 1.0):
            raise ValueError("BGM音量は0.0～1.0の範囲である必要があります")
        return v

    @field_validator("segments")
    @classmethod
    def validate_segments_not_empty(
        cls, v: List[ConversationSegment]
    ) -> List[ConversationSegment]:
        """セグメントリストが空でないことを確認"""
        if not v:
            raise ValueError("セグメントリストは空にできません")
        return v


# === 食べ物モード専用 ===


class FoodTitle(BaseTitleModel):
    """食べ物モードのタイトル"""

    food_name: str = Field(description="食べ物名")
    hook_phrase: str = Field(description="タイトルのフック要素（最も印象的な部分）")

    @field_validator("food_name", "hook_phrase")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()


class FoodOutline(BaseOutlineModel):
    """食べ物モードのアウトライン（動的セクション構造）"""

    food_name: str = Field(description="食べ物名")
    story_summary: str = Field(description="ストーリー全体の要約（2-3文）")
    sections: List[SectionDefinition] = Field(
        description="動的に生成されたセクション定義リスト"
    )

    @field_validator("food_name", "story_summary")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("sections")
    @classmethod
    def validate_sections_not_empty(
        cls, v: List[SectionDefinition]
    ) -> List[SectionDefinition]:
        if not v:
            raise ValueError("セクションリストは空にできません")
        if len(v) < 3:
            raise ValueError("最低3つのセクションが必要です")
        return v


class FoodScript(BaseScriptModel):
    """食べ物モードの完成台本"""

    food_name: str = Field(description="食べ物名")
    sections: List[VideoSection] = Field(description="動画セクションのリスト")
    all_segments: List[ConversationSegment] = Field(
        description="全会話セグメントの統合リスト"
    )

    @field_validator("food_name")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("sections")
    @classmethod
    def validate_sections_not_empty(cls, v: List[VideoSection]) -> List[VideoSection]:
        if not v:
            raise ValueError("セクションリストは空にできません")
        return v

    @field_validator("all_segments")
    @classmethod
    def validate_all_segments_not_empty(
        cls, v: List[ConversationSegment]
    ) -> List[ConversationSegment]:
        if not v:
            raise ValueError("全セグメントリストは空にできません")
        return v


# === お笑いモード専用 ===


class CharacterMood(BaseModel):
    """キャラクター機嫌レベル"""

    zundamon: int = Field(ge=0, le=100, description="ずんだもんの機嫌レベル（0-100）")
    metan: int = Field(ge=0, le=100, description="めたんの機嫌レベル（0-100）")
    tsumugi: int = Field(ge=0, le=100, description="つむぎの機嫌レベル（0-100）")

    @field_validator("zundamon", "metan", "tsumugi")
    @classmethod
    def validate_mood_range(cls, v: int) -> int:
        """機嫌レベルが0-100の範囲内か確認"""
        if not (0 <= v <= 100):
            raise ValueError("機嫌レベルは0-100の範囲である必要があります")
        return v


class ComedyTitleCandidate(BaseModel):
    """お笑いタイトル候補（量産用）"""

    id: int = Field(description="候補ID")
    title: str = Field(description="タイトル")
    hook_pattern: str = Field(description="使用したお笑いフックパターン")
    situation: str = Field(description="シチュエーション")
    chaos_element: str = Field(description="カオス要素")
    expected_conflict: str = Field(description="予想される対立構造")


class ComedyTitleBatch(BaseModel):
    """お笑いタイトル量産結果"""

    titles: List[ComedyTitleCandidate] = Field(
        description="生成されたタイトル候補リスト（5-10個）"
    )

    @field_validator("titles")
    @classmethod
    def validate_titles_count(
        cls, v: List[ComedyTitleCandidate]
    ) -> List[ComedyTitleCandidate]:
        """タイトル数が5-10個であることを確認"""
        if len(v) < 5 or len(v) > 10:
            raise ValueError("タイトルは5-10個生成する必要があります")
        return v


class ComedyTitle(BaseTitleModel):
    """お笑いモードのタイトル"""

    theme: str = Field(description="漫談のテーマ")
    clickbait_elements: List[str] = Field(description="煽り要素リスト（3-5個）")

    @field_validator("theme")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("clickbait_elements")
    @classmethod
    def validate_clickbait_elements(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("煽り要素リストは空にできません")
        if len(v) < 3:
            raise ValueError("最低3つの煽り要素が必要です")
        cleaned = [elem.strip() for elem in v if elem and elem.strip()]
        if len(cleaned) < 3:
            raise ValueError("有効な煽り要素が不足しています")
        return cleaned


class ComedyOutline(BaseOutlineModel):
    """お笑いモードのアウトライン（動的セクション構造）"""

    theme: str = Field(description="漫談のテーマ")
    story_summary: str = Field(description="漫談全体の流れ（2-3文）")
    character_moods: CharacterMood = Field(description="各キャラの機嫌レベル")
    forced_ending_type: str = Field(description="強制終了のタイプ")
    sections: List[SectionDefinition] = Field(
        description="動的に生成されたセクション定義リスト"
    )

    @field_validator("theme", "story_summary", "forced_ending_type")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("sections")
    @classmethod
    def validate_sections_not_empty(
        cls, v: List[SectionDefinition]
    ) -> List[SectionDefinition]:
        if not v:
            raise ValueError("セクションリストは空にできません")
        if len(v) < 3:
            raise ValueError("最低3つのセクションが必要です")
        return v


class ComedyScript(BaseScriptModel):
    """お笑いモードの完成台本"""

    theme: str = Field(description="漫談のテーマ")
    character_moods: CharacterMood = Field(description="各キャラの機嫌レベル")
    sections: List[VideoSection] = Field(description="動画セクションのリスト")
    all_segments: List[ConversationSegment] = Field(
        description="全会話セグメントの統合リスト"
    )
    ending_type: str = Field(description="強制終了のタイプ")

    @field_validator("theme", "ending_type")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("sections")
    @classmethod
    def validate_sections_not_empty(cls, v: List[VideoSection]) -> List[VideoSection]:
        if not v:
            raise ValueError("セクションリストは空にできません")
        return v

    @field_validator("all_segments")
    @classmethod
    def validate_all_segments_not_empty(
        cls, v: List[ConversationSegment]
    ) -> List[ConversationSegment]:
        if not v:
            raise ValueError("全セグメントリストは空にできません")
        return v
