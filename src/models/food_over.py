from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class StoryOutline(BaseModel):
    """ストーリー全体のアウトライン"""

    title: str = Field(description="YouTubeタイトル")
    hook_scene_summary: str = Field(description="冒頭で見せる決定的シーンの概要")
    eating_reason: str = Field(description="毎日食べることになった理由")
    symptom_progression: List[str] = Field(description="症状の段階的進行リスト")
    critical_event: str = Field(description="決定的イベントの具体的内容")
    medical_mechanism: str = Field(description="体内で起きる医学的メカニズム")
    solution: str = Field(description="回復のための具体的解決策")


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


class FoodOverconsumptionScript(BaseModel):
    """食べ物摂取過多動画脚本のモデル"""

    title: str = Field(description="YouTubeタイトル（注目を引く形式）")
    food_name: str = Field(description="対象の食べ物名")
    estimated_duration: str = Field(description="推定動画時間")
    sections: List[VideoSection] = Field(description="動画セクションのリスト")
    all_segments: List[ConversationSegment] = Field(
        description="全会話セグメントの統合リスト"
    )
