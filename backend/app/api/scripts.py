"""Script generation API endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from app.models.food_over import StoryOutline, FoodOverconsumptionScript
from app.core.generate_food_over_sectioned import (
    generate_outline_only,
    generate_sections_from_approved_outline,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class OutlineRequest(BaseModel):
    """アウトライン生成リクエスト"""

    food_name: str = Field(..., description="食べ物名")
    model: Optional[str] = Field(None, description="使用するLLMモデルID")
    temperature: Optional[float] = Field(None, description="生成温度")


class OutlineResponse(BaseModel):
    """アウトライン生成レスポンス"""

    outline: StoryOutline
    search_results: Dict[str, Any]
    reference_info: str
    model: str
    temperature: float


class SectionRequest(BaseModel):
    """セクション生成リクエスト"""

    outline: StoryOutline
    food_name: str
    reference_info: str
    model: str
    temperature: float
    llm_config: Dict[str, Any]


@router.post("/outline", response_model=OutlineResponse)
async def generate_outline(request: OutlineRequest):
    """
    食べ物名からアウトラインを生成する

    - **food_name**: 対象の食べ物名
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    try:
        logger.info(f"アウトライン生成リクエスト: {request.food_name}")

        result = generate_outline_only(
            food_name=request.food_name,
            model=request.model,
            temperature=request.temperature,
        )

        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result.get("details", "アウトライン生成に失敗しました"),
            )

        return OutlineResponse(
            outline=result["outline"],
            search_results=result.get("search_results", {}),
            reference_info=result["reference_info"],
            model=result["model"],
            temperature=result["temperature"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"アウトライン生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sections", response_model=FoodOverconsumptionScript)
async def generate_sections(request: SectionRequest):
    """
    承認されたアウトラインからセクションを生成する

    - **outline**: 承認されたアウトライン
    - **food_name**: 食べ物名
    - **reference_info**: 参照情報
    - **model**: 使用するLLMモデル
    - **temperature**: 生成温度
    """
    try:
        logger.info(f"セクション生成リクエスト: {request.food_name}")

        result = generate_sections_from_approved_outline(
            outline=request.outline,
            food_name=request.food_name,
            reference_info=request.reference_info,
            model=request.model,
            temperature=request.temperature,
            model_config=request.llm_config,
        )

        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result.get("details", "セクション生成に失敗しました"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"セクション生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """スクリプト生成APIのヘルスチェック"""
    return {"status": "healthy", "service": "scripts"}
