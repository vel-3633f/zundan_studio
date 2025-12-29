import cv2
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple
from app.models.video_models import AudioSegmentInfo, SubtitleData
from .frame_info_builder import FrameInfoBuilder

logger = logging.getLogger(__name__)


class FrameGenerator:
    """フレーム生成クラス"""

    def __init__(self, video_processor, fps: int):
        self.video_processor = video_processor
        self.fps = fps
        self.frame_info_builder = FrameInfoBuilder(video_processor, fps)

    def _generate_single_frame(
        self,
        frame_idx: int,
        conversations: List[Dict],
        audio_file_list: List[str],
        segment_audio_intensities: List[AudioSegmentInfo],
        backgrounds: Dict,
        character_images: Dict,
        blink_timings: List,
        subtitle_lines: List[SubtitleData],
        conversation_mode: str,
        item_images: Dict,
        sections: List,
        section_segment_ranges: List[Dict],
    ) -> Tuple[int, any]:
        """単一フレームを生成する（並列化用）"""
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

        # 現在のセグメントを特定してアイテムを決定
        current_item = None
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

                    # アイテム表示が許可されるセクションかチェック
                    ITEM_ALLOWED_SECTIONS = {"background", "learning"}
                    if new_section_key in ITEM_ALLOWED_SECTIONS:
                        # アイテム画像を取得（セクション情報から）
                        if item_images and sections:
                            for section in sections:
                                if getattr(section, "section_key", None) == new_section_key:
                                    # セクションに対応するアイテム画像を取得
                                    item_name = getattr(section, "item", None)
                                    if item_name and item_name in item_images:
                                        current_item = item_images[item_name]
                                    break
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

        return frame_idx, frame

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

            # 並列化の設定
            num_workers = min(multiprocessing.cpu_count(), 8)
            batch_size = max(30, total_frames // (num_workers * 4))  # 最低30フレーム、最大4バッチ/ワーカー

            # フレームをバッチに分割
            frame_batches = []
            for batch_start in range(0, total_frames, batch_size):
                batch_end = min(batch_start + batch_size, total_frames)
                frame_batches.append((batch_start, batch_end))

            # フレーム生成を並列実行
            frames_dict = {}  # frame_idx -> frame の辞書
            completed_frames = 0

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                # 全フレームのタスクを送信
                future_to_frame = {}
                for frame_idx in range(total_frames):
                    future = executor.submit(
                        self._generate_single_frame,
                        frame_idx,
                        conversations,
                        audio_file_list,
                        segment_audio_intensities,
                        backgrounds,
                        character_images,
                        blink_timings,
                        subtitle_lines,
                        conversation_mode,
                        item_images or {},
                        sections or [],
                        section_segment_ranges,
                    )
                    future_to_frame[future] = frame_idx

                # 完了したフレームを順番に書き込み
                for future in as_completed(future_to_frame):
                    try:
                        frame_idx, frame = future.result()
                        frames_dict[frame_idx] = frame
                        completed_frames += 1

                        # 進捗コールバック
                        if progress_callback:
                            progress_callback(completed_frames / total_frames)
                    except Exception as e:
                        logger.error(f"Frame generation error at frame {frame_idx}: {e}")
                        raise

            # フレームを順番に書き込み
            for frame_idx in range(total_frames):
                if frame_idx in frames_dict:
                    out.write(frames_dict[frame_idx])
                else:
                    logger.error(f"Missing frame {frame_idx}")
                    return False

            out.release()
            return True

        except Exception as e:
            logger.error(f"Frame generation failed: {e}")
            out.release()
            return False
