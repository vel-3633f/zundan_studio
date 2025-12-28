"""画像読み込み関連のMixin"""

import os
import logging
from functools import lru_cache
from typing import List, Dict
import cv2
import numpy as np

from app.config import Characters, Backgrounds, Expressions, Paths

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


class ImageLoaderMixin:
    """画像読み込み機能を提供するMixin"""

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

