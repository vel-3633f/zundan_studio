import cv2
import numpy as np
import os
import logging
import random
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont

from config import (
    APP_CONFIG,
    SUBTITLE_CONFIG,
    Characters,
    Backgrounds,
    Expressions,
    Paths,
)

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self):
        self.fps = APP_CONFIG.fps
        self.resolution = APP_CONFIG.resolution
        self.characters = Characters.get_all()
        self.subtitle_config = SUBTITLE_CONFIG

        # ItemManagerをimportして初期化（遅延import）
        from src.services.item_manager import ItemManager

        self.item_manager = ItemManager()

        # フォントキャッシュ
        self._cached_font = None

        # 瞬き設定
        self.blink_config = {
            "min_interval": 2.0,  # 最小瞬き間隔（秒）
            "max_interval": 6.0,  # 最大瞬き間隔（秒）
            "duration": 0.15,  # 瞬きの長さ（秒）
        }

    def load_character_images(
        self, character_name: str = "zundamon", expression: str = "normal"
    ) -> Dict[str, np.ndarray]:
        """キャラクター画像を読み込み（特定の表情）"""
        base_path = Paths.get_character_dir(character_name)
        expression_dir = os.path.join(base_path, expression)

        images = {}
        image_files = {
            "closed": f"{expression}_closed.png",
            "half": f"{expression}_half.png",
            "open": f"{expression}_open.png",
            "blink": f"{expression}_blink.png",  # 瞬き用画像
        }

        for key, filename in image_files.items():
            path = os.path.join(expression_dir, filename)

            if os.path.exists(path):
                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if img is not None:
                    images[key] = img
            else:
                # フォールバック：normal表情を試す
                if expression != "normal":
                    fallback_path = os.path.join(
                        base_path, "normal", f"normal_{key}.png"
                    )
                    if os.path.exists(fallback_path):
                        img = cv2.imread(fallback_path, cv2.IMREAD_UNCHANGED)
                        if img is not None:
                            images[key] = img
                            continue

        if images:
            # 全画像を同じサイズにリサイズ
            target_size = images[list(images.keys())[0]].shape[:2]
            for key in images:
                images[key] = cv2.resize(images[key], (target_size[1], target_size[0]))

        return images

    def get_available_expressions(self, character_name: str) -> List[str]:
        """キャラクターで利用可能な表情を取得"""
        base_path = Paths.get_character_dir(character_name)
        if not os.path.exists(base_path):
            return []

        expressions = set()

        # フォルダ構造から表情を取得
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                # フォルダ内に必要なファイルが存在するかチェック
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

        # config.pyで定義された表情のみを返す
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

        # JSONファイルから背景設定を読み込み
        json_path = os.path.join(bg_dir, "backgrounds.json")
        if os.path.exists(json_path):
            Backgrounds.load_backgrounds_from_json(json_path)
            logger.info(f"Loaded background configurations from {json_path}")

        backgrounds = {}

        if not os.path.exists(bg_dir):
            logger.error(f"Background directory not found: {bg_dir}")
            return backgrounds

        # サポートする画像拡張子
        supported_extensions = Backgrounds.get_supported_extensions()

        for filename in os.listdir(bg_dir):
            file_path = os.path.join(bg_dir, filename)

            # ファイルかどうかチェック
            if not os.path.isfile(file_path):
                continue

            # 拡張子チェック
            _, ext = os.path.splitext(filename.lower())
            if ext not in supported_extensions:
                continue

            try:
                # 画像読み込み
                bg = cv2.imread(file_path)
                if bg is not None:
                    # リサイズ
                    bg = cv2.resize(bg, self.resolution)

                    bg_name = os.path.splitext(filename)[0]
                    backgrounds[bg_name] = bg

                    # 画像ファイルから動的に背景設定を登録
                    if not Backgrounds.is_valid_background(bg_name):
                        Backgrounds.register_background(
                            name=bg_name,
                            display_name=bg_name.replace("_", " ").title(),
                            emoji="🖼️",
                            description=f"背景画像: {bg_name}"
                        )

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
            # 瞬きの開始と終了時間
            blink_start = current_time
            blink_end = current_time + self.blink_config["duration"]

            blink_times.append(
                {"start": blink_start, "end": blink_end, "character": character_name}
            )

            # 次の瞬きまでの間隔をランダムに決定
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
        # 瞬き中は目を閉じた画像を優先（瞬き専用画像がなければclosedを使用）
        if is_blinking:
            return images.get(
                "blink", images.get("closed", images[list(images.keys())[0]])
            )

        # 通常の口パクアニメーション
        if intensity < 0.1:
            return images.get("closed", images[list(images.keys())[0]])
        elif intensity < 0.4:
            return images.get(
                "half", images.get("closed", images[list(images.keys())[0]])
            )
        else:
            return images.get(
                "open", images.get("half", images[list(images.keys())[0]])
            )

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

            # 境界チェック - 位置が負の値になる場合も考慮
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

            # 有効な領域がある場合のみ合成
            if (
                char_h > 0
                and char_w > 0
                and char_rgb.shape[0] > 0
                and char_rgb.shape[1] > 0
            ):
                # アルファチャンネルの次元を拡張
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
        character_items: Dict[str, str] = None,
    ) -> np.ndarray:
        """会話用のフレーム合成（表情対応）"""
        result = background.copy()

        if conversation_mode == "solo":
            # ソロモード：話しているキャラクターのみ表示
            sorted_chars = []
            for char_name, speaker_data in active_speakers.items():
                intensity = 0
                if isinstance(speaker_data, dict):
                    intensity = speaker_data.get("intensity", 0)
                else:
                    intensity = float(speaker_data) if speaker_data else 0

                if intensity > 0.1:  # 実際に話している場合のみ
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

            # 表情データの取得（後方互換性を考慮）
            if isinstance(speaker_data, dict):
                intensity = speaker_data.get("intensity", 0.0)
                expression = speaker_data.get("expression", "normal")
            else:
                # 旧形式（float）の場合
                intensity = float(speaker_data)
                expression = "normal"

            # 表情画像セットの取得
            if expression in character_images[char_name]:
                char_imgs = character_images[char_name][expression]
            elif "normal" in character_images[char_name]:
                char_imgs = character_images[char_name]["normal"]
            else:
                # 最初に見つかった表情を使用
                available_expressions = list(character_images[char_name].keys())
                if available_expressions:
                    char_imgs = character_images[char_name][available_expressions[0]]
                else:
                    logger.error(f"No expressions available for {char_name}")
                    continue

            # 瞬きチェック
            is_blinking = False
            if blink_timings:
                is_blinking = self.is_character_blinking(
                    current_time, blink_timings, char_name
                )

            # 口画像選択（瞬きを考慮）
            mouth_img = self.select_mouth_image(intensity, char_imgs, is_blinking)

            bg_h, bg_w = background.shape[:2]
            char_h, char_w = mouth_img.shape[:2]

            # キャラクター設定からサイズ比率を取得
            char_config = self.characters.get(char_name, Characters.ZUNDAMON)
            unified_size_ratio = char_config.size_ratio
            target_height = int(bg_h * unified_size_ratio)
            target_width = int(char_w * target_height / char_h)

            # 位置計算：常にconfig.pyの設定を使用
            x_offset_ratio = char_config.x_offset_ratio
            x = int(bg_w * x_offset_ratio - target_width // 2)

            y = int(bg_h * char_config.y_offset_ratio)

            # サイズ制限
            if target_width > bg_w * 0.8:
                target_width = int(bg_w * 0.8)
                target_height = int(char_h * target_width / char_w)

            mouth_img = cv2.resize(mouth_img, (target_width, target_height))

            margin = 10
            x = max(-target_width // 3, min(x, bg_w - target_width // 3 * 2))
            y = max(margin, min(y, bg_h - target_height - margin))

            # キャラクター合成
            result = self.composite_frame(result, mouth_img, (x, y))

            # アイテム合成
            if character_items and char_name in character_items:
                item_name = character_items[char_name]
                if item_name and item_name != "none":
                    try:
                        result = self.item_manager.composite_item_on_frame(
                            result,
                            item_name,
                            char_name,
                            (x, y),
                            (target_width, target_height),
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to composite item {item_name} for {char_name}: {e}"
                        )

        return result

    def get_japanese_font(self) -> Optional[ImageFont.FreeTypeFont]:
        """日本語フォントを取得（キャッシュ機能付き）"""
        if self._cached_font is not None:
            return self._cached_font

        local_fonts_dir = Paths.get_fonts_dir()

        # 優先順位付きフォントリスト
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
                        # TTF/OTFファイルの場合
                        font = ImageFont.truetype(
                            font_path, self.subtitle_config.font_size
                        )
                        # 日本語文字でテスト
                        try:
                            self._cached_font = font
                            logger.info(f"Successfully loaded font: {font_path}")
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
        """字幕をフレームに描画"""
        if not text.strip():
            return frame

        try:
            # PIL形式に変換
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_image)

            # フォント取得
            font = self.get_japanese_font()
            if font is None:
                logger.warning("No font available")
                return frame

            # テキストサイズ計算
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 背景サイズ計算
            padding_x = self.subtitle_config.padding_x
            padding_top = self.subtitle_config.padding_top
            padding_bottom = self.subtitle_config.padding_bottom
            border_width = self.subtitle_config.border_width
            bg_width = text_width + (padding_x * 2)
            bg_height = text_height + padding_top + padding_bottom

            # 位置計算
            bg_x = (self.resolution[0] - bg_width) // 2
            bg_y = self.resolution[1] - self.subtitle_config.margin_bottom - bg_height

            text_x = bg_x + padding_x
            text_y = bg_y + padding_top

            # RGBA変換
            if pil_image.mode != "RGBA":
                pil_image = pil_image.convert("RGBA")
                draw = ImageDraw.Draw(pil_image)

            # 話者に応じた色設定
            radius = self.subtitle_config.border_radius
            bg_color = self.subtitle_config.background_color
            border_color = self.characters.get(
                speaker, Characters.ZUNDAMON
            ).subtitle_color

            # 背景描画
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
                # フォールバック
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

            # テキスト描画
            outline_width = self.subtitle_config.outline_width
            outline_color = self.subtitle_config.outline_color
            text_color = self.subtitle_config.font_color

            # アウトライン
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text(
                            (text_x + dx, text_y + dy),
                            text,
                            font=font,
                            fill=outline_color,
                        )

            # メインテキスト
            draw.text((text_x, text_y), text, font=font, fill=text_color)

            # BGR形式に戻す
            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        except Exception as e:
            logger.error(f"Subtitle drawing failed: {e}")
            return frame
