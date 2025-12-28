"""お笑い漫談台本生成API（Comedy専用）"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from app.models.script_models import (
    ScriptMode,
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


# === エンドポイント ===


@router.post("/title", response_model=TitleResponse)
async def generate_title(request: TitleRequest):
    """
    タイトル生成（Comedy専用）

    - **input_text**: 漫談のテーマ
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    try:
        logger.info(f"タイトル生成リクエスト: テーマ={request.input_text}")

        generator = UnifiedScriptGenerator(ScriptMode.COMEDY)

        title, reference_info, model_info = generator.generate_title(
            input_text=request.input_text,
            model=request.model,
            temperature=request.temperature,
        )

        return TitleResponse(
            title=title,
            reference_info=reference_info,
            search_results={},
            model=model_info["model"],
            temperature=model_info["temperature"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"タイトル生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outline", response_model=OutlineResponse)
async def generate_outline(request: OutlineRequest):
    """
    アウトライン生成（Comedy専用）

    - **title_data**: 生成されたタイトル
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    try:
        logger.info(f"アウトライン生成リクエスト: タイトル={request.title_data.title}")

        generator = UnifiedScriptGenerator(ScriptMode.COMEDY)

        outline, model_info = generator.generate_outline(
            title_data=request.title_data,
            reference_info=request.reference_info or "",
            model=request.model,
            temperature=request.temperature,
        )

        return OutlineResponse(
            outline=outline,
            model=model_info["model"],
            temperature=model_info["temperature"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"アウトライン生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/script", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    """
    台本生成（Comedy専用）

    - **outline_data**: 生成されたアウトライン
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    try:
        logger.info(f"台本生成リクエスト: タイトル={request.outline_data.title}")

        generator = UnifiedScriptGenerator(ScriptMode.COMEDY)

        script, model_info = generator.generate_script(
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
    完全台本生成（3段階一括）（Comedy専用）

    - **input_text**: 漫談のテーマ
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    try:
        logger.info(f"完全台本生成リクエスト: テーマ={request.input_text}")

        generator = UnifiedScriptGenerator(ScriptMode.COMEDY)

        # 1. タイトル生成
        title, reference_info, model_info = generator.generate_title(
            input_text=request.input_text,
            model=request.model,
            temperature=request.temperature,
        )

        # 2. アウトライン生成
        outline, _ = generator.generate_outline(
            title_data=title,
            reference_info=reference_info,
            model=request.model,
            temperature=request.temperature,
        )

        # 3. 台本生成
        script, _ = generator.generate_script(
            outline_data=outline,
            reference_info=reference_info,
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


@router.post("/save")
async def save_script_to_file(request: dict):
    """
    生成された台本をJSONファイルとして保存
    
    Args:
        request: {"script": 台本データ, "filename": ファイル名（オプション）}
    
    Returns:
        保存されたファイルのパス
    """
    try:
        import json
        from pathlib import Path
        from datetime import datetime
        
        script_data = request.get("script")
        if not script_data:
            raise HTTPException(status_code=400, detail="台本データが必要です")
        
        # ファイル名生成（指定がない場合は自動生成）
        filename = request.get("filename")
        if not filename:
            # タイトルから安全なファイル名を生成
            title = script_data.get("title", "script")
            # 日本語を削除し、英数字のみに
            safe_title = "".join(c for c in title if c.isalnum() or c in ("-", "_"))
            if not safe_title:
                safe_title = "script"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title}_{timestamp}.json"
        
        # 拡張子確認
        if not filename.endswith(".json"):
            filename += ".json"
        
        # 保存先ディレクトリ
        output_dir = Path("outputs/json")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル保存
        file_path = output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"台本を保存しました: {file_path}")
        
        return {
            "success": True,
            "file_path": str(file_path),
            "filename": filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"台本保存エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """
    利用可能なAIモデルの一覧を取得
    
    Returns:
        - models: 利用可能なモデルのリスト
        - default_model_id: デフォルトモデルID
        - recommended_model_id: 推奨モデルID
    """
    try:
        from app.config.models import get_all_models, get_default_model_config

        models = get_all_models()
        default_config = get_default_model_config()

        return {
            "models": models,
            "default_model_id": default_config["id"],
            "recommended_model_id": default_config["id"],
        }

    except Exception as e:
        logger.error(f"モデル一覧取得エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "service": "comedy_script_generator"}
