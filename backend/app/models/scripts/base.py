from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ScriptMode(str, Enum):
    COMEDY = "comedy"
    THOUGHT_EXPERIMENT = "thought_experiment"


class ScriptDuration(str, Enum):
    """台本の長さ"""
    SHORT = "short"  # 60秒
    LONG = "long"    # 5-10分


class BaseTitleModel(BaseModel):
    title: str = Field(description="YouTubeタイトル")
    mode: ScriptMode = Field(description="生成モード")


class BaseOutlineModel(BaseModel):
    title: str = Field(description="YouTubeタイトル")
    mode: Optional[ScriptMode] = Field(None, description="生成モード")


class BaseScriptModel(BaseModel):
    title: str = Field(description="YouTubeタイトル")
    mode: ScriptMode = Field(description="生成モード")
    estimated_duration: str = Field(description="推定動画時間")
    duration_type: Optional[ScriptDuration] = Field(None, description="台本の長さタイプ")

