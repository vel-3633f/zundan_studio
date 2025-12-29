"""Video generation Celery tasks"""

from celery import Task
from typing import Dict, Any, List, Optional
import logging
import os

from app.tasks.celery_app import celery_app
from app.services.video.video_generator import VideoGenerator
from app.core.asset_generators.voice_generator import VoiceGenerator
from app.models.scripts.common import VideoSection
from app.utils_legacy.files import FileManager

logger = logging.getLogger(__name__)


class VideoGenerationTask(Task):
    """動画生成タスクの基底クラス"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """タスク失敗時の処理"""
        logger.error(f"動画生成タスク失敗 (task_id={task_id}): {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """タスク成功時の処理"""
        logger.info(f"動画生成タスク成功 (task_id={task_id})")
        super().on_success(retval, task_id, args, kwargs)


@celery_app.task(bind=True, base=VideoGenerationTask, name="app.tasks.generate_video")
def generate_video_task(
    self,
    conversations: List[Dict[str, Any]],
    enable_subtitles: bool = True,
    conversation_mode: str = "duo",
    sections: Optional[List[Dict[str, Any]]] = None,
    speed: Optional[float] = None,
    pitch: Optional[float] = None,
    intonation: Optional[float] = None,
) -> Dict[str, Any]:
    """
    動画生成タスク

    Args:
        conversations: 会話リスト
        enable_subtitles: 字幕を有効にするか
        conversation_mode: 会話モード
        sections: セクション情報
        speed: 話速
        pitch: 音高
        intonation: 抑揚

    Returns:
        生成結果
    """
    try:
        logger.info(f"動画生成タスク開始 (task_id={self.request.id})")

        # tempフォルダをクリーンアップ
        try:
            deleted_count = FileManager.cleanup_temp_files()
            logger.info(
                f"Tempフォルダをクリーンアップしました: {deleted_count}ファイルを削除"
            )
        except Exception as cleanup_error:
            logger.warning(
                f"Tempフォルダのクリーンアップに失敗しました: {cleanup_error}"
            )

        # 進捗更新: 音声生成開始
        self.update_state(
            state="PROGRESS", meta={"progress": 0.1, "message": "音声を生成中..."}
        )

        # 音声生成
        voice_generator = VoiceGenerator()
        audio_file_list = None
        try:
            audio_file_list = voice_generator.generate_conversation_voices(
                conversations=conversations,
                speed=speed,
                pitch=pitch,
                intonation=intonation,
            )

            if not audio_file_list:
                raise ValueError("音声生成に失敗しました")
        except Exception as e:
            # 音声生成失敗時は既に生成されたファイルがあれば削除
            if audio_file_list:
                try:
                    FileManager.cleanup_audio_files(audio_file_list)
                except Exception:
                    pass
            raise

        # 進捗更新: 動画生成開始
        self.update_state(
            state="PROGRESS", meta={"progress": 0.4, "message": "動画を生成中..."}
        )

        # セクション情報の変換
        video_sections = None
        if sections:
            from app.models.scripts.common import VideoSection

            video_sections = [VideoSection(**section) for section in sections]

        # 動画生成
        video_generator = VideoGenerator()

        def progress_callback(progress: float):
            """進捗コールバック"""
            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": 0.4 + (progress * 0.5),  # 40%から90%まで
                    "message": f"動画を生成中... ({int(progress * 100)}%)",
                },
            )

        output_path = video_generator.generate_conversation_video(
            conversations=conversations,
            audio_file_list=audio_file_list,
            enable_subtitles=enable_subtitles,
            conversation_mode=conversation_mode,
            sections=video_sections,
            progress_callback=progress_callback,
        )

        if not output_path or not os.path.exists(output_path):
            raise ValueError("動画生成に失敗しました")

        # 進捗更新: 完了
        self.update_state(
            state="PROGRESS", meta={"progress": 1.0, "message": "動画生成完了！"}
        )

        # クリーンアップ
        video_generator.cleanup()

        logger.info(f"動画生成タスク完了 (task_id={self.request.id}): {output_path}")

        return {
            "status": "completed",
            "video_path": output_path,
            "message": "動画生成が完了しました",
        }

    except Exception as e:
        logger.error(
            f"動画生成タスクエラー (task_id={self.request.id}): {str(e)}", exc_info=True
        )
        # エラー時も音声ファイルをクリーンアップ
        if "audio_file_list" in locals() and audio_file_list:
            try:
                FileManager.cleanup_audio_files(audio_file_list)
            except Exception as cleanup_error:
                logger.warning(
                    f"Failed to cleanup audio files on task error: {cleanup_error}"
                )
        # Celeryの例外情報を正しく設定
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "動画生成に失敗しました",
            },
        )
        # 元の例外をそのまま再発生させる
        raise


@celery_app.task(bind=True, name="app.tasks.generate_voice")
def generate_voice_task(
    self,
    text: str,
    speaker: str = "zundamon",
    speed: float = 1.0,
    pitch: float = 0.0,
    intonation: float = 1.0,
) -> Dict[str, Any]:
    """
    音声生成タスク

    Args:
        text: 読み上げテキスト
        speaker: 話者名
        speed: 話速
        pitch: 音高
        intonation: 抑揚

    Returns:
        生成結果
    """
    try:
        logger.info(f"音声生成タスク開始 (task_id={self.request.id})")

        voice_generator = VoiceGenerator()
        audio_path = voice_generator.generate_voice(
            text=text, speaker=speaker, speed=speed, pitch=pitch, intonation=intonation
        )

        if not audio_path or not os.path.exists(audio_path):
            raise ValueError("音声生成に失敗しました")

        logger.info(f"音声生成タスク完了 (task_id={self.request.id}): {audio_path}")

        return {
            "status": "completed",
            "audio_path": audio_path,
            "message": "音声生成が完了しました",
        }

    except Exception as e:
        logger.error(
            f"音声生成タスクエラー (task_id={self.request.id}): {str(e)}", exc_info=True
        )
        raise
