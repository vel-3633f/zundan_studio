import streamlit as st
import os
import logging
import gc
from typing import List, Dict, Optional
from src.core.voice_generator import VoiceGenerator
from src.services.video_generator import VideoGenerator
from src.utils.utils import generate_unique_filename
from config import Paths

logger = logging.getLogger(__name__)


def generate_conversation_video(
    conversations: List[Dict],
    progress_bar,
    status_text,
    enable_subtitles: bool = True,
    conversation_mode: str = "duo",
    sections=None,
) -> Optional[str]:
    """Generate conversation video"""
    voice_gen = None
    video_gen = None

    try:
        voice_gen = VoiceGenerator()
        video_gen = VideoGenerator()
        base_dir = os.path.dirname(os.path.abspath(__file__))

        progress_bar.progress(0.1)
        status_text.text("会話音声を生成中...")

        audio_files = voice_gen.generate_conversation_voices(
            conversations=conversations,
            speed=None,
            pitch=None,
            intonation=None,
            output_dir=Paths.get_temp_dir(),
        )

        if not audio_files:
            st.error("音声生成に失敗しました")
            return None

        progress_bar.progress(0.5)
        status_text.text("会話動画を生成中...")

        video_path = os.path.join(
            Paths.get_outputs_dir(),
            generate_unique_filename("conversation_video", "mp4"),
        )

        def progress_callback(progress):
            progress_bar.progress(0.5 + (progress * 0.4))
            status_text.text(f"会話動画を生成中... ({int(progress * 100)}%)")

        result = video_gen.generate_conversation_video(
            conversations=conversations,
            audio_file_list=audio_files,
            output_path=video_path,
            progress_callback=progress_callback,
            enable_subtitles=enable_subtitles,
            conversation_mode=conversation_mode,
            sections=sections,
        )

        if result:
            progress_bar.progress(1.0)
            status_text.text("生成完了！")
        else:
            st.error("動画生成に失敗しました")

        return result

    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        st.error(f"エラーが発生しました: {str(e)}")
        return None

    finally:
        try:
            if video_gen is not None:
                logger.info("Starting cleanup to prevent memory leaks...")
                video_gen.cleanup()

            del voice_gen
            del video_gen

            collected = gc.collect()
            logger.info(f"Final cleanup: collected {collected} objects")

        except Exception as cleanup_error:
            logger.warning(f"Cleanup warning: {cleanup_error}")
