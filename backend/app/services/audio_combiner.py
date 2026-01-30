import os
import logging
from typing import List, Optional, Tuple, Dict
from moviepy import AudioFileClip, concatenate_audioclips
from app.models.video_models import AudioSegmentInfo

logger = logging.getLogger(__name__)


class AudioCombiner:
    """音声結合・解析クラス"""

    def __init__(self, audio_processor, fps: int):
        self.audio_processor = audio_processor
        self.fps = fps

    def combine_audio_files(
        self, audio_file_list: List[str]
    ) -> Tuple[Optional[AudioFileClip], List[AudioFileClip], Dict[str, float]]:
        """音声ファイルの結合（duration情報も返す）

        Returns:
            tuple: (combined_audio, audio_clips, audio_durations)
                   audio_durations は {audio_path: duration} の辞書
        """
        audio_clips = []
        audio_durations = {}

        for audio_path in audio_file_list:
            if os.path.exists(audio_path):
                clip = AudioFileClip(audio_path)
                clip = clip.with_volume_scaled(2.0)
                audio_clips.append(clip)
                audio_durations[audio_path] = clip.duration

        if not audio_clips:
            logger.error("No valid audio clips")
            return None, None, {}

        combined_audio = concatenate_audioclips(audio_clips)
        return combined_audio, audio_clips, audio_durations

    def analyze_audio_segments(
        self, audio_file_list: List[str]
    ) -> List[AudioSegmentInfo]:
        """音声セグメントの解析（実時間ベース）"""
        segment_audio_intensities = []
        current_time = 0.0

        for audio_path in audio_file_list:
            if os.path.exists(audio_path):
                intensities, actual_duration = (
                    self.audio_processor.analyze_audio_for_mouth_sync(audio_path)
                )
                if intensities and actual_duration > 0:
                    max_intensity = max(intensities)
                    avg_intensity = sum(intensities) / len(intensities)
                    non_zero_count = sum(1 for i in intensities if i > 0.1)

                    segment_audio_intensities.append(
                        AudioSegmentInfo(
                            start_time=current_time,
                            intensities=intensities,
                            duration=actual_duration,
                            actual_frame_count=len(intensities),
                        )
                    )
                    current_time += actual_duration
                else:
                    logger.warning(f"Failed to analyze audio segment: {audio_path}")

        total_duration = current_time
        return segment_audio_intensities

    def cleanup_audio_clips(
        self, combined_audio: AudioFileClip, audio_clips: List[AudioFileClip]
    ):
        """音声クリップのクリーンアップ"""
        if combined_audio:
            combined_audio.close()
        for clip in audio_clips:
            clip.close()
