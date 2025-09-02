import cv2
import os
import logging
from typing import List, Dict, Optional
from moviepy import VideoFileClip, AudioFileClip, concatenate_audioclips

from config import Paths
from src.audio_processor import AudioProcessor
from src.video_processor import VideoProcessor

logger = logging.getLogger(__name__)


class VideoGenerator:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.fps = self.video_processor.fps

    def generate_conversation_video_v2(
        self,
        conversations: List[Dict],
        audio_file_list: List[str],
        output_path: str = None,
        progress_callback=None,
        enable_subtitles: bool = True,
        conversation_mode: str = "duo",
    ) -> Optional[str]:
        """会話動画生成（メイン機能）"""
        if not output_path:
            output_path = os.path.join(
                Paths.get_outputs_dir(), "conversation_video.mp4"
            )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            # リソース読み込み
            character_images = self.video_processor.load_all_character_images()
            backgrounds = self.video_processor.load_backgrounds()

            if not character_images:
                logger.error("No character images loaded")
                return None

            if not backgrounds:
                logger.error("No background images loaded")
                return None

            # 音声結合
            audio_clips = []
            for audio_path in audio_file_list:
                if os.path.exists(audio_path):
                    clip = AudioFileClip(audio_path)
                    audio_clips.append(clip)

            if not audio_clips:
                logger.error("No valid audio clips")
                return None

            combined_audio = concatenate_audioclips(audio_clips)
            total_duration = combined_audio.duration
            total_frames = int(total_duration * self.fps)

            # 字幕作成
            subtitle_lines = []
            if enable_subtitles:
                current_time = 0
                for i, (conv, audio_path) in enumerate(
                    zip(conversations, audio_file_list)
                ):
                    text = conv.get("text", "").strip()
                    if not text:
                        continue

                    if os.path.exists(audio_path):
                        audio_clip = AudioFileClip(audio_path)
                        duration = audio_clip.duration
                        audio_clip.close()

                        speaker = conv.get("speaker", "zundamon")
                        background_name = conv.get("background", "default")

                        # 背景名が有効かチェック
                        if background_name not in backgrounds:
                            background_name = "default"

                        subtitle_lines.append(
                            {
                                "text": text,
                                "start_time": current_time,
                                "end_time": current_time + duration,
                                "duration": duration,
                                "speaker": speaker,
                                "background": background_name,
                            }
                        )
                        current_time += duration

            # 音声解析
            segment_audio_intensities = []
            current_time = 0
            for audio_path in audio_file_list:
                if os.path.exists(audio_path):
                    intensities = self.audio_processor.analyze_audio_for_mouth_sync(
                        audio_path
                    )
                    if intensities:
                        segment_audio_intensities.append(
                            {
                                "start_time": current_time,
                                "intensities": intensities,
                                "duration": len(intensities) / self.fps,
                            }
                        )
                        current_time += len(intensities) / self.fps

            # 瞬きタイミング生成
            blink_timings = []
            # 各キャラクターに対して瞬きタイミングを生成
            for char_name in self.video_processor.characters.keys():
                char_blink_timings = self.video_processor.generate_blink_timings(
                    total_duration, char_name
                )
                blink_timings.extend(char_blink_timings)

            # 動画書き出し
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            temp_video_path = output_path.replace(".mp4", "_temp.mp4")
            out = cv2.VideoWriter(
                temp_video_path, fourcc, self.fps, self.video_processor.resolution
            )

            if not out.isOpened():
                logger.error("Failed to open video writer")
                return None

            # フレーム生成
            for frame_idx in range(total_frames):
                if progress_callback:
                    progress_callback((frame_idx + 1) / total_frames)

                current_time = frame_idx / self.fps
                active_speakers = {}
                current_background = backgrounds["default"]  # デフォルト背景

                # 現在の話者と強度、背景、表情を特定
                current_conversation = None
                for i, (conv, audio_path) in enumerate(
                    zip(conversations, audio_file_list)
                ):
                    if i < len(segment_audio_intensities):
                        segment = segment_audio_intensities[i]
                        segment_start = segment["start_time"]
                        segment_end = segment_start + segment["duration"]

                        if segment_start <= current_time < segment_end:
                            current_conversation = conv
                            local_time = current_time - segment_start
                            local_frame = max(
                                0,
                                min(
                                    int(local_time * self.fps),
                                    len(segment["intensities"]) - 1,
                                ),
                            )

                            speaker = conv.get("speaker", "zundamon")
                            intensity = (
                                segment["intensities"][local_frame]
                                if segment["intensities"]
                                else 0
                            )
                            expression = conv.get("expression", "normal")

                            # 現在のセリフの背景を取得
                            background_name = conv.get("background", "default")
                            if background_name in backgrounds:
                                current_background = backgrounds[background_name]

                            break

                # 表示するキャラクターを決定
                if current_conversation:
                    visible_chars = current_conversation.get(
                        "visible_characters", [speaker, "zundamon"]
                    )
                    # 重複を除去し、話者を含める
                    visible_chars = list(set(visible_chars + [speaker]))

                    for char_name in visible_chars:
                        if char_name in self.video_processor.characters:
                            if char_name == speaker:
                                # 話している人
                                active_speakers[char_name] = {
                                    "intensity": intensity,
                                    "expression": expression,
                                }
                            else:
                                # 表示されているが話していない人
                                active_speakers[char_name] = {
                                    "intensity": 0,
                                    "expression": "normal",
                                }
                else:
                    # デフォルト：ずんだもんのみ表示
                    active_speakers = {
                        "zundamon": {"intensity": 0, "expression": "normal"}
                    }

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
                if subtitle_lines:
                    for subtitle in subtitle_lines:
                        if (
                            subtitle["start_time"]
                            <= current_time
                            <= subtitle["end_time"]
                        ):
                            line_progress = (
                                current_time - subtitle["start_time"]
                            ) / subtitle["duration"]
                            line_progress = min(1.0, max(0.0, line_progress))
                            speaker = subtitle.get("speaker", "zundamon")
                            frame = self.video_processor.draw_subtitle_on_frame(
                                frame, subtitle["text"], line_progress, speaker
                            )
                            break

                out.write(frame)

            out.release()

            # 音声付加
            logger.info("Adding audio to video...")
            video_clip = VideoFileClip(temp_video_path)
            final_clip = video_clip.with_audio(combined_audio)
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            # クリーンアップ
            video_clip.close()
            combined_audio.close()
            final_clip.close()
            for clip in audio_clips:
                clip.close()

            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

            logger.info(f"Conversation video generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return None
