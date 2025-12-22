from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict


class SectionDefinition(BaseModel):
    section_key: str = Field(
        description="セクションのキー（例: hook, background, introduction）"
    )
    section_name: str = Field(description="セクションの表示名")
    purpose: str = Field(description="このセクションの目的・役割")
    content_summary: str = Field(description="このセクションで扱う内容の要約")
    min_lines: int = Field(ge=5, le=50, description="最低セリフ数")
    max_lines: int = Field(ge=5, le=50, description="最大セリフ数")
    background: str = Field(
        description="背景シーン（3単語アンダースコア区切り形式、例: modern_study_room）"
    )

    @field_validator("section_key")
    @classmethod
    def validate_section_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("セクションキーは空にできません")
        if not v.replace("_", "").isalnum():
            raise ValueError("セクションキーは英数字とアンダースコアのみ使用できます")
        return v.strip().lower()

    @field_validator("background")
    @classmethod
    def validate_background_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("背景は空にできません")
        return v.strip()

    @field_validator("min_lines", "max_lines")
    @classmethod
    def validate_line_range(cls, v: int) -> int:
        if v < 5 or v > 50:
            raise ValueError("セリフ数は5-50の範囲である必要があります")
        return v


class ConversationSegment(BaseModel):
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
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("visible_characters")
    @classmethod
    def validate_visible_characters_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("表示するキャラクターリストは空にできません")
        cleaned = [char.strip() for char in v if char and char.strip()]
        if not cleaned:
            raise ValueError("有効な表示キャラクターが必要です")
        return cleaned


class VideoSection(BaseModel):
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
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("bgm_volume")
    @classmethod
    def validate_bgm_volume_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("BGM音量は0.0～1.0の範囲である必要があります")
        return v

    @field_validator("segments")
    @classmethod
    def validate_segments_not_empty(
        cls, v: List[ConversationSegment]
    ) -> List[ConversationSegment]:
        if not v:
            raise ValueError("セグメントリストは空にできません")
        return v

