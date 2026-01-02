"""台本生成APIのエンドポイントハンドラー"""

from fastapi import HTTPException
from typing import Dict, Any
import logging

from app.models.script_models import ScriptMode, ComedyTitleBatch
from app.core.script_generators.unified_script_generator import UnifiedScriptGenerator
from .scripts_models import (
    TitleRequest,
    TitleResponse,
    OutlineRequest,
    OutlineResponse,
    ScriptRequest,
    ScriptResponse,
    FullScriptRequest,
    FullScriptResponse,
    ThemeBatchResponse,
    ThemeTitleRequest,
)

logger = logging.getLogger(__name__)


async def handle_generate_title(request: TitleRequest) -> TitleResponse:
    """タイトル生成ハンドラー"""
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


async def handle_generate_outline(request: OutlineRequest) -> OutlineResponse:
    """アウトライン生成ハンドラー"""
    try:
        logger.info(f"アウトライン生成リクエスト: タイトル={request.title_data.title}")

        generator = UnifiedScriptGenerator(ScriptMode.COMEDY)

        outline, youtube_metadata, model_info = generator.generate_outline(
            title_data=request.title_data,
            reference_info=request.reference_info or "",
            model=request.model,
            temperature=request.temperature,
        )

        return OutlineResponse(
            outline=outline,
            youtube_metadata=youtube_metadata,
            model=model_info["model"],
            temperature=model_info["temperature"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"アウトライン生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def handle_generate_script(request: ScriptRequest) -> ScriptResponse:
    """台本生成ハンドラー"""
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


async def handle_generate_full_script(request: FullScriptRequest) -> FullScriptResponse:
    """完全台本生成ハンドラー"""
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


async def handle_generate_comedy_titles_batch() -> ComedyTitleBatch:
    """お笑いタイトル量産ハンドラー"""
    try:
        logger.info("お笑いタイトル量産リクエスト")

        from app.core.script_generators.comedy import ComedyScriptGenerator
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


async def handle_save_script_to_file(request: dict) -> Dict[str, Any]:
    """台本保存ハンドラー"""
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


async def handle_get_available_models() -> Dict[str, Any]:
    """利用可能なモデル一覧取得ハンドラー"""
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


async def handle_generate_theme_batch() -> ThemeBatchResponse:
    """テーマ候補生成ハンドラー"""
    try:
        logger.info("テーマ候補生成リクエスト")

        from app.core.script_generators.comedy import ComedyScriptGenerator
        from app.core.script_generators.generate_food_over import create_llm_instance
        from app.config.models import get_default_model_config

        generator = ComedyScriptGenerator()

        model_config = get_default_model_config()
        model = model_config["id"]
        temperature = 0.9

        llm = create_llm_instance(model, temperature, model_config)

        theme_batch = generator.title_generator.generate_theme_batch(llm)

        return ThemeBatchResponse(themes=theme_batch.themes)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"テーマ候補生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def handle_generate_theme_titles(request: ThemeTitleRequest) -> ComedyTitleBatch:
    """テーマベースタイトル生成ハンドラー"""
    try:
        logger.info(f"テーマベースタイトル生成リクエスト: {request.theme}")

        from app.core.script_generators.comedy import ComedyScriptGenerator
        from app.core.script_generators.generate_food_over import create_llm_instance
        from app.config.models import get_default_model_config

        generator = ComedyScriptGenerator()

        model_config = get_default_model_config()
        model = request.model or model_config["id"]
        temperature = request.temperature or 0.9

        llm = create_llm_instance(model, temperature, model_config)

        title_batch = generator.title_generator.generate_title_from_theme(
            request.theme, llm
        )

        return title_batch

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"テーマベースタイトル生成エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

