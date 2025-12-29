"""フレーム合成関連のMixin"""

import logging
from typing import List, Tuple, Optional, Dict
import cv2
import numpy as np

from app.config import Characters

logger = logging.getLogger(__name__)


class CompositorMixin:
    """フレーム合成機能を提供するMixin"""

    def _get_resized_image(
        self,
        original_img: np.ndarray,
        char_name: str,
        expression: str,
        intensity: float,
        is_blinking: bool,
        target_width: int,
        target_height: int,
    ) -> np.ndarray:
        """リサイズ画像をキャッシュから取得"""
        mouth_state = self._get_mouth_state(intensity, is_blinking)
        cache_key = (char_name, expression, mouth_state, target_width, target_height)

        if cache_key in self._resize_cache:
            return self._resize_cache[cache_key]

        resized_img = cv2.resize(original_img, (target_width, target_height))

        if len(self._resize_cache) >= 500:
            first_key = next(iter(self._resize_cache))
            del self._resize_cache[first_key]

        self._resize_cache[cache_key] = resized_img

        return resized_img

    def composite_frame(
        self,
        background: np.ndarray,
        character: np.ndarray,
        position: Tuple[int, int] = None,
    ) -> np.ndarray:
        """キャラクターを背景に合成"""
        if position is None:
            bg_h, bg_w = background.shape[:2]
            char_h, char_w = character.shape[:2]
            position = ((bg_w - char_w) // 2, (bg_h - char_h) // 2)

        x, y = position
        result = background.copy()

        if character.shape[2] == 4:
            char_rgb = character[:, :, :3]
            char_alpha = character[:, :, 3] / 255.0

            char_h, char_w = character.shape[:2]
            bg_h, bg_w = background.shape[:2]

            if y < 0:
                char_rgb = char_rgb[-y:, :]
                char_alpha = char_alpha[-y:, :]
                char_h += y
                y = 0

            if x < 0:
                char_rgb = char_rgb[:, -x:]
                char_alpha = char_alpha[:, -x:]
                char_w += x
                x = 0

            if y + char_h > bg_h:
                char_h = bg_h - y
                if char_h > 0:
                    char_rgb = char_rgb[:char_h, :]
                    char_alpha = char_alpha[:char_h, :]

            if x + char_w > bg_w:
                char_w = bg_w - x
                if char_w > 0:
                    char_rgb = char_rgb[:, :char_w]
                    char_alpha = char_alpha[:, :char_w]

            if (
                char_h > 0
                and char_w > 0
                and char_rgb.shape[0] > 0
                and char_rgb.shape[1] > 0
            ):
                char_alpha_expanded = char_alpha[:, :, np.newaxis]
                for c in range(3):
                    result[y : y + char_h, x : x + char_w, c] = (
                        char_alpha_expanded[:, :, 0] * char_rgb[:, :, c]
                        + (1 - char_alpha_expanded[:, :, 0])
                        * background[y : y + char_h, x : x + char_w, c]
                    )
        else:
            char_h, char_w = character.shape[:2]
            result[y : y + char_h, x : x + char_w] = character

        return result

    def composite_conversation_frame(
        self,
        background: np.ndarray,
        character_images: Dict[str, Dict[str, Dict[str, np.ndarray]]],
        active_speakers: Dict[str, Dict[str, any]],
        conversation_mode: str = "duo",
        current_time: float = 0.0,
        blink_timings: List[Dict] = None,
    ) -> np.ndarray:
        """会話用のフレーム合成（表情対応）"""
        result = background.copy()

        # デバッグ: active_speakers の内容をログ出力（サンプリング）
        if not hasattr(self, "_composite_call_count"):
            self._composite_call_count = 0
        self._composite_call_count += 1

        if conversation_mode == "solo":
            sorted_chars = []
            for char_name, speaker_data in active_speakers.items():
                intensity = 0
                if isinstance(speaker_data, dict):
                    intensity = speaker_data.get("intensity", 0)
                else:
                    intensity = float(speaker_data) if speaker_data else 0

                if intensity > 0.1:
                    sorted_chars.append((char_name, speaker_data))
        else:
            sorted_chars = sorted(
                active_speakers.items(),
                key=lambda x: self.characters.get(
                    x[0], Characters.ZUNDAMON
                ).x_offset_ratio,
            )

        for char_name, speaker_data in sorted_chars:
            if char_name not in character_images or char_name not in self.characters:
                continue

            if isinstance(speaker_data, dict):
                intensity = speaker_data.get("intensity", 0.0)
                expression = speaker_data.get("expression", "normal")
            else:
                intensity = float(speaker_data)
                expression = "normal"

            if expression in character_images[char_name]:
                char_imgs = character_images[char_name][expression]
            elif "normal" in character_images[char_name]:
                char_imgs = character_images[char_name]["normal"]
                # 初回のみ警告ログを出力（ログの大量出力を防ぐ）
                if not hasattr(self, "_expression_warnings"):
                    self._expression_warnings = set()
                warning_key = (char_name, expression, "normal")
                if warning_key not in self._expression_warnings:
                    logger.debug(
                        f"[COMPOSITE] Expression '{expression}' not found for {char_name}, using 'normal'"
                    )
                    self._expression_warnings.add(warning_key)
            else:
                available_expressions = list(character_images[char_name].keys())
                if available_expressions:
                    char_imgs = character_images[char_name][available_expressions[0]]
                    # 初回のみ警告ログを出力（ログの大量出力を防ぐ）
                    if not hasattr(self, "_expression_warnings"):
                        self._expression_warnings = set()
                    warning_key = (char_name, expression, available_expressions[0])
                    if warning_key not in self._expression_warnings:
                        logger.debug(
                            f"[COMPOSITE] Expression '{expression}' not found for {char_name}, using '{available_expressions[0]}'"
                        )
                        self._expression_warnings.add(warning_key)
                else:
                    logger.error(f"No expressions available for {char_name}")
                    continue

            is_blinking = False
            if blink_timings:
                is_blinking = self.is_character_blinking(
                    current_time, blink_timings, char_name
                )

            # キャラクター別の口パク感度調整
            adjusted_intensity = intensity
            if char_name == "zundamon":
                # ずんだもんは口の動きを大きくする
                adjusted_intensity = intensity * 1.7

            mouth_img = self.select_mouth_image(
                adjusted_intensity, char_imgs, is_blinking
            )

            bg_h, bg_w = background.shape[:2]
            char_h, char_w = mouth_img.shape[:2]

            char_config = self.characters.get(char_name, Characters.ZUNDAMON)
            unified_size_ratio = char_config.size_ratio
            target_height = int(bg_h * unified_size_ratio)
            target_width = int(char_w * target_height / char_h)

            x_offset_ratio = char_config.x_offset_ratio
            x = int(bg_w * x_offset_ratio - target_width // 2)

            y = int(bg_h * char_config.y_offset_ratio)

            if target_width > bg_w * 0.8:
                target_width = int(bg_w * 0.8)
                target_height = int(char_h * target_width / char_w)

            mouth_img = self._get_resized_image(
                mouth_img,
                char_name,
                expression,
                intensity,
                is_blinking,
                target_width,
                target_height,
            )

            margin = 10
            x = max(-target_width // 3, min(x, bg_w - target_width // 3 * 2))
            y = max(margin, min(y, bg_h - target_height - margin))

            result = self.composite_frame(result, mouth_img, (x, y))

        return result

    def composite_conversation_frame_with_item(
        self,
        background: np.ndarray,
        character_images: Dict[str, Dict[str, Dict[str, np.ndarray]]],
        active_speakers: Dict[str, Dict[str, any]],
        conversation_mode: str = "duo",
        current_time: float = 0.0,
        blink_timings: List[Dict] = None,
        item_image: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """会話用のフレーム合成（アイテム画像表示対応版）

        Args:
            background: 背景画像
            character_images: キャラクター画像辞書
            active_speakers: アクティブな話者情報
            conversation_mode: 会話モード
            current_time: 現在時刻
            blink_timings: 瞬きタイミング
            item_image: 教育アイテム画像（None の場合は表示しない）

        Returns:
            合成されたフレーム
        """
        # 既存のフレーム合成処理
        frame = self.composite_conversation_frame(
            background,
            character_images,
            active_speakers,
            conversation_mode,
            current_time,
            blink_timings,
        )

        # アイテム画像がある場合は右側中央に配置
        if item_image is not None:
            max_size = 400  # 最大サイズ（正方形の枠）

            # 元の画像サイズを取得
            orig_h, orig_w = item_image.shape[:2]

            # アスペクト比を維持してリサイズ
            scale = min(max_size / orig_w, max_size / orig_h)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)

            # リサイズ（高品質な補間方法を使用）
            item_resized = cv2.resize(item_image, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # 正方形のキャンバス（透明）を作成
            if item_image.shape[2] == 4:  # RGBA画像の場合
                canvas = np.zeros((max_size, max_size, 4), dtype=np.uint8)
            else:  # RGB画像の場合
                canvas = np.zeros((max_size, max_size, 3), dtype=np.uint8)

            # 中央配置のためのオフセット計算
            paste_x = (max_size - new_w) // 2
            paste_y = (max_size - new_h) // 2

            # キャンバスの中央に画像を配置
            canvas[paste_y : paste_y + new_h, paste_x : paste_x + new_w] = item_resized

            # 最終的なアイテム画像
            item_resized = canvas
            item_width = max_size
            item_height = max_size

            # 右側上部の位置を計算（右端からマージン150px、上から80px）
            frame_h, frame_w = frame.shape[:2]
            x_offset = frame_w - item_width - 150  # 右端から150px内側
            y_offset = 80  # 上から80px

            # アイテム画像の合成（アルファチャンネル対応）
            if item_resized.shape[2] == 4:  # RGBA画像の場合
                # アルファチャンネルを分離
                alpha = item_resized[:, :, 3] / 255.0

                # RGB部分を取得
                item_rgb = item_resized[:, :, :3]

                # 背景部分を取得
                bg_region = frame[
                    y_offset : y_offset + item_height, x_offset : x_offset + item_width
                ]

                # アルファブレンディング
                for c in range(3):
                    bg_region[:, :, c] = (
                        alpha * item_rgb[:, :, c] + (1 - alpha) * bg_region[:, :, c]
                    )

                frame[
                    y_offset : y_offset + item_height, x_offset : x_offset + item_width
                ] = bg_region
            else:
                # RGB画像の場合は半透明合成
                alpha = 0.9  # 不透明度
                bg_region = frame[
                    y_offset : y_offset + item_height, x_offset : x_offset + item_width
                ]
                blended = cv2.addWeighted(bg_region, 1 - alpha, item_resized, alpha, 0)
                frame[
                    y_offset : y_offset + item_height, x_offset : x_offset + item_width
                ] = blended

        return frame

