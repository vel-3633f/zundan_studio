import os
import logging
from typing import List, Dict
from moviepy import AudioFileClip
from src.models.video_models import SubtitleData

logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """字幕生成クラス"""

    def __init__(self):
        pass

    def generate_subtitles(
        self,
        conversations: List[Dict],
        audio_file_list: List[str],
        backgrounds: Dict,
        enable_subtitles: bool = True,
    ) -> List[SubtitleData]:
        """字幕データの生成"""
        subtitle_lines = []

        if not enable_subtitles:
            return subtitle_lines

        current_time = 0
        for i, (conv, audio_path) in enumerate(zip(conversations, audio_file_list)):
            text = conv.get("text", "").strip()
            if not text:
                continue

            if os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                audio_clip.close()

                speaker = conv.get("speaker", "zundamon")
                background_name = conv.get("background", "default")

                # 背景名が有効かチェック
                if background_name not in backgrounds:
                    background_name = "default"

                subtitle_lines.append(
                    SubtitleData(
                        text=text,
                        start_time=current_time,
                        end_time=current_time + duration,
                        duration=duration,
                        speaker=speaker,
                        background=background_name,
                    )
                )
                current_time += duration

        return subtitle_lines

    def find_current_subtitle(
        self, subtitle_lines: List[SubtitleData], current_time: float
    ) -> tuple:
        """現在時刻の字幕を検索"""
        for subtitle in subtitle_lines:
            if subtitle.start_time <= current_time <= subtitle.end_time:
                line_progress = (current_time - subtitle.start_time) / subtitle.duration
                line_progress = min(1.0, max(0.0, line_progress))
                return subtitle, line_progress
        return None, 0
