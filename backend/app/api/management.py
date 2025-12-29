from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
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
        from app.config import Paths
        from app.config.content_config.content import Backgrounds

        backgrounds_dir = Paths.get_backgrounds_dir()
        supported_extensions = Backgrounds.get_supported_extensions()

        if not os.path.exists(backgrounds_dir):
            logger.warning(f"Background directory not found: {backgrounds_dir}")
            return []

        backgrounds = []
        # ディレクトリ内のファイルをスキャン
        for filename in os.listdir(backgrounds_dir):
            file_path = os.path.join(backgrounds_dir, filename)
            if not os.path.isfile(file_path):
                continue

            # 拡張子をチェック
            _, ext = os.path.splitext(filename)
            if ext.lower() not in supported_extensions:
                continue

            # ファイル名から拡張子を除いた部分をIDと名前として使用
            name_without_ext = os.path.splitext(filename)[0]
            # 相対パスを作成（assets/backgrounds/filename.png）
            relative_path = f"assets/backgrounds/{filename}"

            backgrounds.append(
                Background(
                    id=name_without_ext,
                    name=name_without_ext,
                    path=relative_path,
                )
            )

        # 名前でソート
        backgrounds.sort(key=lambda x: x.name)
        return backgrounds

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
        from app.core.asset_generators.background_generator import (
            BackgroundImageGenerator,
        )

        generator = BackgroundImageGenerator()
        output_path = generator.generate_background_image(request.name)

        from app.config import Paths

        backgrounds_dir = Paths.get_backgrounds_dir()
        if output_path.startswith(backgrounds_dir):
            relative_path = output_path[len(backgrounds_dir) + 1 :]
        else:
            relative_path = output_path

        return BackgroundGenerateResponse(
            success=True,
            message=f"背景画像「{request.name}」の生成が完了しました",
            path=relative_path,
        )

    except Exception as e:
        logger.error(f"背景生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"背景生成に失敗しました: {str(e)}")


class BackgroundGenerateFromJsonRequest(BaseModel):
    """JSONファイルから背景生成リクエスト"""

    filename: str = Field(..., description="JSONファイル名")


class BackgroundGenerateFromJsonResponse(BaseModel):
    """JSONファイルから背景生成レスポンス"""

    success: bool
    message: str
    generated: Dict[str, str]
    total: int
    generated_count: int


@router.post(
    "/backgrounds/generate-from-json",
    response_model=BackgroundGenerateFromJsonResponse,
)
async def generate_backgrounds_from_json(
    request: BackgroundGenerateFromJsonRequest,
):
    """JSONファイルから背景画像を一括生成する"""
    try:
        from app.api.videos.videos_handlers import handle_get_json_file
        from app.utils.json_utils import extract_background_names_from_json
        from app.core.asset_generators.background_generator import (
            BackgroundImageGenerator,
        )

        json_data = await handle_get_json_file(request.filename)
        background_names = extract_background_names_from_json(json_data)

        if not background_names:
            return BackgroundGenerateFromJsonResponse(
                success=True,
                message="JSONファイルに背景画像の指定がありません",
                generated={},
                total=0,
                generated_count=0,
            )

        generator = BackgroundImageGenerator()
        generated = generator.generate_missing_backgrounds(background_names)

        generated_count = len(generated)
        total = len(background_names)

        if generated_count > 0:
            message = f"{generated_count}件の背景画像の生成が完了しました"
            if generated_count < total:
                skipped_count = total - generated_count
                message += f"（{skipped_count}件は既に存在するためスキップ）"
        else:
            message = "すべての背景画像は既に存在しています"

        return BackgroundGenerateFromJsonResponse(
            success=True,
            message=message,
            generated=generated,
            total=total,
            generated_count=generated_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JSONから背景生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"背景生成に失敗しました: {str(e)}"
        )


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
        raise HTTPException(
            status_code=501, detail="アイテムアップロード機能は実装中です"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"アイテムアップロードエラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class BackgroundCheckRequest(BaseModel):
    """背景画像確認リクエスト"""

    background_names: List[str] = Field(..., description="確認する背景画像名のリスト")


class BackgroundCheckFile(BaseModel):
    """背景画像確認結果（1ファイル）"""

    name: str
    exists: bool
    path: Optional[str] = None


class BackgroundCheckResponse(BaseModel):
    """背景画像確認レスポンス"""

    total: int
    available: int
    missing: int
    files: List[BackgroundCheckFile]


@router.post("/backgrounds/check", response_model=BackgroundCheckResponse)
async def check_backgrounds(request: BackgroundCheckRequest):
    """指定された背景画像の存在確認を行う"""
    try:
        from app.config import Paths, Backgrounds

        backgrounds_dir = Paths.get_backgrounds_dir()
        supported_extensions = Backgrounds.get_supported_extensions()

        if not os.path.exists(backgrounds_dir):
            logger.warning(f"Background directory not found: {backgrounds_dir}")
            # すべての背景画像が存在しないとして返す
            files = [
                BackgroundCheckFile(name=name, exists=False)
                for name in request.background_names
            ]
            return BackgroundCheckResponse(
                total=len(files),
                available=0,
                missing=len(files),
                files=files,
            )

        files = []
        available_count = 0
        missing_count = 0

        # 指定された背景画像名を確認
        for bg_name in request.background_names:
            exists = False
            file_path = None

            # サポートされている拡張子でファイルを探す
            for ext in supported_extensions:
                # 拡張子にドットが含まれている場合と含まれていない場合の両方を確認
                ext_without_dot = ext.lstrip(".")
                possible_filenames = [
                    f"{bg_name}{ext}",
                    f"{bg_name}.{ext_without_dot}",
                ]

                for filename in possible_filenames:
                    file_path = os.path.join(backgrounds_dir, filename)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        # ファイルが実際に読み込めるか確認
                        try:
                            import cv2

                            img = cv2.imread(file_path)
                            if img is not None:
                                exists = True
                                break
                        except Exception as e:
                            logger.warning(f"Failed to read image {file_path}: {e}")
                if exists:
                    break

            files.append(
                BackgroundCheckFile(
                    name=bg_name, exists=exists, path=file_path if exists else None
                )
            )

            if exists:
                available_count += 1
            else:
                missing_count += 1

        return BackgroundCheckResponse(
            total=len(files),
            available=available_count,
            missing=missing_count,
            files=files,
        )

    except Exception as e:
        logger.error(f"背景画像確認エラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"背景画像確認に失敗しました: {str(e)}"
        )


class BackgroundDeleteRequest(BaseModel):
    """背景画像削除リクエスト"""

    ids: List[str] = Field(..., description="削除する背景画像のIDリスト")


class BackgroundDeleteResponse(BaseModel):
    """背景画像削除レスポンス"""

    success: bool
    message: str
    deleted_count: int
    failed_count: int
    failed_ids: List[str] = []


@router.delete("/backgrounds", response_model=BackgroundDeleteResponse)
async def delete_backgrounds(request: BackgroundDeleteRequest):
    """背景画像を削除する"""
    try:
        from app.config import Paths
        from app.config.content_config.content import Backgrounds

        backgrounds_dir = Paths.get_backgrounds_dir()
        supported_extensions = Backgrounds.get_supported_extensions()

        if not os.path.exists(backgrounds_dir):
            raise HTTPException(
                status_code=404, detail="背景画像ディレクトリが見つかりません"
            )

        deleted_count = 0
        failed_count = 0
        failed_ids = []

        for bg_id in request.ids:
            try:
                # サポートされている拡張子でファイルを探す
                found = False
                for ext in supported_extensions:
                    ext_without_dot = ext.lstrip(".")
                    possible_filenames = [
                        f"{bg_id}{ext}",
                        f"{bg_id}.{ext_without_dot}",
                    ]

                    for filename in possible_filenames:
                        file_path = os.path.join(backgrounds_dir, filename)
                        if os.path.exists(file_path) and os.path.isfile(file_path):
                            # ファイルを削除
                            os.remove(file_path)
                            deleted_count += 1
                            found = True
                            logger.info(f"Deleted background image: {file_path}")
                            break

                    if found:
                        break

                if not found:
                    failed_count += 1
                    failed_ids.append(bg_id)
                    logger.warning(f"Background image not found: {bg_id}")

            except Exception as e:
                failed_count += 1
                failed_ids.append(bg_id)
                logger.error(f"Failed to delete background {bg_id}: {str(e)}")

        message = f"{deleted_count}件の背景画像を削除しました"
        if failed_count > 0:
            message += f"（{failed_count}件失敗）"

        return BackgroundDeleteResponse(
            success=deleted_count > 0,
            message=message,
            deleted_count=deleted_count,
            failed_count=failed_count,
            failed_ids=failed_ids,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"背景画像削除エラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"背景画像削除に失敗しました: {str(e)}"
        )


@router.get("/backgrounds/file/{filename:path}")
async def get_background_image(filename: str):
    """背景画像を取得する（静的ファイル配信のフォールバック）"""
    try:
        from app.config import Paths

        backgrounds_dir = Paths.get_backgrounds_dir()
        file_path = os.path.join(backgrounds_dir, filename)

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise HTTPException(
                status_code=404, detail=f"画像が見つかりません: {filename}"
            )

        # メディアタイプを判定
        if filename.lower().endswith(".png"):
            media_type = "image/png"
        elif filename.lower().endswith((".jpg", ".jpeg")):
            media_type = "image/jpeg"
        else:
            media_type = "application/octet-stream"

        return FileResponse(
            file_path,
            media_type=media_type,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"背景画像取得エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """管理APIのヘルスチェック"""
    return {"status": "healthy", "service": "management"}
