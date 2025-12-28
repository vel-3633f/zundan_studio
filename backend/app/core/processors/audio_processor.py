import librosa
import numpy as np
import logging
from typing import List, Tuple
from moviepy import AudioFileClip
from scipy import signal

logger = logging.getLogger(__name__)


class AudioProcessor:
    def __init__(self, fps: int = 30):
        self.fps = fps

    def analyze_audio_for_mouth_sync(self, audio_path: str) -> Tuple[List[float], float]:
        """音声解析（口パク用）- 実時間ベース"""
        try:
            # 1. 実際の音声時間を取得
            audio_clip = AudioFileClip(audio_path)
            actual_duration = audio_clip.duration
            audio_clip.close()

            if actual_duration <= 0:
                logger.warning(f"Invalid audio duration: {audio_path}")
                return [], 0.0

            # 2. 音声データ読み込み
            y, sr = librosa.load(audio_path)
            if len(y) == 0:
                logger.warning(f"Empty audio file: {audio_path}")
                return [], actual_duration

            # 3. 目標フレーム数を実時間から計算
            target_frames = max(1, int(actual_duration * self.fps))

            # 4. 実時間ベースのhop_length計算
            time_per_frame = actual_duration / target_frames
            hop_length = max(1, int(sr * time_per_frame))

            # 5. フレーム長の調整
            frame_length = hop_length * 2
            if frame_length > len(y):
                frame_length = len(y)

            # 6. RMS解析
            rms = librosa.feature.rms(
                y=y, hop_length=hop_length, frame_length=frame_length
            )[0]

            if len(rms) == 0:
                logger.warning(f"RMS analysis returned empty array for: {audio_path}")
                return [], actual_duration

            # 7. 正確なフレーム数にリサンプリング
            if len(rms) != target_frames:
                try:
                    rms_resampled = signal.resample(rms, target_frames)
                    rms = rms_resampled
                except Exception as resample_error:
                    logger.warning(f"Resampling failed, using interpolation: {resample_error}")
                    # フォールバック：線形補間
                    x_old = np.linspace(0, 1, len(rms))
                    x_new = np.linspace(0, 1, target_frames)
                    rms = np.interp(x_new, x_old, rms)

            # 8. 正規化
            rms_max = np.max(rms)
            if rms_max > 0:
                rms = rms / rms_max
            else:
                logger.warning(f"RMS max is zero for: {audio_path}")
                rms = np.zeros_like(rms)

            return rms.tolist(), actual_duration

        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return [], 0.0
