import cv2
import logging
from typing import List, Dict, Optional, Tuple
from src.models.video_models import AudioSegmentInfo, SubtitleData, ActiveSpeakerInfo

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
                active_speakers, current_background, character_items = self._get_frame_info(
                    current_time,
                    conversations,
                    audio_file_list,
                    segment_audio_intensities,
                    backgrounds,
                )

                # フレーム合成
                frame = self.video_processor.composite_conversation_frame(
                    current_background,
                    character_images,
                    active_speakers,
                    conversation_mode,
                    current_time,
                    blink_timings,
                    character_items,
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
    ) -> Tuple[Dict, any, Dict[str, str]]:
        """現在のフレーム情報を取得"""
        active_speakers = {}
        current_background = backgrounds["default"]
        current_conversation = None
        character_items = {}

        # 現在の話者と強度、背景、表情を特定
        for i, (conv, audio_path) in enumerate(zip(conversations, audio_file_list)):
            if i < len(segment_audio_intensities):
                segment = segment_audio_intensities[i]
                segment_start = segment.start_time
                segment_end = segment_start + segment.duration

                if segment_start <= current_time < segment_end:
                    current_conversation = conv
                    local_time = current_time - segment_start
                    local_frame = max(
                        0,
                        min(
                            int(local_time * self.fps),
                            len(segment.intensities) - 1,
                        ),
                    )

                    speaker = conv.get("speaker", "zundamon")
                    intensity = (
                        segment.intensities[local_frame] if segment.intensities else 0
                    )
                    expression = conv.get("expression", "normal")

                    # 現在のセリフの背景を取得
                    background_name = conv.get("background", "default")
                    if background_name in backgrounds:
                        current_background = backgrounds[background_name]

                    # 現在のセリフのキャラクター別アイテム情報を取得
                    char_items = conv.get("character_items", {})
                    if char_items:
                        character_items.update(char_items)
                    
                    # 後方互換性のため、古い形式のitemも処理
                    item_name = conv.get("item", "none")
                    if item_name and item_name != "none":
                        character_items[speaker] = item_name

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
                    if char_name in self.video_processor.characters and char_name != "narrator":
                        active_speakers[char_name] = {
                            "intensity": 0,  # ナレーション中なので動きなし
                            "expression": "normal",
                        }
            else:
                # 通常のキャラクター会話の場合
                visible_chars = list(set(visible_chars + [speaker]))
                for char_name in visible_chars:
                    if char_name in self.video_processor.characters and char_name != "narrator":
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

        return active_speakers, current_background, character_items

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
