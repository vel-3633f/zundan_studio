import os
import logging
from typing import List, Optional
from moviepy import AudioFileClip, concatenate_audioclips
from src.models.video_models import AudioSegmentInfo

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
        """音声セグメントの解析（実時間ベース）"""
        segment_audio_intensities = []
        current_time = 0.0

        for audio_path in audio_file_list:
            if os.path.exists(audio_path):
                # 実時間ベースの音声解析
                intensities, actual_duration = self.audio_processor.analyze_audio_for_mouth_sync(
                    audio_path
                )
                if intensities and actual_duration > 0:
                    segment_audio_intensities.append(
                        AudioSegmentInfo(
                            start_time=current_time,
                            intensities=intensities,
                            duration=actual_duration,  # 実際の音声時間を使用
                            actual_frame_count=len(intensities)  # 実際のフレーム数
                        )
                    )
                    current_time += actual_duration  # 実時間で累積
                    logger.debug(f"Added segment: {audio_path}, start: {current_time - actual_duration:.3f}s, duration: {actual_duration:.3f}s, frames: {len(intensities)}")
                else:
                    logger.warning(f"Failed to analyze audio segment: {audio_path}")

        total_duration = current_time
        logger.info(f"Total analyzed duration: {total_duration:.3f}s, segments: {len(segment_audio_intensities)}")
        return segment_audio_intensities

    def cleanup_audio_clips(
        self, combined_audio: AudioFileClip, audio_clips: List[AudioFileClip]
    ):
        """音声クリップのクリーンアップ"""
        if combined_audio:
            combined_audio.close()
        for clip in audio_clips:
            clip.close()
