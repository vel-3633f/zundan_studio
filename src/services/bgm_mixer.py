"""BGMミキサーモジュール

セクションごとに異なるBGMを動画に合成します。
"""

import os
import logging
from typing import List, Optional
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

from config.bgm_library import get_bgm_file_path, get_bgm_track
from src.models.food_over import VideoSection

logger = logging.getLogger(__name__)


class BGMMixer:
    """BGMミキサークラス"""

    def __init__(self):
        pass

    def create_section_bgm_track(
        self,
        section: VideoSection,
        start_time: float,
        duration: float
    ) -> Optional[AudioFileClip]:
        """セクション用のBGMトラックを作成

        Args:
            section: ビデオセクション
            start_time: セクションの開始時刻（秒）
            duration: セクションの長さ（秒）

        Returns:
            AudioFileClip: BGM音声クリップ、BGMがない場合はNone
        """
        if section.bgm_id == "none" or not section.bgm_id:
            return None

        bgm_file_path = get_bgm_file_path(section.bgm_id)
        if not bgm_file_path or not os.path.exists(bgm_file_path):
            logger.warning(
                f"BGMファイルが見つかりません: {section.bgm_id} "
                f"(path: {bgm_file_path})"
            )
            return None

        try:
            # BGMファイルを読み込み
            bgm_clip = AudioFileClip(bgm_file_path)

            # BGMをループさせて必要な長さに調整
            if bgm_clip.duration < duration:
                # ループ回数を計算
                loop_count = int(duration / bgm_clip.duration) + 1
                bgm_clip = bgm_clip.loop(n=loop_count)

            # 必要な長さにトリミング
            bgm_clip = bgm_clip.subclipped(0, duration)

            # 音量を調整
            bgm_clip = bgm_clip.with_volume_scaled(section.bgm_volume)

            # フェードイン・フェードアウト（0.5秒）
            fade_duration = min(0.5, duration / 4)  # 最大0.5秒、短いセクションは1/4
            bgm_clip = bgm_clip.audio_fadein(fade_duration).audio_fadeout(fade_duration)

            # タイムライン上の位置を設定
            bgm_clip = bgm_clip.with_start(start_time)

            track = get_bgm_track(section.bgm_id)
            logger.info(
                f"BGM作成: {track.name if track else section.bgm_id} "
                f"(start: {start_time:.2f}s, duration: {duration:.2f}s, "
                f"volume: {section.bgm_volume})"
            )

            return bgm_clip

        except Exception as e:
            logger.error(f"BGM作成エラー ({section.bgm_id}): {e}", exc_info=True)
            return None

    def mix_bgm_with_voiceover(
        self,
        voiceover_audio,
        sections: List[VideoSection],
        section_durations: List[float]
    ):
        """ボイスオーバーとBGMを合成

        Args:
            voiceover_audio: ボイスオーバー音声
            sections: ビデオセクションのリスト
            section_durations: 各セクションの長さ（秒）のリスト

        Returns:
            CompositeAudioClip: 合成された音声
        """
        if len(sections) != len(section_durations):
            logger.error(
                f"セクション数とduration数が一致しません: "
                f"sections={len(sections)}, durations={len(section_durations)}"
            )
            return voiceover_audio

        bgm_clips = []
        current_time = 0.0

        for section, duration in zip(sections, section_durations):
            bgm_clip = self.create_section_bgm_track(
                section,
                start_time=current_time,
                duration=duration
            )

            if bgm_clip:
                bgm_clips.append(bgm_clip)

            current_time += duration

        if not bgm_clips:
            logger.info("BGMが設定されていないため、ボイスオーバーのみ使用")
            return voiceover_audio

        # ボイスオーバーとBGMを合成
        logger.info(f"BGMトラック数: {len(bgm_clips)}")
        composite_audio = CompositeAudioClip([voiceover_audio] + bgm_clips)

        return composite_audio

    def cleanup_bgm_clips(self, bgm_clips: List[AudioFileClip]):
        """BGMクリップのクリーンアップ

        Args:
            bgm_clips: BGM音声クリップのリスト
        """
        for clip in bgm_clips:
            try:
                if clip:
                    clip.close()
            except Exception as e:
                logger.warning(f"BGMクリップのクリーンアップエラー: {e}")
