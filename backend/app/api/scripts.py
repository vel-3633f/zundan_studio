"""統合台本生成API（食べ物・お笑い両モード対応）"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
import logging

from app.models.script_models import (
    ScriptMode,
    FoodTitle,
    FoodOutline,
    FoodScript,
    ComedyTitle,
    ComedyOutline,
    ComedyScript,
    ComedyTitleBatch,
)
from app.core.script_generators.unified_script_generator import UnifiedScriptGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


class TitleRequest(BaseModel):
    """タイトル生成リクエスト"""

    mode: ScriptMode = Field(..., description="生成モード（food or comedy）")
    input_text: str = Field(
        ..., description="食べ物名（foodモード）またはテーマ（comedyモード）"
    )
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class TitleResponse(BaseModel):
    """タイトル生成レスポンス"""

    title: Union[FoodTitle, ComedyTitle]
    reference_info: str = Field(description="参照情報（foodモードのみ）")
    search_results: Dict[str, Any] = Field(
        default_factory=dict, description="検索結果（foodモードのみ）"
    )
    model: str
    temperature: float


class OutlineRequest(BaseModel):
    """アウトライン生成リクエスト"""

    mode: ScriptMode = Field(..., description="生成モード（food or comedy）")
    title_data: Union[FoodTitle, ComedyTitle] = Field(
        ..., description="生成されたタイトル"
    )
    reference_info: Optional[str] = Field(
        None, description="参照情報（foodモードのみ）"
    )
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class OutlineResponse(BaseModel):
    """アウトライン生成レスポンス"""

    outline: Union[FoodOutline, ComedyOutline]
    model: str
    temperature: float


class ScriptRequest(BaseModel):
    """台本生成リクエスト"""

    mode: ScriptMode = Field(..., description="生成モード（food or comedy）")
    outline_data: Union[FoodOutline, ComedyOutline] = Field(
        ..., description="生成されたアウトライン"
    )
    reference_info: Optional[str] = Field(
        None, description="参照情報（foodモードのみ）"
    )
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class ScriptResponse(BaseModel):
    """台本生成レスポンス"""

    script: Union[FoodScript, ComedyScript]


class FullScriptRequest(BaseModel):
    """完全台本生成リクエスト（3段階一括）"""

    mode: ScriptMode = Field(..., description="生成モード（food or comedy）")
    input_text: str = Field(
        ..., description="食べ物名（foodモード）またはテーマ（comedyモード）"
    )
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class FullScriptResponse(BaseModel):
    """完全台本生成レスポンス"""

    script: Union[FoodScript, ComedyScript]


# === エンドポイント ===


@router.post("/title", response_model=TitleResponse)
async def generate_title(request: TitleRequest):
    """
    モード別タイトル生成

    - **mode**: 生成モード（food or comedy）
    - **input_text**: 食べ物名またはテーマ
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    try:
        logger.info(
            f"タイトル生成リクエスト ({request.mode.value}): {request.input_text}"
        )

        generator = UnifiedScriptGenerator(request.mode)

        title, reference_info, model_settings = generator.generate_title(
            input_text=request.input_text,
            model=request.model,
            temperature=request.temperature,
        )

        return TitleResponse(
            title=title,
            reference_info=reference_info,
            search_results=model_settings.get("search_results", {}),
            model=model_settings["model"],
            temperature=model_settings["temperature"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"タイトル生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outline", response_model=OutlineResponse)
async def generate_outline(request: OutlineRequest):
    """
    モード別アウトライン生成

    - **mode**: 生成モード（food or comedy）
    - **title_data**: 生成されたタイトル
    - **reference_info**: 参照情報（foodモードのみ）
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    try:
        logger.info(f"アウトライン生成リクエスト ({request.mode.value})")

        generator = UnifiedScriptGenerator(request.mode)

        outline, model_settings = generator.generate_outline(
            title_data=request.title_data,
            reference_info=request.reference_info or "",
            model=request.model,
            temperature=request.temperature,
        )

        return OutlineResponse(
            outline=outline,
            model=model_settings["model"],
            temperature=model_settings["temperature"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"アウトライン生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/script", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    """
    モード別台本生成

    - **mode**: 生成モード（food or comedy）
    - **outline_data**: 生成されたアウトライン
    - **reference_info**: 参照情報（foodモードのみ）
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    try:
        logger.info(f"台本生成リクエスト ({request.mode.value})")

        generator = UnifiedScriptGenerator(request.mode)

        script = generator.generate_script(
            outline_data=request.outline_data,
            reference_info=request.reference_info or "",
            model=request.model,
            temperature=request.temperature,
        )

        return ScriptResponse(script=script)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"台本生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full", response_model=FullScriptResponse)
async def generate_full_script(request: FullScriptRequest):
    """
    3段階一括生成（Title → Outline → Script）

    - **mode**: 生成モード（food or comedy）
    - **input_text**: 食べ物名またはテーマ
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    try:
        logger.info(
            f"完全台本生成リクエスト ({request.mode.value}): {request.input_text}"
        )

        generator = UnifiedScriptGenerator(request.mode)

        script = generator.generate_full_script(
            input_text=request.input_text,
            model=request.model,
            temperature=request.temperature,
        )

        return FullScriptResponse(script=script)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"完全台本生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comedy/titles/batch")
async def generate_comedy_titles_batch():
    """
    お笑いモード: ランダムタイトル量産（20-30個）

    テーマ入力不要で、AIが自動的にバカバカしいタイトルを20-30個生成します。
    """
    try:
        logger.info("お笑いタイトル量産リクエスト")

        from app.core.script_generators.comedy_script_generator import ComedyScriptGenerator
        from app.core.script_generators.generate_food_over import create_llm_instance
        from app.config.models import get_default_model_config

        generator = ComedyScriptGenerator()

        # モデル設定（お笑いモードは高temperature推奨）
        model_config = get_default_model_config()
        model = model_config["id"]
        temperature = 0.9  # お笑いモードは高めに固定

        llm = create_llm_instance(model, temperature, model_config)

        # タイトル量産
        title_batch = generator.generate_title_batch(llm)

        return title_batch

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"お笑いタイトル量産エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """
    利用可能なAIモデルの一覧を取得
    
    Returns:
        - models: 利用可能なモデルのリスト
        - default_model_id: デフォルトモデルのID
        - recommended_model_id: 推奨モデルのID
    """
    from app.config.models import (
        AVAILABLE_MODELS,
        DEFAULT_MODEL_ID,
        get_recommended_model_id,
    )

    return {
        "models": AVAILABLE_MODELS,
        "default_model_id": DEFAULT_MODEL_ID,
        "recommended_model_id": get_recommended_model_id(),
    }


@router.get("/health")
async def health_check():
    """スクリプト生成APIのヘルスチェック"""
    return {"status": "healthy", "service": "scripts"}
