"""台本生成APIのリクエスト/レスポンスモデル"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.models.script_models import (
    ScriptMode,
    ComedyTitle,
    ComedyTitleBatch,
    ComedyOutline,
    ComedyScript,
    YouTubeMetadata,
    ThemeBatch,
)


class TitleRequest(BaseModel):
    """タイトル生成リクエスト"""

    mode: ScriptMode = Field(default=ScriptMode.COMEDY, description="生成モード（comedyのみ）")
    input_text: str = Field(..., description="漫談のテーマ")
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class TitleResponse(BaseModel):
    """タイトル生成レスポンス"""

    title: ComedyTitle
    reference_info: str = Field(default="", description="参照情報（常に空文字）")
    search_results: Dict[str, Any] = Field(default_factory=dict, description="検索結果（常に空）")
    model: str
    temperature: float


class OutlineRequest(BaseModel):
    """アウトライン生成リクエスト"""

    mode: ScriptMode = Field(default=ScriptMode.COMEDY, description="生成モード（comedyのみ）")
    title_data: ComedyTitle = Field(..., description="生成されたタイトル")
    reference_info: Optional[str] = Field(None, description="参照情報（使用されない）")
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class OutlineResponse(BaseModel):
    """アウトライン生成レスポンス"""

    outline: ComedyOutline
    youtube_metadata: Optional[YouTubeMetadata] = Field(
        default=None, description="YouTubeメタデータ（生成失敗時はNone）"
    )
    model: str
    temperature: float


class ScriptRequest(BaseModel):
    """台本生成リクエスト"""

    mode: ScriptMode = Field(default=ScriptMode.COMEDY, description="生成モード（comedyのみ）")
    outline_data: ComedyOutline = Field(..., description="生成されたアウトライン")
    reference_info: Optional[str] = Field(None, description="参照情報（使用されない）")
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class ScriptResponse(BaseModel):
    """台本生成レスポンス"""

    script: ComedyScript


class FullScriptRequest(BaseModel):
    """完全台本生成リクエスト（3段階一括）"""

    mode: ScriptMode = Field(default=ScriptMode.COMEDY, description="生成モード（comedyのみ）")
    input_text: str = Field(..., description="漫談のテーマ")
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class FullScriptResponse(BaseModel):
    """完全台本生成レスポンス"""

    script: ComedyScript
    title: ComedyTitle = Field(..., description="生成されたタイトル")
    outline: ComedyOutline = Field(..., description="生成されたアウトライン")
    youtube_metadata: Optional[YouTubeMetadata] = Field(
        default=None, description="YouTubeメタデータ（生成失敗時はNone）"
    )


class ThemeBatchResponse(BaseModel):
    """テーマ候補バッチレスポンス"""

    themes: list[str] = Field(description="テーマ候補のリスト")


class ThemeTitleRequest(BaseModel):
    """テーマベースタイトル生成リクエスト"""

    theme: str = Field(..., description="テーマ（単語・フレーズ）")
    model: Optional[str] = Field(None, description="使用するLLMモデル")
    temperature: Optional[float] = Field(None, description="生成温度")


class ShortScriptRequest(BaseModel):
    """ショート動画台本生成リクエスト（60秒）"""

    mode: ScriptMode = Field(default=ScriptMode.COMEDY, description="生成モード（comedyのみ）")
    title_data: ComedyTitle = Field(..., description="生成されたタイトル")
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class ShortTitleRequest(BaseModel):
    """ショート動画タイトル生成リクエスト"""

    theme: str = Field(..., description="テーマ（単語・フレーズ）")
    model: Optional[str] = Field(None, description="使用するLLMモデル")
    temperature: Optional[float] = Field(None, description="生成温度")

