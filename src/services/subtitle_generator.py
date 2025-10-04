import os
import logging
from typing import List, Dict, Optional
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
        audio_durations: Optional[Dict[str, float]] = None,
    ) -> List[SubtitleData]:
        """字幕データの生成（音声duration情報を再利用）

        Args:
            conversations: 会話データリスト
            audio_file_list: 音声ファイルパスリスト
            backgrounds: 背景画像辞書
            enable_subtitles: 字幕有効化フラグ
            audio_durations: 音声ファイルのduration辞書（パス→duration）
                            Noneの場合は従来通りAudioFileClipで読み込み

        Returns:
            字幕データリスト
        """
        subtitle_lines = []

        if not enable_subtitles:
            return subtitle_lines

        current_time = 0
        for i, (conv, audio_path) in enumerate(zip(conversations, audio_file_list)):
            text = conv.get("text", "").strip()
            if not text:
                continue

            # duration取得（キャッシュがあればそれを使用）
            if audio_durations and audio_path in audio_durations:
                duration = audio_durations[audio_path]
                logger.debug(f"Using cached duration for {audio_path}: {duration:.3f}s")
            elif os.path.exists(audio_path):
                # フォールバック：AudioFileClipで読み込み
                from moviepy import AudioFileClip
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                audio_clip.close()
                logger.debug(f"Loaded duration for {audio_path}: {duration:.3f}s")
            else:
                logger.warning(f"Audio file not found: {audio_path}")
                continue

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

