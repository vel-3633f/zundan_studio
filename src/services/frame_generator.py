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
        item_images: Dict = None,
        sections: List = None,
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
            # 現在表示中のアイテムを追跡
            current_item = None
            current_section_key = None

            # アイテム表示が許可されるセクションキー
            ITEM_ALLOWED_SECTIONS = {"background", "learning"}

            # セクションごとのセグメント範囲を事前計算
            section_segment_ranges = []
            if sections:
                segment_index = 0
                for section in sections:
                    segment_count = len(section.segments)
                    section_segment_ranges.append({
                        "key": getattr(section, "section_key", None),
                        "start": segment_index,
                        "end": segment_index + segment_count
                    })
                    segment_index += segment_count

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

                # 現在のセグメントを特定してアイテムを更新
                for i, conv in enumerate(conversations):
                    if i < len(segment_audio_intensities):
                        segment = segment_audio_intensities[i]
                        segment_start = segment.start_time
                        segment_end = segment_start + segment.duration

                        if segment_start <= current_time < segment_end:
                            # 現在のセグメントが属するセクションを判定
                            new_section_key = None
                            for section_range in section_segment_ranges:
                                if section_range["start"] <= i < section_range["end"]:
                                    new_section_key = section_range["key"]
                                    break

                            # セクションが変わった場合
                            if new_section_key != current_section_key:
                                # アイテム表示が許可されていないセクションに入った場合はクリア
                                if new_section_key not in ITEM_ALLOWED_SECTIONS:
                                    if current_item is not None:
                                        logger.info(
                                            f"Item cleared: section changed to '{new_section_key}' at time={current_time:.3f}s"
                                        )
                                        current_item = None
                                else:
                                    logger.info(
                                        f"Entered item-allowed section '{new_section_key}' at time={current_time:.3f}s"
                                    )
                                current_section_key = new_section_key

                            # アイテム表示が許可されているセクションでのみアイテムを処理
                            if current_section_key in ITEM_ALLOWED_SECTIONS:
                                display_item_id = conv.get("display_item")

                                if display_item_id is not None:
                                    # "none" または空文字列の場合はアイテムを非表示
                                    if display_item_id == "none" or display_item_id == "":
                                        if current_item is not None:
                                            logger.debug(
                                                f"Item cleared at time={current_time:.3f}s"
                                            )
                                            current_item = None
                                    # アイテムIDが指定されている場合
                                    elif item_images and display_item_id in item_images:
                                        current_item = item_images[display_item_id]
                                        logger.debug(
                                            f"Item switched to '{display_item_id}' at time={current_time:.3f}s"
                                        )
                                    # アイテムIDが指定されているが画像が見つからない場合
                                    elif item_images is not None:
                                        logger.warning(
                                            f"Item image not found: '{display_item_id}' at time={current_time:.3f}s (keeping previous item)"
                                        )
                            break

                # フレーム合成（アイテム付き）
                frame = self.video_processor.composite_conversation_frame_with_item(
                    current_background,
                    character_images,
                    active_speakers,
                    conversation_mode,
                    current_time,
                    blink_timings,
                    current_item,
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
                        # 1秒ごとまたは高い強度値のときにログ出力
                        if current_frame_idx % self.fps == 0 or intensity > 0.5:
                            logger.info(
                                f"Frame {current_frame_idx} (time={current_time:.3f}s): "
                                f"segment[{i}], local_time={local_time:.3f}s, "
                                f"progress={frame_progress:.3f}, idx={exact_frame_index:.2f}, "
                                f"intensity={intensity:.3f}"
                            )
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
            expression = current_conversation.get("expression", "normal")
            character_expressions = current_conversation.get("character_expressions", {})
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
                        # character_expressionsから表情を取得、なければnormal
                        char_expression = character_expressions.get(char_name, "normal")
                        active_speakers[char_name] = {
                            "intensity": 0,  # ナレーション中なので動きなし
                            "expression": char_expression,
                        }
            else:
                # 通常のキャラクター会話の場合
                visible_chars = list(set(visible_chars + [speaker]))
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
                            # 話者の強度値を常に記録（重要な情報）
                            current_frame_idx = int(current_time * self.fps)
                            if current_frame_idx % (self.fps * 2) == 0:  # 2秒ごと
                                logger.info(
                                    f"Active speaker: {char_name}, time={current_time:.3f}s, "
                                    f"intensity={intensity:.3f}, expression={char_expression}"
                                )
                        else:
                            active_speakers[char_name] = {
                                "intensity": 0,
                                "expression": char_expression,
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
