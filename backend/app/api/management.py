from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()


class Background(BaseModel):
    """背景情報"""
    id: str
    name: str
    path: str


@router.get("/backgrounds", response_model=List[Background])
async def list_backgrounds():
    """背景一覧を取得する"""
    try:
        return []
        
    except Exception as e:
        logger.error(f"背景一覧取得エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backgrounds/upload")
async def upload_background(file: UploadFile = File(...)):
    """背景画像をアップロードする"""
    try:
        raise HTTPException(status_code=501, detail="背景アップロード機能は実装中です")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"背景アップロードエラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class BackgroundGenerateRequest(BaseModel):
    """背景生成リクエスト"""
    name: str = Field(..., description="背景名", min_length=1, max_length=100)


class BackgroundGenerateResponse(BaseModel):
    """背景生成レスポンス"""
    success: bool
    message: str
    path: Optional[str] = None


@router.post("/backgrounds/generate", response_model=BackgroundGenerateResponse)
async def generate_background(request: BackgroundGenerateRequest):
    """背景画像を生成する"""
    try:
        from app.core.asset_generators.background_generator import BackgroundImageGenerator
        
        generator = BackgroundImageGenerator()
        output_path = generator.generate_background_image(request.name)
        
        # 相対パスに変換（必要に応じて）
        from app.config import Paths
        backgrounds_dir = Paths.get_backgrounds_dir()
        if output_path.startswith(backgrounds_dir):
            relative_path = output_path[len(backgrounds_dir) + 1:]
        else:
            relative_path = output_path
        
        return BackgroundGenerateResponse(
            success=True,
            message=f"背景画像 '{request.name}' を生成しました",
            path=relative_path
        )
        
    except Exception as e:
        logger.error(f"背景生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"背景生成に失敗しました: {str(e)}")


class Item(BaseModel):
    """アイテム情報"""
    id: str
    name: str
    path: str
    description: Optional[str] = None


@router.get("/items", response_model=List[Item])
async def list_items():
    """アイテム一覧を取得する"""
    try:
        return []
        
    except Exception as e:
        logger.error(f"アイテム一覧取得エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/items/upload")
async def upload_item(file: UploadFile = File(...)):
    """アイテム画像をアップロードする"""
    try:
        raise HTTPException(status_code=501, detail="アイテムアップロード機能は実装中です")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"アイテムアップロードエラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """管理APIのヘルスチェック"""
    return {"status": "healthy", "service": "management"}
