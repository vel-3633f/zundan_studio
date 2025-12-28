"""瞬き・口パクアニメーション関連のMixin"""

import logging
import random
from typing import List, Dict
import numpy as np

logger = logging.getLogger(__name__)


class AnimationMixin:
    """瞬き・口パクアニメーション機能を提供するMixin"""

    def generate_blink_timings(
        self, total_duration: float, character_name: str = None
    ) -> List[Dict]:
        """瞬きタイミングを生成"""
        blink_times = []
        current_time = random.uniform(1.0, 3.0)

        while current_time < total_duration - self.blink_config["duration"]:
            blink_start = current_time
            blink_end = current_time + self.blink_config["duration"]

            blink_times.append(
                {"start": blink_start, "end": blink_end, "character": character_name}
            )

            interval = random.uniform(
                self.blink_config["min_interval"], self.blink_config["max_interval"]
            )
            current_time += interval

        return blink_times

    def is_character_blinking(
        self, current_time: float, blink_timings: List[Dict], character_name: str
    ) -> bool:
        """指定されたキャラクターが現在瞬きしているかチェック"""
        for blink in blink_timings:
            if (
                blink.get("character") == character_name
                or blink.get("character") is None
            ):
                if blink["start"] <= current_time <= blink["end"]:
                    return True
        return False

    def select_mouth_image(
        self, intensity: float, images: dict, is_blinking: bool = False
    ) -> np.ndarray:
        """音声強度に基づく口画像選択（瞬き対応）"""

        # 利用可能な画像キーを確認
        if not images:
            logger.error("No images available for mouth selection")
            return None

        # デバッグ情報を常にログ出力（INFO レベル）
        if not hasattr(self, "_mouth_call_count"):
            self._mouth_call_count = 0

        self._mouth_call_count += 1

        # 瞬き中の処理
        if is_blinking:
            if "blink" in images:
                return images["blink"]
            elif "closed" in images:
                return images["closed"]
            else:
                # フォールバック: 最初の利用可能な画像
                fallback_key = list(images.keys())[0]
                return images[fallback_key]

        # 通常の口パクアニメーション
        # intensity値に基づいて適切な画像を選択
        if intensity < 0.1:
            # 優先順位: closed > blink > half > open > 最初の画像
            for key in ["closed", "blink", "half", "open"]:
                if key in images:
                    return images[key]
        elif intensity < 0.4:
            # 優先順位: half > closed > open > 最初の画像
            for key in ["half", "closed", "open"]:
                if key in images:
                    return images[key]
        else:
            # 優先順位: open > half > closed > 最初の画像
            for key in ["open", "half", "closed"]:
                if key in images:
                    return images[key]

        # フォールバック
        fallback_key = list(images.keys())[0]
        return images[fallback_key]

    def _get_mouth_state(self, intensity: float, is_blinking: bool) -> str:
        """音声強度から口の状態を判定"""
        if is_blinking:
            return "blink"
        elif intensity < 0.1:
            return "closed"
        elif intensity < 0.4:
            return "half"
        else:
            return "open"

