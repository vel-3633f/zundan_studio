import cv2
import numpy as np
import os
import logging
import random
from functools import lru_cache
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont
from budoux import load_default_japanese_parser

from app.config import (
    APP_CONFIG,
    SUBTITLE_CONFIG,
    Characters,
    Backgrounds,
    Expressions,
    Paths,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=10)
def _load_character_images_cached(
    character_name: str, expression: str, base_path: str
) -> tuple:
    """キャラクター画像を読み込み（キャッシュ機能付き）

    Args:
        character_name: キャラクター名
        expression: 表情名
        base_path: ベースディレクトリパス

    Returns:
        tuple: (images_dict_items, target_size) のタプル
            images_dict_items は (key, image_bytes) のタプルのリスト
    """
    expression_dir = os.path.join(base_path, expression)

    images = {}
    image_files = {
        "closed": f"{expression}_closed.png",
        "half": f"{expression}_half.png",
        "open": f"{expression}_open.png",
        "blink": f"{expression}_blink.png",
    }

    for key, filename in image_files.items():
        path = os.path.join(expression_dir, filename)

        if os.path.exists(path):
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                images[key] = img
        else:
            if expression != "normal":
                fallback_path = os.path.join(base_path, "normal", f"normal_{key}.png")
                if os.path.exists(fallback_path):
                    img = cv2.imread(fallback_path, cv2.IMREAD_UNCHANGED)
                    if img is not None:
                        images[key] = img
                        continue

    if images:
        target_size = images[list(images.keys())[0]].shape[:2]
        for key in images:
            images[key] = cv2.resize(images[key], (target_size[1], target_size[0]))

        cached_images = []
        for key, img in images.items():
            img_bytes = img.tobytes()
            cached_images.append((key, img.shape, img.dtype.str, img_bytes))

        return tuple(cached_images), target_size

    return tuple(), None


class VideoProcessor:
    def __init__(self):
        self.fps = APP_CONFIG.fps
        self.resolution = APP_CONFIG.resolution
        self.characters = Characters.get_all()
        self.subtitle_config = SUBTITLE_CONFIG

        self._cached_font = None
        self._resize_cache = {}
        self._budoux_parser = load_default_japanese_parser()

        self.blink_config = {
            "min_interval": 2.0,
            "max_interval": 6.0,
            "duration": 0.15,
        }

    def load_character_images(
        self, character_name: str = "zundamon", expression: str = "normal"
    ) -> Dict[str, np.ndarray]:
        """キャラクター画像を読み込み（特定の表情）"""
        base_path = Paths.get_character_dir(character_name)

        cached_data, target_size = _load_character_images_cached(
            character_name, expression, base_path
        )

        if not cached_data:
            return {}

        images = {}
        for key, shape, dtype_str, img_bytes in cached_data:
            img = np.frombuffer(img_bytes, dtype=dtype_str).reshape(shape)
            images[key] = img.copy()

        return images

    def get_available_expressions(self, character_name: str) -> List[str]:
        """キャラクターで利用可能な表情を取得"""
        base_path = Paths.get_character_dir(character_name)
        if not os.path.exists(base_path):
            return []

        expressions = set()

        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                required_files = [
                    f"{item}_closed.png",
                    f"{item}_half.png",
                    f"{item}_open.png",
                ]
                if any(
                    os.path.exists(os.path.join(item_path, file))
                    for file in required_files
                ):
                    expressions.add(item)

        available_expressions = Expressions.get_available_names()
        return [expr for expr in available_expressions if expr in expressions]

    def load_character_images_all_expressions(
        self, character_name: str
    ) -> Dict[str, Dict[str, np.ndarray]]:
        """キャラクターの全表情画像を読み込み"""
        available_expressions = self.get_available_expressions(character_name)
        if not available_expressions:
            available_expressions = ["normal"]

        all_expressions = {}
        for expression in available_expressions:
            expr_images = self.load_character_images(character_name, expression)
            if expr_images:
                all_expressions[expression] = expr_images

        return all_expressions

    def load_all_character_images(self) -> Dict[str, Dict[str, Dict[str, np.ndarray]]]:
        """全キャラクターの全表情画像を読み込み"""
        all_images = {}
        for char_key, char_info in self.characters.items():
            char_expressions = self.load_character_images_all_expressions(char_key)
            if char_expressions:
                all_images[char_key] = char_expressions

        return all_images

    def load_backgrounds(self) -> Dict[str, np.ndarray]:
        """すべての背景画像を読み込み"""
        bg_dir = Paths.get_backgrounds_dir()

        backgrounds = {}

        if not os.path.exists(bg_dir):
            logger.error(f"Background directory not found: {bg_dir}")
            return backgrounds

        supported_extensions = Backgrounds.get_supported_extensions()

        for filename in os.listdir(bg_dir):
            file_path = os.path.join(bg_dir, filename)

            if not os.path.isfile(file_path):
                continue

            _, ext = os.path.splitext(filename.lower())
            if ext not in supported_extensions:
                continue

            try:
                bg = cv2.imread(file_path)
                if bg is not None:
                    bg = cv2.resize(bg, self.resolution)

                    bg_name = os.path.splitext(filename)[0]
                    backgrounds[bg_name] = bg

            except Exception as e:
                logger.error(f"Error loading background {file_path}: {e}")

        if "default_bg" in backgrounds:
            backgrounds["default"] = backgrounds["default_bg"]
        elif backgrounds:
            first_key = list(backgrounds.keys())[0]
            backgrounds["default"] = backgrounds[first_key]

        if not backgrounds:
            logger.error("No background images found")

        return backgrounds

    def get_background_names(self) -> List[str]:
        """利用可能な背景画像名のリストを取得"""
        backgrounds = self.load_backgrounds()
        names = [name for name in backgrounds.keys() if name != "default"]
        return sorted(names)

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

        if len(self._resize_cache) >= 100:
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
                logger.warning(
                    f"[COMPOSITE] Expression '{expression}' not found for {char_name}, using 'normal'"
                )
            else:
                available_expressions = list(character_images[char_name].keys())
                if available_expressions:
                    char_imgs = character_images[char_name][available_expressions[0]]
                    logger.warning(
                        f"[COMPOSITE] Expression '{expression}' not found for {char_name}, using '{available_expressions[0]}'"
                    )
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

    def _split_text_into_lines(self, text: str, max_chars_per_line: int) -> List[str]:
        """budouxを使って自然な位置でテキストを複数行に分割

        Args:
            text: 分割するテキスト
            max_chars_per_line: 1行あたりの最大文字数

        Returns:
            分割されたテキストの行リスト
        """
        if len(text) <= max_chars_per_line:
            return [text]

        chunks = self._budoux_parser.parse(text)

        lines = []
        current_line = ""

        for chunk in chunks:
            if len(current_line + chunk) <= max_chars_per_line:
                current_line += chunk
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = chunk
                else:
                    if len(chunk) > max_chars_per_line:
                        for i in range(0, len(chunk), max_chars_per_line):
                            lines.append(chunk[i : i + max_chars_per_line])
                    else:
                        current_line = chunk

        if current_line:
            lines.append(current_line)

        return lines

    def get_japanese_font(self) -> Optional[ImageFont.FreeTypeFont]:
        """日本語フォントを取得（キャッシュ機能付き）"""
        if self._cached_font is not None:
            return self._cached_font

        local_fonts_dir = Paths.get_fonts_dir()

        priority_fonts = [
            "NotoSansJP-Black.ttf",
        ]

        local_font_paths = []

        if os.path.exists(local_fonts_dir):
            for priority_font in priority_fonts:
                priority_path = os.path.join(local_fonts_dir, priority_font)
                if os.path.exists(priority_path):
                    local_font_paths.append(priority_path)

        font_paths = local_font_paths

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    if font_path.lower().endswith(".ttc"):
                        for index in range(15):
                            try:
                                font = ImageFont.truetype(
                                    font_path,
                                    self.subtitle_config.font_size,
                                    index=index,
                                )
                            except (OSError, IOError, ValueError):
                                continue
                    else:
                        font = ImageFont.truetype(
                            font_path, self.subtitle_config.font_size
                        )
                        try:
                            self._cached_font = font
                            return font
                        except Exception:
                            continue
                except Exception as e:
                    logger.warning(f"Failed to load font {font_path}: {e}")
                    continue

        logger.warning("No suitable Japanese font found, using default font")
        try:
            default_font = ImageFont.load_default()
            try:
                self._cached_font = default_font
                return default_font
            except Exception:
                logger.warning("Default font does not support Japanese characters")
                self._cached_font = default_font
                return default_font
        except Exception as e:
            logger.error(f"Failed to load default font: {e}")
            return None

    def draw_subtitle_on_frame(
        self,
        frame: np.ndarray,
        text: str,
        progress: float = 1.0,
        speaker: str = "zundamon",
    ) -> np.ndarray:
        """字幕をフレームに描画（複数行対応、左揃え）"""
        if not text.strip():
            return frame

        try:
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)

            font = self.get_japanese_font()
            if font is None:
                logger.warning("No font available")
                return frame

            max_chars = self.subtitle_config.max_chars_per_line
            lines = self._split_text_into_lines(text, max_chars)

            line_heights = []
            line_widths = []
            max_line_width = 0

            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                line_widths.append(width)
                line_heights.append(height)
                max_line_width = max(max_line_width, width)

            line_spacing = 8

            padding_x = self.subtitle_config.padding_x
            padding_top = self.subtitle_config.padding_top
            padding_bottom = self.subtitle_config.padding_bottom
            border_width = self.subtitle_config.border_width

            total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)
            bg_width = max_line_width + (padding_x * 2)
            bg_height = total_text_height + padding_top + padding_bottom

            bg_x = (self.resolution[0] - bg_width) // 2
            bg_y = self.resolution[1] - self.subtitle_config.margin_bottom - bg_height

            if pil_image.mode != "RGBA":
                pil_image = pil_image.convert("RGBA")
                draw = ImageDraw.Draw(pil_image)

            radius = self.subtitle_config.border_radius
            bg_color = self.subtitle_config.background_color
            border_color = self.characters.get(
                speaker, Characters.ZUNDAMON
            ).subtitle_color

            try:
                draw.rounded_rectangle(
                    [
                        bg_x - border_width,
                        bg_y - border_width,
                        bg_x + bg_width + border_width,
                        bg_y + bg_height + border_width,
                    ],
                    radius + border_width,
                    fill=border_color,
                )
                draw.rounded_rectangle(
                    [bg_x, bg_y, bg_x + bg_width, bg_y + bg_height],
                    radius,
                    fill=bg_color,
                )
            except AttributeError:
                draw.rectangle(
                    [
                        bg_x - border_width,
                        bg_y - border_width,
                        bg_x + bg_width + border_width,
                        bg_y + bg_height + border_width,
                    ],
                    fill=border_color,
                )
                draw.rectangle(
                    [bg_x, bg_y, bg_x + bg_width, bg_y + bg_height], fill=bg_color
                )

            outline_width = self.subtitle_config.outline_width
            outline_color = self.subtitle_config.outline_color
            text_color = self.subtitle_config.font_color

            current_y = bg_y + padding_top

            for i, line in enumerate(lines):
                text_x = bg_x + padding_x
                text_y = current_y

                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text(
                                (text_x + dx, text_y + dy),
                                line,
                                font=font,
                                fill=outline_color,
                            )

                draw.text((text_x, text_y), line, font=font, fill=text_color)

                current_y += line_heights[i] + line_spacing

            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        except Exception as e:
            logger.error(f"Subtitle drawing failed: {e}")
            return frame
