import librosa
import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)


class AudioProcessor:
    def __init__(self, fps: int = 30):
        self.fps = fps

    def analyze_audio_for_mouth_sync(self, audio_path: str) -> List[float]:
        """音声解析（口パク用）"""
        try:
            y, sr = librosa.load(audio_path)
            if len(y) == 0:
                logger.warning(f"Empty audio file: {audio_path}")
                return []

            hop_length = int(sr / self.fps)
            if hop_length <= 0:
                hop_length = 1024

            frame_length = hop_length * 2
            if frame_length > len(y):
                frame_length = len(y)

            rms = librosa.feature.rms(
                y=y, hop_length=hop_length, frame_length=frame_length
            )[0]

            if len(rms) == 0:
                logger.warning(f"RMS analysis returned empty array for: {audio_path}")
                return []

            rms_max = np.max(rms)
            if rms_max > 0:
                rms = rms / rms_max
            else:
                logger.warning(f"RMS max is zero for: {audio_path}")
                rms = np.zeros_like(rms)

            return rms.tolist()
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return []
