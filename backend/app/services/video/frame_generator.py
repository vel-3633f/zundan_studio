import cv2
import logging
from typing import List, Dict, Optional
from app.models.video_models import AudioSegmentInfo, SubtitleData
from .frame_info_builder import FrameInfoBuilder

logger = logging.getLogger(__name__)


class FrameGenerator:
    """フレーム生成クラス"""

    def __init__(self, video_processor, fps: int):
        self.video_processor = video_processor
        self.fps = fps
        self.frame_info_builder = FrameInfoBuilder(video_processor, fps)

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
        if not self.frame_info_builder.validate_timing_consistency(
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
                    self.frame_info_builder.get_frame_info(
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
                frame = self.frame_info_builder.add_subtitle_to_frame(frame, subtitle_lines, current_time)

                out.write(frame)

            out.release()
            return True

        except Exception as e:
            logger.error(f"Frame generation failed: {e}")
            out.release()
            return False
