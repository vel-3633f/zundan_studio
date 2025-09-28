from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class SubtitleData:
    """字幕データクラス"""

    text: str
    start_time: float
    end_time: float
    duration: float
    speaker: str
    background: str


@dataclass
class AudioSegmentInfo:
    """音声セグメント情報"""

    start_time: float
    intensities: List[float]
    duration: float
    actual_frame_count: int  # 実際のフレーム数（精密な同期用）


