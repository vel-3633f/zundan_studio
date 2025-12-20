"""Script generation Celery tasks"""
from celery import Task
from typing import Dict, Any
import logging

from app.tasks.celery_app import celery_app
from app.core.script_generators.generate_food_over_sectioned import (
    generate_outline_only,
    generate_sections_from_approved_outline
)
from app.models.food_over import StoryOutline

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


@celery_app.task(bind=True, base=ScriptGenerationTask, name='app.tasks.generate_sections')
def generate_sections_task(
    self,
    outline_data: Dict[str, Any],
    food_name: str,
    reference_info: str,
    model: str,
    temperature: float,
    model_config: Dict[str, Any]
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
        
        # アウトラインオブジェクトの復元
        outline = StoryOutline(**outline_data)
        
        def progress_callback(message: str, progress: float):
            """進捗コールバック"""
            self.update_state(
                state='PROGRESS',
                meta={'progress': progress, 'message': message}
            )
        
        # セクション生成
        result = generate_sections_from_approved_outline(
            outline=outline,
            food_name=food_name,
            reference_info=reference_info,
            model=model,
            temperature=temperature,
            model_config=model_config,
            progress_callback=progress_callback
        )
        
        if isinstance(result, dict) and "error" in result:
            raise ValueError(result.get("details", "セクション生成に失敗しました"))
        
        logger.info(f"セクション生成タスク完了 (task_id={self.request.id})")
        
        return {
            'status': 'completed',
            'script': result.model_dump(),
            'message': '台本生成が完了しました'
        }
        
    except Exception as e:
        logger.error(f"セクション生成タスクエラー (task_id={self.request.id}): {str(e)}", exc_info=True)
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'message': 'セクション生成に失敗しました'}
        )
        raise


@celery_app.task(bind=True, base=ScriptGenerationTask, name='app.tasks.generate_full_script')
def generate_full_script_task(
    self,
    food_name: str,
    model: str = None,
    temperature: float = None
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
            meta = {'message': message}
            if progress is not None:
                meta['progress'] = progress
            self.update_state(state='PROGRESS', meta=meta)
        
        # アウトライン生成
        self.update_state(
            state='PROGRESS',
            meta={'progress': 0.0, 'message': 'アウトラインを生成中...'}
        )
        
        outline_result = generate_outline_only(
            food_name=food_name,
            model=model,
            temperature=temperature,
            progress_callback=progress_callback
        )
        
        if isinstance(outline_result, dict) and "error" in outline_result:
            raise ValueError(outline_result.get("details", "アウトライン生成に失敗しました"))
        
        # セクション生成
        self.update_state(
            state='PROGRESS',
            meta={'progress': 0.3, 'message': 'セクションを生成中...'}
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
            progress_callback=lambda msg, prog: progress_callback(msg, 0.3 + (prog * 0.7))
        )
        
        if isinstance(script_result, dict) and "error" in script_result:
            raise ValueError(script_result.get("details", "セクション生成に失敗しました"))
        
        logger.info(f"完全台本生成タスク完了 (task_id={self.request.id})")
        
        return {
            'status': 'completed',
            'script': script_result.model_dump(),
            'message': '台本生成が完了しました'
        }
        
    except Exception as e:
        logger.error(f"完全台本生成タスクエラー (task_id={self.request.id}): {str(e)}", exc_info=True)
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'message': '台本生成に失敗しました'}
        )
        raise
