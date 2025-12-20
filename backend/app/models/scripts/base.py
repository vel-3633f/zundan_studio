from enum import Enum
from pydantic import BaseModel, Field


class ScriptMode(str, Enum):
    FOOD = "food"
    COMEDY = "comedy"


class BaseTitleModel(BaseModel):
    title: str = Field(description="YouTubeタイトル")
    mode: ScriptMode = Field(description="生成モード")


class BaseOutlineModel(BaseModel):
    title: str = Field(description="YouTubeタイトル")
    mode: ScriptMode = Field(description="生成モード")


class BaseScriptModel(BaseModel):
    title: str = Field(description="YouTubeタイトル")
    mode: ScriptMode = Field(description="生成モード")
    estimated_duration: str = Field(description="推定動画時間")

