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

logger = logging.getLogger(__name__)


class VideoGenerator:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.fps = self.video_processor.fps

        # 各処理クラスの初期化
        self.resource_manager = ResourceManager(self.video_processor)
        self.audio_combiner = AudioCombiner(self.audio_processor, self.fps)
        self.subtitle_generator = SubtitleGenerator()
        self.frame_generator = FrameGenerator(self.video_processor, self.fps)

    def generate_conversation_video(
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
            character_images = self.resource_manager.load_character_images()
            backgrounds = self.resource_manager.load_backgrounds()

            if not self.resource_manager.validate_resources(
                character_images, backgrounds
            ):
                return None

            # 音声結合（duration情報も取得）
            combined_audio, audio_clips, audio_durations = self.audio_combiner.combine_audio_files(
                audio_file_list
            )
            if combined_audio is None:
                return None

            # 実際の音声時間を基準にフレーム数を計算
            actual_total_duration = combined_audio.duration
            total_frames = int(actual_total_duration * self.fps)

            logger.info(
                f"Audio duration: {actual_total_duration:.3f}s, Total frames: {total_frames} at {self.fps} FPS"
            )

            # 字幕作成（duration情報を再利用してメモリ削減）
            subtitle_lines = self.subtitle_generator.generate_subtitles(
                conversations, audio_file_list, backgrounds, enable_subtitles, audio_durations
            )

            # 音声解析
            segment_audio_intensities = self.audio_combiner.analyze_audio_segments(
                audio_file_list
            )

            # 瞬きタイミング生成
            blink_timings = self.resource_manager.generate_blink_timings(
                actual_total_duration
            )

            # 動画書き出し
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
                progress_callback=progress_callback,
            )

            if not success:
                return None

            # 音声付加
            logger.info("Adding audio to video...")
            final_output_path = self._combine_video_with_audio(
                temp_video_path, combined_audio, output_path
            )

            # クリーンアップ
            self.audio_combiner.cleanup_audio_clips(combined_audio, audio_clips)

            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

            logger.info(f"Conversation video generated: {final_output_path}")
            return final_output_path

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return None

    def _combine_video_with_audio(
        self, temp_video_path: str, combined_audio, output_path: str
    ) -> str:
        """動画と音声の結合（精密な同期）"""
        video_clip = VideoFileClip(temp_video_path)

        # 映像の長さを音声に正確に合わせる
        video_duration = video_clip.duration
        audio_duration = combined_audio.duration
        duration_diff = abs(video_duration - audio_duration)

        logger.info(
            f"Video duration: {video_duration:.3f}s, Audio duration: {audio_duration:.3f}s, Diff: {duration_diff:.3f}s"
        )

        # 1ms以上の差がある場合は映像の長さを調整
        if duration_diff > 0.001:
            logger.info(
                f"Adjusting video duration from {video_duration:.3f}s to {audio_duration:.3f}s"
            )
            video_clip = video_clip.with_duration(audio_duration)

        final_clip = video_clip.with_audio(combined_audio)

        # より精密なエンコーディング設定
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
        )

        video_clip.close()
        final_clip.close()

        # 明示的にメモリ解放
        del video_clip
        del final_clip

        return output_path

    def cleanup(self):
        """メモリリソースのクリーンアップ（メモリリーク対策）"""
        try:
            # 1. リサイズキャッシュをクリア
            if hasattr(self.video_processor, '_resize_cache'):
                cache_size = len(self.video_processor._resize_cache)
                self.video_processor._resize_cache.clear()
                logger.info(f"Cleared resize cache ({cache_size} entries)")

            # 2. LRUキャッシュをクリア（グローバル関数）
            try:
                from src.core.video_processor import _load_character_images_cached
                cache_info = _load_character_images_cached.cache_info()
                _load_character_images_cached.cache_clear()
                logger.info(f"Cleared LRU cache (hits: {cache_info.hits}, misses: {cache_info.misses}, size: {cache_info.currsize})")
            except Exception as e:
                logger.warning(f"Failed to clear LRU cache: {e}")

            # 3. フォントキャッシュをクリア
            if hasattr(self.video_processor, '_cached_font'):
                self.video_processor._cached_font = None
                logger.info("Cleared font cache")

            # 4. 強制ガベージコレクション
            collected = gc.collect()
            logger.info(f"Garbage collection: collected {collected} objects")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
