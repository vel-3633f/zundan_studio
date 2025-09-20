from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional, List, Any, Union


class ConversationSegment(BaseModel):
    """会話セグメントのモデル"""

    speaker: str = Field(description="話者名")
    text: str = Field(description="セリフ内容")
    expression: str = Field(description="表情名")
    visible_characters: List[str] = Field(description="表示するキャラクターのリスト")
    character_items: Dict[str, str] = Field(description="キャラクターが持つアイテム")

    @field_validator('character_items')
    @classmethod
    def validate_character_items(cls, v: Dict[str, str]) -> Dict[str, str]:
        """ずんだもん以外のキャラクターのアイテムをnoneに設定"""
        validated_items = {}
        for character, item in v.items():
            if character == "zundamon":
                validated_items[character] = item
            else:
                validated_items[character] = "none"
        return validated_items


class VideoSection(BaseModel):
    """動画セクションのモデル"""

    section_name: str = Field(description="セクション名")
    scene_background: str = Field(description="このセクションで使用する背景シーン")
    segments: List[ConversationSegment] = Field(
        description="このセクションの会話セグメント"
    )


class FoodOverconsumptionScript(BaseModel):
    """食べ物摂取過多動画脚本のモデル"""

    title: str = Field(description="YouTubeタイトル（注目を引く形式）")
    food_name: str = Field(description="対象の食べ物名")
    estimated_duration: str = Field(description="推定動画時間")
    sections: List[VideoSection] = Field(description="動画セクションのリスト")
    all_segments: List[ConversationSegment] = Field(
        description="全会話セグメントの統合リスト"
    )
