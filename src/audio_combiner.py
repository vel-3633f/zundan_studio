import os
import logging
from typing import List, Optional
from moviepy import AudioFileClip, concatenate_audioclips
from src.video_models import AudioSegmentInfo

logger = logging.getLogger(__name__)


class AudioCombiner:
    """音声結合・解析クラス"""

    def __init__(self, audio_processor, fps: int):
        self.audio_processor = audio_processor
        self.fps = fps

    def combine_audio_files(
        self, audio_file_list: List[str]
    ) -> Optional[AudioFileClip]:
        """音声ファイルの結合"""
        audio_clips = []
        for audio_path in audio_file_list:
            if os.path.exists(audio_path):
                clip = AudioFileClip(audio_path)
                audio_clips.append(clip)

        if not audio_clips:
            logger.error("No valid audio clips")
            return None, None

        combined_audio = concatenate_audioclips(audio_clips)
        return combined_audio, audio_clips

    def analyze_audio_segments(
        self, audio_file_list: List[str]
    ) -> List[AudioSegmentInfo]:
        """音声セグメントの解析"""
        segment_audio_intensities = []
        current_time = 0

        for audio_path in audio_file_list:
            if os.path.exists(audio_path):
                intensities = self.audio_processor.analyze_audio_for_mouth_sync(
                    audio_path
                )
                if intensities:
                    segment_audio_intensities.append(
                        AudioSegmentInfo(
                            start_time=current_time,
                            intensities=intensities,
                            duration=len(intensities) / self.fps,
                        )
                    )
                    current_time += len(intensities) / self.fps

        return segment_audio_intensities

    def cleanup_audio_clips(
        self, combined_audio: AudioFileClip, audio_clips: List[AudioFileClip]
    ):
        """音声クリップのクリーンアップ"""
        if combined_audio:
            combined_audio.close()
        for clip in audio_clips:
            clip.close()
