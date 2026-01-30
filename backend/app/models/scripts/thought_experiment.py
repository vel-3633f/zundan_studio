"""思考実験モード用のデータモデル"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import logging
from app.models.scripts.base import BaseTitleModel, BaseOutlineModel, BaseScriptModel
from app.models.scripts.common import (
    SectionDefinition,
    VideoSection,
    ConversationSegment,
)
from app.models.scripts.comedy import CharacterMood, YouTubeMetadata

logger = logging.getLogger(__name__)


class ThoughtExperimentTitleCandidate(BaseModel):
    """思考実験タイトル候補"""
    
    id: int = Field(description="候補ID")
    title: str = Field(description="タイトル（50文字以内）")
    theme: str = Field(description="思考実験のテーマ")
    category: str = Field(description="テーマのカテゴリ（社会リセット・崩壊、SF・オタク妄想、極限状態・科学）")
    hook_type: str = Field(description="使用した思考実験フックタイプ（極限状態、パラドックス、世界観崩壊、倫理的ジレンマなど）")
    expected_discussion: str = Field(description="予想される議論の方向性")
    
    @field_validator("title")
    @classmethod
    def validate_title_length(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("タイトルは空にできません")
        cleaned = v.strip()
        if len(cleaned) > 50:
            logger.warning(
                f"タイトルが50文字を超えています（現在: {len(cleaned)}文字）: {cleaned[:50]}..."
            )
        return cleaned


class ThoughtExperimentTitleBatch(BaseModel):
    """思考実験タイトル候補バッチ"""
    
    titles: List[ThoughtExperimentTitleCandidate] = Field(
        description="生成されたタイトル候補リスト（20個）"
    )
    
    @field_validator("titles")
    @classmethod
    def validate_titles_count(
        cls, v: List[ThoughtExperimentTitleCandidate]
    ) -> List[ThoughtExperimentTitleCandidate]:
        if len(v) < 15 or len(v) > 25:
            raise ValueError("タイトルは15-25個生成する必要があります")
        return v


class ThoughtExperimentTitle(BaseTitleModel):
    """思考実験モード用タイトル"""
    
    theme: str = Field(description="思考実験のテーマ（例: もしもゾンビパンデミックが起きたら）")
    category: str = Field(description="テーマのカテゴリ（社会リセット・崩壊、SF・オタク妄想、極限状態・科学）")
    
    @field_validator("title")
    @classmethod
    def validate_title_length(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("タイトルは空にできません")
        cleaned = v.strip()
        if len(cleaned) > 50:
            logger.warning(
                f"タイトルが50文字を超えています（現在: {len(cleaned)}文字）: {cleaned[:50]}..."
            )
        return cleaned
    
    @field_validator("theme", "category")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()


class ThoughtExperimentOutline(BaseOutlineModel):
    """思考実験モード用アウトライン"""
    
    theme: str = Field(description="思考実験のテーマ")
    category: str = Field(description="テーマのカテゴリ")
    story_summary: str = Field(description="動画全体の流れ（2-3文）")
    character_moods: CharacterMood = Field(description="各キャラの機嫌レベル")
    ending_type: str = Field(description="オチのタイプ（30文字以内）")
    sections: List[SectionDefinition] = Field(
        description="動的に生成されたセクション定義リスト"
    )
    youtube_metadata: Optional[YouTubeMetadata] = Field(
        default=None, description="YouTubeメタデータ（ディスクリプションとタグ）"
    )
    
    @field_validator("theme", "category", "story_summary", "ending_type")
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


class ThoughtExperimentScript(BaseScriptModel):
    """思考実験モード用台本"""
    
    theme: str = Field(description="思考実験のテーマ")
    category: str = Field(description="テーマのカテゴリ")
    character_moods: CharacterMood = Field(description="各キャラの機嫌レベル")
    sections: List[VideoSection] = Field(description="動画セクションのリスト")
    all_segments: List[ConversationSegment] = Field(
        description="全会話セグメントの統合リスト"
    )
    ending_type: str = Field(description="オチのタイプ")
    youtube_metadata: Optional[YouTubeMetadata] = Field(
        default=None, description="YouTubeメタデータ（ディスクリプションとタグ）"
    )
    
    @field_validator("theme", "category", "ending_type")
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
