"""フレーム情報構築ユーティリティ"""

import cv2
import logging
import os
from typing import List, Dict, Tuple
from moviepy import AudioFileClip
from app.models.video_models import AudioSegmentInfo, SubtitleData

logger = logging.getLogger(__name__)

CHARACTER_NAME_MAP = {
    "ずんだもん": "zundamon",
    "めたん": "metan",
    "四国めたん": "metan",
    "つむぎ": "tsumugi",
    "春日部つむぎ": "tsumugi",
    "ナレーター": "narrator",
}


class FrameInfoBuilder:
    """フレーム情報構築クラス"""

    def __init__(self, video_processor, fps: int):
        self.video_processor = video_processor
        self.fps = fps

    def get_frame_info(
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
        intensity = 0.0  # 強度値を初期化

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
                    else:
                        intensity = 0

                    speaker = conv.get("speaker", "zundamon")
                    expression = conv.get("expression", "normal")
                    character_expressions = conv.get("character_expressions", {})

                    # 現在のセリフの背景を取得
                    background_name = conv.get("background", "default")
                    if background_name in backgrounds:
                        current_background = backgrounds[background_name]

                    break

        # 表示するキャラクターを決定
        if current_conversation:
            speaker = current_conversation.get("speaker", "zundamon")
            speaker = CHARACTER_NAME_MAP.get(speaker, speaker)
            expression = current_conversation.get("expression", "normal")
            character_expressions = current_conversation.get("character_expressions", {})
            visible_chars_raw = current_conversation.get(
                "visible_characters", [speaker, "zundamon"]
            )
            visible_chars = [
                CHARACTER_NAME_MAP.get(char, char) for char in visible_chars_raw
            ]
            character_expressions = {
                CHARACTER_NAME_MAP.get(k, k): v
                for k, v in character_expressions.items()
            }

            # ナレーターの場合、話者自体は表示しない
            if speaker == "narrator":
                # visible_charactersに指定されたキャラクターのみ表示
                for char_name in visible_chars:
                    if (
                        char_name in self.video_processor.characters
                        and char_name != "narrator"
                    ):
                        # character_expressionsから表情を取得、なければnormal
                        char_expression = character_expressions.get(char_name, "normal")
                        active_speakers[char_name] = {
                            "intensity": 0,  # ナレーション中なので動きなし
                            "expression": char_expression,
                        }
            else:
                if speaker not in visible_chars:
                    visible_chars = visible_chars + [speaker]
                for char_name in visible_chars:
                    if (
                        char_name in self.video_processor.characters
                        and char_name != "narrator"
                    ):
                        # character_expressionsから表情を取得
                        # 優先順位: character_expressions > expression(話者の場合) > normal
                        if char_name in character_expressions:
                            char_expression = character_expressions[char_name]
                        elif char_name == speaker:
                            # 後方互換性: character_expressionsがない場合、話者はexpressionを使用
                            char_expression = expression
                        else:
                            char_expression = "normal"

                        if char_name == speaker:
                            active_speakers[char_name] = {
                                "intensity": intensity,
                                "expression": char_expression,
                            }
                        else:
                            active_speakers[char_name] = {
                                "intensity": 0,
                                "expression": char_expression,
                            }
        else:
            active_speakers = {"zundamon": {"intensity": 0, "expression": "normal"}}

        return active_speakers, current_background

    def add_subtitle_to_frame(
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

    def validate_timing_consistency(
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

