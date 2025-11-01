import os
import logging
import gc
from typing import List, Dict, Optional
from moviepy import VideoFileClip

from config import Paths
from src.core.audio_processor import AudioProcessor
from src.core.video_processor import VideoProcessor
from src.services.resource_manager import ResourceManager
from src.services.audio_combiner import AudioCombiner
from src.services.subtitle_generator import SubtitleGenerator
from src.services.frame_generator import FrameGenerator
from src.services.bgm_mixer import BGMMixer
from src.models.food_over import VideoSection

logger = logging.getLogger(__name__)


class VideoGenerator:
    def __init__(self):
        # 口パクデバッグ用: ログレベルを一時的にINFOに設定
        for logger_name in ['src.services.audio_combiner', 'src.services.frame_generator',
                           'src.core.video_processor', 'src.core.audio_processor',
                           'src.services.bgm_mixer', 'config.bgm_library']:
            logging.getLogger(logger_name).setLevel(logging.INFO)

        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.fps = self.video_processor.fps

        # 各処理クラスの初期化
        self.resource_manager = ResourceManager(self.video_processor)
        self.audio_combiner = AudioCombiner(self.audio_processor, self.fps)
        self.subtitle_generator = SubtitleGenerator()
        self.frame_generator = FrameGenerator(self.video_processor, self.fps)
        self.bgm_mixer = BGMMixer()

    def generate_conversation_video(
        self,
        conversations: List[Dict],
        audio_file_list: List[str],
        output_path: str = None,
        progress_callback=None,
        enable_subtitles: bool = True,
        conversation_mode: str = "duo",
        sections: Optional[List[VideoSection]] = None,
    ) -> Optional[str]:
        """会話動画生成（メイン機能）"""
        if not output_path:
            output_path = os.path.join(
                Paths.get_outputs_dir(), "conversation_video.mp4"
            )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            character_images = self.resource_manager.load_character_images()
            backgrounds = self.resource_manager.load_backgrounds()
            item_images = self.resource_manager.load_item_images()

            if not self.resource_manager.validate_resources(
                character_images, backgrounds
            ):
                return None

            combined_audio, audio_clips, audio_durations = self.audio_combiner.combine_audio_files(
                audio_file_list
            )
            if combined_audio is None:
                return None

            if sections:
                logger.info("BGMをミキシング中...")
                section_durations = self._calculate_section_durations(
                    sections, audio_durations, audio_file_list
                )
                combined_audio = self.bgm_mixer.mix_bgm_with_voiceover(
                    combined_audio, sections, section_durations
                )

            actual_total_duration = combined_audio.duration
            total_frames = int(actual_total_duration * self.fps)

            logger.info(
                f"Audio duration: {actual_total_duration:.3f}s, Total frames: {total_frames} at {self.fps} FPS"
            )

            subtitle_lines = self.subtitle_generator.generate_subtitles(
                conversations, audio_file_list, backgrounds, enable_subtitles, audio_durations
            )

            segment_audio_intensities = self.audio_combiner.analyze_audio_segments(
                audio_file_list
            )

            blink_timings = self.resource_manager.generate_blink_timings(
                actual_total_duration
            )

            temp_video_path = output_path.replace(".mp4", "_temp.mp4")

            success = self.frame_generator.generate_video_frames(
                total_frames=total_frames,
                conversations=conversations,
                audio_file_list=audio_file_list,
                segment_audio_intensities=segment_audio_intensities,
                backgrounds=backgrounds,
                character_images=character_images,
                blink_timings=blink_timings,
                subtitle_lines=subtitle_lines,
                conversation_mode=conversation_mode,
                temp_video_path=temp_video_path,
                item_images=item_images,
                sections=sections,
                progress_callback=progress_callback,
            )

            if not success:
                return None

            logger.info("Adding audio to video...")
            final_output_path = self._combine_video_with_audio(
                temp_video_path, combined_audio, output_path
            )

            self.audio_combiner.cleanup_audio_clips(combined_audio, audio_clips)

            # BGMキャッシュのクリア
            if sections:
                self.bgm_mixer.clear_cache()

            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

            logger.info(f"Conversation video generated: {final_output_path}")
            return final_output_path

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            # エラー時もBGMキャッシュをクリア
            if sections:
                try:
                    self.bgm_mixer.clear_cache()
                except Exception:
                    pass
            return None

    def _combine_video_with_audio(
        self, temp_video_path: str, combined_audio, output_path: str
    ) -> str:
        """動画と音声の結合（精密な同期）"""
        video_clip = VideoFileClip(temp_video_path)

        video_duration = video_clip.duration
        audio_duration = combined_audio.duration
        duration_diff = abs(video_duration - audio_duration)

        logger.info(
            f"Video duration: {video_duration:.3f}s, Audio duration: {audio_duration:.3f}s, Diff: {duration_diff:.3f}s"
        )

        if duration_diff > 0.001:
            logger.info(
                f"Adjusting video duration from {video_duration:.3f}s to {audio_duration:.3f}s"
            )
            video_clip = video_clip.with_duration(audio_duration)

        final_clip = video_clip.with_audio(combined_audio)

        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
        )

        video_clip.close()
        final_clip.close()

        del video_clip
        del final_clip

        return output_path

    def _calculate_section_durations(
        self, sections: List[VideoSection], audio_durations: Dict[str, float], audio_file_list: List[str]
    ) -> List[float]:
        """各セクションの長さを計算

        Args:
            sections: ビデオセクションのリスト
            audio_durations: {audio_path: duration}の辞書
            audio_file_list: 音声ファイルパスのリスト

        Returns:
            List[float]: 各セクションの長さ（秒）のリスト
        """
        section_durations = []
        current_segment_index = 0

        for section in sections:
            segment_count = len(section.segments)
            # このセクションに属する音声ファイルのパスを取得
            section_audio_files = audio_file_list[current_segment_index : current_segment_index + segment_count]
            # このセクションに属する音声の長さを合計
            section_duration = sum(
                audio_durations.get(audio_path, 0.0) for audio_path in section_audio_files
            )
            section_durations.append(section_duration)
            current_segment_index += segment_count

        logger.info(
            f"セクション長さ計算完了: {len(sections)}セクション, "
            f"合計 {sum(section_durations):.2f}秒"
        )

        return section_durations

    def cleanup(self):
        """メモリリソースのクリーンアップ"""
        try:
            # BGMキャッシュのクリア
            if hasattr(self, 'bgm_mixer') and self.bgm_mixer:
                self.bgm_mixer.clear_cache()

            if hasattr(self.video_processor, '_resize_cache'):
                cache_size = len(self.video_processor._resize_cache)
                self.video_processor._resize_cache.clear()
                logger.info(f"Cleared resize cache ({cache_size} entries)")

            try:
                from src.core.video_processor import _load_character_images_cached
                cache_info = _load_character_images_cached.cache_info()
                _load_character_images_cached.cache_clear()
                logger.info(f"Cleared LRU cache (hits: {cache_info.hits}, misses: {cache_info.misses}, size: {cache_info.currsize})")
            except Exception as e:
                logger.warning(f"Failed to clear LRU cache: {e}")

            if hasattr(self.video_processor, '_cached_font'):
                self.video_processor._cached_font = None
                logger.info("Cleared font cache")

            collected = gc.collect()
            logger.info(f"Garbage collection: collected {collected} objects")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
