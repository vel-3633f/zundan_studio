"""字幕描画関連のMixin"""

import logging
import os
from typing import List, Optional
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from budoux import load_default_japanese_parser

from app.config import SUBTITLE_CONFIG, Characters, Paths

logger = logging.getLogger(__name__)


class SubtitleMixin:
    """字幕描画機能を提供するMixin"""

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

