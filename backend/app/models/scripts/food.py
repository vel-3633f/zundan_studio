from pydantic import Field, field_validator
from typing import List
from app.models.scripts.base import BaseTitleModel, BaseOutlineModel, BaseScriptModel
from app.models.scripts.common import SectionDefinition, VideoSection, ConversationSegment


class FoodTitle(BaseTitleModel):
    food_name: str = Field(description="食べ物名")
    hook_phrase: str = Field(description="タイトルのフック要素（最も印象的な部分）")

    @field_validator("food_name", "hook_phrase")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()


class FoodOutline(BaseOutlineModel):
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

