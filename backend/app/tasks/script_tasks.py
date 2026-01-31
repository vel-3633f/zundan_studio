"""Script generation Celery tasks"""

from celery import Task
from typing import Dict, Any, Optional
import logging

from app.tasks.celery_app import celery_app
from app.core.script_generators.generate_food_over_sectioned import (
    generate_outline_only,
    generate_sections_from_approved_outline,
)
from app.models.food_over import StoryOutline
from app.models.script_models import ScriptMode
from app.core.script_generators.unified_script_generator import UnifiedScriptGenerator

logger = logging.getLogger(__name__)


class ScriptGenerationTask(Task):
    """台本生成タスクの基底クラス"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """タスク失敗時の処理"""
        logger.error(f"台本生成タスク失敗 (task_id={task_id}): {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """タスク成功時の処理"""
        logger.info(f"台本生成タスク成功 (task_id={task_id})")
        super().on_success(retval, task_id, args, kwargs)


@celery_app.task(
    bind=True, base=ScriptGenerationTask, name="app.tasks.generate_sections"
)
def generate_sections_task(
    self,
    outline_data: Dict[str, Any],
    food_name: str,
    reference_info: str,
    model: str,
    temperature: float,
    model_config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    セクション生成タスク

    Args:
        outline_data: アウトラインデータ
        food_name: 食べ物名
        reference_info: 参照情報
        model: 使用するモデルID
        temperature: 生成温度
        model_config: モデル設定

    Returns:
        生成された台本
    """
    try:
        logger.info(f"セクション生成タスク開始 (task_id={self.request.id})")

        outline = StoryOutline(**outline_data)

        def progress_callback(message: str, progress: float):
            """進捗コールバック"""
            self.update_state(
                state="PROGRESS", meta={"progress": progress, "message": message}
            )

        result = generate_sections_from_approved_outline(
            outline=outline,
            food_name=food_name,
            reference_info=reference_info,
            model=model,
            temperature=temperature,
            model_config=model_config,
            progress_callback=progress_callback,
        )

        if isinstance(result, dict) and "error" in result:
            raise ValueError(result.get("details", "セクション生成に失敗しました"))

        logger.info(f"セクション生成タスク完了 (task_id={self.request.id})")

        return {
            "status": "completed",
            "script": result.model_dump(),
            "message": "台本生成が完了しました",
        }

    except Exception as e:
        logger.error(
            f"セクション生成タスクエラー (task_id={self.request.id}): {str(e)}",
            exc_info=True,
        )
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "message": "セクション生成に失敗しました"},
        )
        raise


@celery_app.task(
    bind=True, base=ScriptGenerationTask, name="app.tasks.generate_full_script"
)
def generate_full_script_task(
    self, food_name: str, model: str = None, temperature: float = None
) -> Dict[str, Any]:
    """
    完全な台本生成タスク（アウトライン→セクション）

    Args:
        food_name: 食べ物名
        model: 使用するモデルID
        temperature: 生成温度

    Returns:
        生成された台本
    """
    try:
        logger.info(f"完全台本生成タスク開始 (task_id={self.request.id})")

        def progress_callback(message: str, progress: float = None):
            """進捗コールバック"""
            meta = {"message": message}
            if progress is not None:
                meta["progress"] = progress
            self.update_state(state="PROGRESS", meta=meta)

        self.update_state(
            state="PROGRESS",
            meta={"progress": 0.0, "message": "アウトラインを生成中..."},
        )

        outline_result = generate_outline_only(
            food_name=food_name,
            model=model,
            temperature=temperature,
            progress_callback=progress_callback,
        )

        if isinstance(outline_result, dict) and "error" in outline_result:
            raise ValueError(
                outline_result.get("details", "アウトライン生成に失敗しました")
            )

        self.update_state(
            state="PROGRESS", meta={"progress": 0.3, "message": "セクションを生成中..."}
        )

        outline = outline_result["outline"]
        reference_info = outline_result["reference_info"]
        model = outline_result["model"]
        temperature = outline_result["temperature"]
        model_config = outline_result["model_config"]

        script_result = generate_sections_from_approved_outline(
            outline=outline,
            food_name=food_name,
            reference_info=reference_info,
            model=model,
            temperature=temperature,
            model_config=model_config,
            progress_callback=lambda msg, prog: progress_callback(
                msg, 0.3 + (prog * 0.7)
            ),
        )

        if isinstance(script_result, dict) and "error" in script_result:
            raise ValueError(
                script_result.get("details", "セクション生成に失敗しました")
            )

        logger.info(f"完全台本生成タスク完了 (task_id={self.request.id})")

        return {
            "status": "completed",
            "script": script_result.model_dump(),
            "message": "台本生成が完了しました",
        }

    except Exception as e:
        logger.error(
            f"完全台本生成タスクエラー (task_id={self.request.id}): {str(e)}",
            exc_info=True,
        )
        self.update_state(
            state="FAILURE", meta={"error": str(e), "message": "台本生成に失敗しました"}
        )
        raise


@celery_app.task(
    bind=True, base=ScriptGenerationTask, name="app.tasks.generate_unified_full_script"
)
def generate_unified_full_script_async(
    self,
    mode: str,
    input_text: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> Dict[str, Any]:
    """
    統合台本生成タスク（Comedy/ThoughtExperiment対応）
    
    Args:
        mode: 生成モード（comedy or thought_experiment）
        input_text: テーマ
        model: 使用するモデルID
        temperature: 生成温度
    
    Returns:
        生成された台本、タイトル、アウトライン、YouTubeメタデータ
    """
    try:
        logger.info(f"統合台本生成タスク開始 (task_id={self.request.id}, mode={mode})")
        
        def progress_callback(message: str, progress: float = None):
            """進捗コールバック"""
            meta = {"message": message}
            if progress is not None:
                meta["progress"] = progress
            self.update_state(state="PROGRESS", meta=meta)
        
        # 生成モードの設定
        script_mode = ScriptMode(mode)
        generator = UnifiedScriptGenerator(script_mode)
        
        # タイトル生成
        self.update_state(
            state="PROGRESS",
            meta={"progress": 0.0, "message": "タイトルを生成中..."}
        )
        title, reference_info, model_info = generator.generate_title(
            input_text=input_text,
            model=model,
            temperature=temperature,
            progress_callback=progress_callback,
        )
        
        # アウトライン生成
        self.update_state(
            state="PROGRESS",
            meta={"progress": 0.2, "message": "アウトラインを生成中..."}
        )
        outline, youtube_metadata, _ = generator.generate_outline(
            title_data=title,
            reference_info=reference_info,
            model=model_info["model"],
            temperature=model_info["temperature"],
            progress_callback=progress_callback,
        )
        
        # 台本生成（ここで詳細な進捗が送信される）
        self.update_state(
            state="PROGRESS",
            meta={"progress": 0.4, "message": "台本を生成中..."}
        )
        
        def script_progress_callback(message: str, progress: float):
            """台本生成の進捗を40%〜90%にマッピング"""
            mapped_progress = 0.4 + (progress * 0.5)
            self.update_state(
                state="PROGRESS",
                meta={"progress": mapped_progress, "message": message}
            )
        
        script, _ = generator.generate_script(
            outline_data=outline,
            reference_info=reference_info,
            model=model_info["model"],
            temperature=model_info["temperature"],
            progress_callback=script_progress_callback,
        )
        
        self.update_state(
            state="PROGRESS",
            meta={"progress": 0.95, "message": "完了処理中..."}
        )
        
        logger.info(f"統合台本生成タスク完了 (task_id={self.request.id})")
        
        return {
            "status": "completed",
            "script": script.model_dump() if hasattr(script, 'model_dump') else script.dict(),
            "title": title.model_dump() if hasattr(title, 'model_dump') else title.dict(),
            "outline": outline.model_dump() if hasattr(outline, 'model_dump') else outline.dict(),
            "youtube_metadata": (
                youtube_metadata.model_dump() if hasattr(youtube_metadata, 'model_dump') 
                else youtube_metadata.dict()
            ) if youtube_metadata else None,
            "message": "台本生成が完了しました",
        }
        
    except Exception as e:
        logger.error(
            f"統合台本生成タスクエラー (task_id={self.request.id}): {str(e)}",
            exc_info=True,
        )
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "message": "台本生成に失敗しました"}
        )
        raise


@celery_app.task(
    bind=True, base=ScriptGenerationTask, name="app.tasks.generate_unified_script_only"
)
def generate_unified_script_only_async(
    self,
    mode: str,
    outline_data: Dict[str, Any],
    reference_info: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> Dict[str, Any]:
    """
    台本のみ生成タスク（Comedy/ThoughtExperiment対応）
    
    Args:
        mode: 生成モード（comedy or thought_experiment）
        outline_data: アウトラインデータ
        reference_info: 参照情報
        model: 使用するモデルID
        temperature: 生成温度
    
    Returns:
        生成された台本
    """
    try:
        logger.info(f"台本生成タスク開始 (task_id={self.request.id}, mode={mode})")
        
        def progress_callback(message: str, progress: float):
            """進捗コールバック"""
            self.update_state(
                state="PROGRESS",
                meta={"progress": progress, "message": message}
            )
        
        # 生成モードの設定
        script_mode = ScriptMode(mode)
        generator = UnifiedScriptGenerator(script_mode)
        
        # アウトラインの復元
        if script_mode == ScriptMode.COMEDY:
            from app.models.script_models import ComedyOutline
            outline = ComedyOutline(**outline_data)
        else:  # THOUGHT_EXPERIMENT
            from app.models.script_models import ThoughtExperimentOutline
            outline = ThoughtExperimentOutline(**outline_data)
        
        # 台本生成
        self.update_state(
            state="PROGRESS",
            meta={"progress": 0.0, "message": "台本を生成中..."}
        )
        
        script, _ = generator.generate_script(
            outline_data=outline,
            reference_info=reference_info,
            model=model,
            temperature=temperature,
            progress_callback=progress_callback,
        )
        
        logger.info(f"台本生成タスク完了 (task_id={self.request.id})")
        
        return {
            "status": "completed",
            "script": script.model_dump() if hasattr(script, 'model_dump') else script.dict(),
            "message": "台本生成が完了しました",
        }
        
    except Exception as e:
        logger.error(
            f"台本生成タスクエラー (task_id={self.request.id}): {str(e)}",
            exc_info=True,
        )
        self.update_state(
            state="FAILURE",
            meta={"error": str(e), "message": "台本生成に失敗しました"}
        )
        raise
