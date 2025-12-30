from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from app.models.scripts.base import BaseTitleModel, BaseOutlineModel, BaseScriptModel
from app.models.scripts.common import SectionDefinition, VideoSection, ConversationSegment


class CharacterMood(BaseModel):
    zundamon: int = Field(ge=0, le=100, description="ずんだもんの機嫌レベル（0-100）")
    metan: int = Field(ge=0, le=100, description="めたんの機嫌レベル（0-100）")
    tsumugi: int = Field(ge=0, le=100, description="つむぎの機嫌レベル（0-100）")

    @field_validator("zundamon", "metan", "tsumugi")
    @classmethod
    def validate_mood_range(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("機嫌レベルは0-100の範囲である必要があります")
        return v


class ThemeBatch(BaseModel):
    """テーマ候補バッチ"""
    themes: List[str] = Field(
        description="テーマ候補のリスト（15-20個）",
        min_length=15,
        max_length=20
    )

    @field_validator("themes")
    @classmethod
    def validate_themes_count(cls, v: List[str]) -> List[str]:
        if len(v) < 15 or len(v) > 20:
            raise ValueError("テーマは15-20個生成する必要があります")
        cleaned = [theme.strip() for theme in v if theme and theme.strip()]
        if len(cleaned) < 15:
            raise ValueError("有効なテーマが不足しています")
        return cleaned


class ComedyTitleCandidate(BaseModel):
    id: int = Field(description="候補ID")
    title: str = Field(description="タイトル（30文字以内）")
    hook_pattern: str = Field(description="使用したお笑いフックパターン")
    situation: str = Field(description="シチュエーション")
    chaos_element: str = Field(description="カオス要素")
    expected_conflict: str = Field(description="予想される対立構造")

    @field_validator("title")
    @classmethod
    def validate_title_length(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("タイトルは空にできません")
        cleaned = v.strip()
        if len(cleaned) > 30:
            raise ValueError(f"タイトルは30文字以内である必要があります（現在: {len(cleaned)}文字）")
        return cleaned


class ComedyTitleBatch(BaseModel):
    titles: List[ComedyTitleCandidate] = Field(
        description="生成されたタイトル候補リスト（20-30個）"
    )

    @field_validator("titles")
    @classmethod
    def validate_titles_count(
        cls, v: List[ComedyTitleCandidate]
    ) -> List[ComedyTitleCandidate]:
        if len(v) < 20 or len(v) > 30:
            raise ValueError("タイトルは20-30個生成する必要があります")
        return v


class ComedyTitle(BaseTitleModel):
    theme: str = Field(description="漫談のテーマ")
    clickbait_elements: List[str] = Field(description="煽り要素リスト（3-5個）")

    @field_validator("title")
    @classmethod
    def validate_title_length(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("タイトルは空にできません")
        cleaned = v.strip()
        if len(cleaned) > 30:
            raise ValueError(f"タイトルは30文字以内である必要があります（現在: {len(cleaned)}文字）")
        return cleaned

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
    theme: str = Field(description="漫談のテーマ")
    story_summary: str = Field(description="漫談全体の流れ（2-3文）")
    character_moods: CharacterMood = Field(description="各キャラの機嫌レベル")
    ending_type: str = Field(description="オチのタイプ")
    sections: List[SectionDefinition] = Field(
        description="動的に生成されたセクション定義リスト"
    )

    @field_validator("theme", "story_summary", "ending_type")
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


class YouTubeMetadata(BaseModel):
    """YouTubeメタデータ"""

    tags: List[str] = Field(description="YouTubeタグ（最大15個）")
    description: str = Field(description="YouTube説明文（5000文字以内）")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("タグリストは空にできません")
        if len(v) > 15:
            raise ValueError("タグは最大15個までです")
        cleaned = [tag.strip() for tag in v if tag and tag.strip()]
        if not cleaned:
            raise ValueError("有効なタグがありません")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description_length(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("説明文は空にできません")
        cleaned = v.strip()
        if len(cleaned) > 5000:
            raise ValueError("説明文は5000文字以内である必要があります")
        return cleaned


class ComedyScript(BaseScriptModel):
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

