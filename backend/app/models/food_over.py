from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional


class StoryOutline(BaseModel):
    """ストーリー全体のアウトライン（8セクション構造）"""

    title: str = Field(description="YouTubeタイトル")
    food_name: str = Field(description="食べ物名")

    # 各セクションに対応したコンテンツ
    hook_content: str = Field(description="冒頭フックで見せる決定的シーン")
    background_content: str = Field(description="食品の特性・成分・一般的な効果")
    daily_content: str = Field(description="毎日食べることになった理由・状況")
    honeymoon_content: str = Field(description="楽観期の様子・ポジティブな面")
    deterioration_content: List[str] = Field(description="異変期の症状進行・段階的悪化")
    crisis_content: str = Field(description="決定的イベントの具体的内容")
    learning_content: str = Field(description="医学的メカニズム・真相")
    recovery_content: str = Field(description="回復のための解決策")

    @field_validator("title", "food_name", "hook_content", "background_content", "daily_content",
                     "honeymoon_content", "crisis_content", "learning_content", "recovery_content")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        """文字列フィールドが空でないことを確認"""
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("deterioration_content")
    @classmethod
    def validate_deterioration_content_not_empty(cls, v: List[str]) -> List[str]:
        """症状リストが空でなく、かつ3-5要素を持つことを確認"""
        if not v:
            raise ValueError("異変期の症状進行リストは空にできません")
        if len(v) < 3:
            raise ValueError("異変期の症状進行は最低3段階必要です")
        if len(v) > 5:
            raise ValueError("異変期の症状進行は最大5段階です")
        # 各要素が空でないことを確認
        cleaned = [item.strip() for item in v if item and item.strip()]
        if len(cleaned) < 3:
            raise ValueError("異変期の症状進行に有効な要素が不足しています")
        return cleaned


class ConversationSegment(BaseModel):
    """会話セグメントのモデル"""

    speaker: str = Field(description="話者名")
    text: str = Field(description="セリフ内容（字幕表示用・漢字カタカナ含む）")
    text_for_voicevox: str = Field(description="VOICEVOX読み上げ用テキスト（完全ひらがな）")
    expression: str = Field(description="話者の表情名（後方互換性のため維持）")
    visible_characters: List[str] = Field(description="表示するキャラクターのリスト")
    character_expressions: Dict[str, str] = Field(
        default_factory=dict,
        description="各キャラクターの表情を個別に指定 {キャラクター名: 表情名}"
    )
    display_item: Optional[str] = Field(
        default=None,
        description="このセリフで表示する教育アイテム画像のID（ナレーター+めたんセクション専用）"
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
        description="セクションのキー（例: background, learning）"
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
    def validate_segments_not_empty(cls, v: List[ConversationSegment]) -> List[ConversationSegment]:
        """セグメントリストが空でないことを確認"""
        if not v:
            raise ValueError("セグメントリストは空にできません")
        return v


class FoodOverconsumptionScript(BaseModel):
    """食べ物摂取過多動画脚本のモデル"""

    title: str = Field(description="YouTubeタイトル（注目を引く形式）")
    food_name: str = Field(description="対象の食べ物名")
    estimated_duration: str = Field(description="推定動画時間")
    sections: List[VideoSection] = Field(description="動画セクションのリスト")
    all_segments: List[ConversationSegment] = Field(
        description="全会話セグメントの統合リスト"
    )

    @field_validator("title", "food_name", "estimated_duration")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        """文字列フィールドが空でないことを確認"""
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("sections")
    @classmethod
    def validate_sections_not_empty(cls, v: List[VideoSection]) -> List[VideoSection]:
        """セクションリストが空でないことを確認"""
        if not v:
            raise ValueError("セクションリストは空にできません")
        return v

    @field_validator("all_segments")
    @classmethod
    def validate_all_segments_not_empty(cls, v: List[ConversationSegment]) -> List[ConversationSegment]:
        """全セグメントリストが空でないことを確認"""
        if not v:
            raise ValueError("全セグメントリストは空にできません")
        return v

