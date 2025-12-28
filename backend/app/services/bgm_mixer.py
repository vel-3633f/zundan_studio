"""BGMミキサーモジュール

セクションごとに異なるBGMを動画に合成します。
"""

import os
import logging
import threading
import time
import gc
from typing import List, Optional, Dict
from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips, AudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut

from app.config.resource_config.bgm_library import get_bgm_file_path, get_bgm_track
from app.models.scripts.common import VideoSection

logger = logging.getLogger(__name__)


class BGMMixer:
    """BGMミキサークラス"""

    def __init__(self):
        # 使用中のBGMクリップを追跡（クリーンアップ用）
        self._active_clips: List[AudioFileClip] = []
        # BGMファイルのキャッシュ（音声データをメモリに保持）
        self._bgm_cache: Dict[str, AudioFileClip] = {}
        # ファイル読み込みを直列化するためのロック（ffmpegのデッドロック回避）
        self._load_lock = threading.Lock()

    def _load_bgm_file(self, bgm_file_path: str, max_retries: int = 3) -> Optional[AudioFileClip]:
        """BGMファイルを読み込む（キャッシュ使用、スレッドセーフ、リトライ機能付き）

        Args:
            bgm_file_path: BGMファイルのパス
            max_retries: 最大リトライ回数

        Returns:
            AudioFileClip: BGM音声クリップ、失敗時はNone
        """
        # キャッシュチェックはロック外で実行（読み取りのみなので安全）
        if bgm_file_path in self._bgm_cache:
            return self._bgm_cache[bgm_file_path]

        # ファイル読み込みは完全に直列化（ffmpegのデッドロック回避）
        with self._load_lock:
            # ダブルチェック: ロック取得中に他スレッドが読み込んだ可能性
            if bgm_file_path in self._bgm_cache:
                return self._bgm_cache[bgm_file_path]

            # リトライ機構
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        wait_time = attempt * 0.5  # 0.5秒、1.0秒、1.5秒...
                        logger.warning(f"BGMファイル読み込みリトライ ({attempt + 1}/{max_retries}): {bgm_file_path}")
                        time.sleep(wait_time)
                        # ガベージコレクションを実行してファイルハンドルを解放
                        gc.collect()

                    bgm_clip = AudioFileClip(bgm_file_path)
                    self._bgm_cache[bgm_file_path] = bgm_clip
                    self._active_clips.append(bgm_clip)
                    return bgm_clip

                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"BGMファイルの読み込み失敗 (試行 {attempt + 1}/{max_retries}): {bgm_file_path} - {str(e)[:100]}")
                        # 失敗時のクリーンアップ
                        gc.collect()
                    else:
                        logger.error(f"BGMファイルの読み込みエラー ({bgm_file_path}): {e}")
                        return None

            return None

    def create_section_bgm_track(
        self,
        section: VideoSection,
        start_time: float,
        duration: float
    ) -> Optional[AudioClip]:
        """セクション用のBGMトラックを作成

        Args:
            section: ビデオセクション
            start_time: セクションの開始時刻（秒）
            duration: セクションの長さ（秒）

        Returns:
            AudioClip: BGM音声クリップ、BGMがない場合はNone
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
            # キャッシュからBGMファイルを取得（初回のみファイルを開く）
            base_bgm_clip = self._load_bgm_file(bgm_file_path)
            if base_bgm_clip is None:
                return None

            # BGMをループさせて必要な長さに調整
            # 注意: base_bgm_clipを直接使用せず、subclipped()で新しいクリップを作成
            if base_bgm_clip.duration < duration:
                # ループ回数を計算
                loop_count = int(duration / base_bgm_clip.duration) + 1
                # 各ループで新しいsubclipを作成（ファイルハンドルの競合を回避）
                loop_clips = []
                for i in range(loop_count):
                    # subclipped()は新しいクリップインスタンスを返す
                    if i == 0:
                        loop_clips.append(base_bgm_clip.subclipped(0, base_bgm_clip.duration))
                    else:
                        loop_clips.append(base_bgm_clip.subclipped(0, base_bgm_clip.duration))
                bgm_clip = concatenate_audioclips(loop_clips)
            else:
                bgm_clip = base_bgm_clip.subclipped(0, min(duration, base_bgm_clip.duration))

            # 必要な長さに正確にトリミング
            if bgm_clip.duration > duration:
                bgm_clip = bgm_clip.subclipped(0, duration)

            # 音量を調整
            bgm_clip = bgm_clip.with_volume_scaled(section.bgm_volume)

            # フェードイン・フェードアウト（0.5秒）
            fade_duration = min(0.5, duration / 4)  # 最大0.5秒、短いセクションは1/4
            bgm_clip = bgm_clip.with_effects([
                AudioFadeIn(fade_duration),
                AudioFadeOut(fade_duration)
            ])

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

        # 事前にすべての必要なBGMファイルを読み込む（デッドロック回避）
        unique_bgm_ids = set()
        for section in sections:
            if section.bgm_id and section.bgm_id != "none":
                bgm_file_path = get_bgm_file_path(section.bgm_id)
                if bgm_file_path and os.path.exists(bgm_file_path):
                    unique_bgm_ids.add(bgm_file_path)

        # すべてのBGMファイルを順次読み込み
        success_count = 0
        for idx, bgm_path in enumerate(unique_bgm_ids, 1):
            result = self._load_bgm_file(bgm_path)
            if result:
                success_count += 1
            # ファイル間で少し待機（ffmpegプロセスのクリーンアップ時間を確保）
            if idx < len(unique_bgm_ids):
                time.sleep(0.2)

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
            return voiceover_audio

        # ボイスオーバーとBGMを合成
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

    def clear_cache(self):
        """使用中のBGMクリップとキャッシュをクリーンアップする"""
        closed_count = 0

        # キャッシュされたBGMクリップをクローズ
        for bgm_path, clip in self._bgm_cache.items():
            try:
                if clip:
                    clip.close()
                    closed_count += 1
            except Exception as e:
                logger.warning(f"BGMキャッシュのクリーンアップエラー ({bgm_path}): {e}")

        self._bgm_cache.clear()
        self._active_clips.clear()
