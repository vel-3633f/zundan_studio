import cv2
import logging
import os
from typing import List, Dict, Optional, Tuple
from moviepy import AudioFileClip
from src.models.video_models import AudioSegmentInfo, SubtitleData

logger = logging.getLogger(__name__)


class FrameGenerator:
    """フレーム生成クラス"""

    def __init__(self, video_processor, fps: int):
        self.video_processor = video_processor
        self.fps = fps

    def generate_video_frames(
        self,
        total_frames: int,
        conversations: List[Dict],
        audio_file_list: List[str],
        segment_audio_intensities: List[AudioSegmentInfo],
        backgrounds: Dict,
        character_images: Dict,
        blink_timings: List,
        subtitle_lines: List[SubtitleData],
        conversation_mode: str,
        temp_video_path: str,
        progress_callback=None,
    ) -> bool:
        """動画フレームの生成"""
        # タイミング整合性の検証
        if not self._validate_timing_consistency(
            segment_audio_intensities, audio_file_list
        ):
            logger.warning("Timing inconsistency detected, but continuing...")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            temp_video_path, fourcc, self.fps, self.video_processor.resolution
        )

        if not out.isOpened():
            logger.error("Failed to open video writer")
            return False

        try:
            for frame_idx in range(total_frames):
                if progress_callback:
                    progress_callback((frame_idx + 1) / total_frames)

                current_time = frame_idx / self.fps

                # 現在のフレーム情報を取得
                active_speakers, current_background = (
                    self._get_frame_info(
                        current_time,
                        conversations,
                        audio_file_list,
                        segment_audio_intensities,
                        backgrounds,
                    )
                )

                # フレーム合成
                frame = self.video_processor.composite_conversation_frame(
                    current_background,
                    character_images,
                    active_speakers,
                    conversation_mode,
                    current_time,
                    blink_timings,
                )

                # 字幕追加
                frame = self._add_subtitle_to_frame(frame, subtitle_lines, current_time)

                out.write(frame)

            out.release()
            return True

        except Exception as e:
            logger.error(f"Frame generation failed: {e}")
            out.release()
            return False

    def _get_frame_info(
        self,
        current_time: float,
        conversations: List[Dict],
        audio_file_list: List[str],
        segment_audio_intensities: List[AudioSegmentInfo],
        backgrounds: Dict,
    ) -> Tuple[Dict, any]:
        """現在のフレーム情報を取得"""
        active_speakers = {}
        current_background = backgrounds["default"]
        current_conversation = None

        # 現在の話者と強度、背景、表情を特定
        for i, (conv, audio_path) in enumerate(zip(conversations, audio_file_list)):
            if i < len(segment_audio_intensities):
                segment = segment_audio_intensities[i]
                segment_start = segment.start_time
                segment_end = segment_start + segment.duration

                if segment_start <= current_time < segment_end:
                    current_conversation = conv
                    local_time = current_time - segment_start

                    # より精密なフレーム番号計算（線形補間使用）
                    if segment.intensities and segment.duration > 0:
                        # 相対的な進行度を計算
                        frame_progress = local_time / segment.duration
                        exact_frame_index = frame_progress * (
                            len(segment.intensities) - 1
                        )

                        # 線形補間でintensityを計算
                        lower_idx = max(0, int(exact_frame_index))
                        upper_idx = min(lower_idx + 1, len(segment.intensities) - 1)

                        if lower_idx == upper_idx:
                            intensity = segment.intensities[lower_idx]
                        else:
                            interpolation_factor = exact_frame_index - lower_idx
                            intensity = (
                                segment.intensities[lower_idx]
                                * (1 - interpolation_factor)
                                + segment.intensities[upper_idx] * interpolation_factor
                            )

                        current_frame_idx = int(current_time * self.fps)
                        logger.debug(
                            f"Frame {current_frame_idx}: local_time={local_time:.3f}, progress={frame_progress:.3f}, exact_idx={exact_frame_index:.2f}, intensity={intensity:.3f}"
                        )
                    else:
                        intensity = 0

                    speaker = conv.get("speaker", "zundamon")
                    expression = conv.get("expression", "normal")

                    # 現在のセリフの背景を取得
                    background_name = conv.get("background", "default")
                    if background_name in backgrounds:
                        current_background = backgrounds[background_name]

                    break

        # 表示するキャラクターを決定
        if current_conversation:
            speaker = current_conversation.get("speaker", "zundamon")
            visible_chars = current_conversation.get(
                "visible_characters", [speaker, "zundamon"]
            )

            # ナレーターの場合、話者自体は表示しない
            if speaker == "narrator":
                # visible_charactersに指定されたキャラクターのみ表示
                for char_name in visible_chars:
                    if (
                        char_name in self.video_processor.characters
                        and char_name != "narrator"
                    ):
                        active_speakers[char_name] = {
                            "intensity": 0,  # ナレーション中なので動きなし
                            "expression": "normal",
                        }
            else:
                # 通常のキャラクター会話の場合
                visible_chars = list(set(visible_chars + [speaker]))
                for char_name in visible_chars:
                    if (
                        char_name in self.video_processor.characters
                        and char_name != "narrator"
                    ):
                        if char_name == speaker:
                            active_speakers[char_name] = {
                                "intensity": intensity,
                                "expression": expression,
                            }
                        else:
                            active_speakers[char_name] = {
                                "intensity": 0,
                                "expression": "normal",
                            }
        else:
            active_speakers = {"zundamon": {"intensity": 0, "expression": "normal"}}

        return active_speakers, current_background

    def _add_subtitle_to_frame(
        self, frame, subtitle_lines: List[SubtitleData], current_time: float
    ):
        """フレームに字幕を追加"""
        if not subtitle_lines:
            return frame

        for subtitle in subtitle_lines:
            if subtitle.start_time <= current_time <= subtitle.end_time:
                line_progress = (current_time - subtitle.start_time) / subtitle.duration
                line_progress = min(1.0, max(0.0, line_progress))
                frame = self.video_processor.draw_subtitle_on_frame(
                    frame, subtitle.text, line_progress, subtitle.speaker
                )
                break

        return frame

    def _validate_timing_consistency(
        self, segments: List[AudioSegmentInfo], audio_files: List[str]
    ) -> bool:
        """タイミングの整合性をチェック"""
        try:
            # セグメント時間の合計を計算
            total_segment_duration = sum(segment.duration for segment in segments)

            # 実際の音声ファイル時間の合計を計算
            total_actual_duration = 0.0
            for audio_path in audio_files:
                if os.path.exists(audio_path):
                    audio_clip = AudioFileClip(audio_path)
                    total_actual_duration += audio_clip.duration
                    audio_clip.close()

            # 許容誤差（1秒）
            tolerance = 1.0
            time_diff = abs(total_segment_duration - total_actual_duration)

            logger.info(
                f"Timing validation: segment_total={total_segment_duration:.3f}s, actual_total={total_actual_duration:.3f}s, diff={time_diff:.3f}s"
            )

            if time_diff > tolerance:
                logger.warning(
                    f"Large timing difference detected: {time_diff:.3f}s > {tolerance}s"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"Timing validation failed: {e}")
            return False
