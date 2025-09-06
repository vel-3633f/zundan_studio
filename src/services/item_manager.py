import os
import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from config import Items, Paths, ItemConfig

logger = logging.getLogger(__name__)


class ItemManager:
    """アイテム管理クラス"""

    def __init__(self):
        self.item_cache: Dict[str, np.ndarray] = {}
        self.available_items: Dict[str, ItemConfig] = Items.get_all()

    def load_item_image(self, item_name: str) -> Optional[np.ndarray]:
        """アイテム画像を読み込み"""
        if item_name in self.item_cache:
            return self.item_cache[item_name]

        item_config = Items.get_item(item_name)
        if not item_config:
            logger.warning(f"Item config not found for: {item_name}")
            return None

        item_path = Paths.get_item_file_path(item_config.category, item_name)

        if not os.path.exists(item_path):
            logger.warning(f"Item image not found: {item_path}")
            return None

        try:
            img = cv2.imread(item_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                self.item_cache[item_name] = img
                logger.info(f"Loaded item image: {item_name}")
                return img
            else:
                logger.error(f"Failed to load item image: {item_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading item image {item_path}: {e}")
            return None

    def get_item_position_and_size(
        self,
        item_name: str,
        character_name: str,
        character_position: Tuple[int, int],
        character_size: Tuple[int, int],
        background_size: Tuple[int, int],
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """アイテムの位置とサイズを計算"""
        item_config = Items.get_item(item_name)
        if not item_config:
            return (0, 0), (0, 0)

        bg_w, bg_h = background_size
        char_x, char_y = character_position
        char_w, char_h = character_size

        # キャラクター固有の位置設定を取得
        if character_name in item_config.positions:
            pos_x_ratio, pos_y_ratio = item_config.positions[character_name]
        else:
            # デフォルト位置
            pos_x_ratio, pos_y_ratio = 0.5, 0.5

        # アイテムの位置を計算（キャラクターの相対位置）
        item_x = int(char_x + char_w * pos_x_ratio)
        item_y = int(char_y + char_h * pos_y_ratio)

        # アイテムのサイズを計算（新しい設定を使用）
        final_size = item_config.get_size_for_character(character_name)
        
        # デフォルトは正方形
        item_width = int(bg_h * final_size)
        item_height = int(bg_h * final_size)
        
        # 最大サイズ制限をチェック
        max_width = int(bg_w * item_config.max_width_ratio)
        max_height = int(bg_h * item_config.max_height_ratio)
        item_width = min(item_width, max_width)
        item_height = min(item_height, max_height)

        return (item_x, item_y), (item_width, item_height)

    def composite_item_on_frame(
        self,
        frame: np.ndarray,
        item_name: str,
        character_name: str,
        character_position: Tuple[int, int],
        character_size: Tuple[int, int],
    ) -> np.ndarray:
        """フレームにアイテムを合成"""
        if not item_name or item_name == "none":
            return frame

        item_img = self.load_item_image(item_name)
        if item_img is None:
            return frame

        bg_h, bg_w = frame.shape[:2]
        background_size = (bg_w, bg_h)

        # アイテムの位置とサイズを計算（アスペクト比考慮）
        item_config = Items.get_item(item_name)
        if item_config and item_config.maintain_aspect_ratio:
            # アスペクト比維持の場合、元画像サイズを使用
            original_h, original_w = item_img.shape[:2]
            aspect_ratio = original_w / original_h if original_h > 0 else 1.0
            
            # 基準サイズから実際のサイズを計算
            final_size = item_config.get_size_for_character(character_name)
            base_height = int(bg_h * final_size)
            base_width = int(base_height * aspect_ratio)
            
            # 最大サイズ制限をチェック
            max_width = int(bg_w * item_config.max_width_ratio)
            max_height = int(bg_h * item_config.max_height_ratio)
            
            if base_width > max_width:
                item_width = max_width
                item_height = int(item_width / aspect_ratio)
            elif base_height > max_height:
                item_height = max_height
                item_width = int(item_height * aspect_ratio)
            else:
                item_width = base_width
                item_height = base_height
                
            # 位置計算
            bg_w, bg_h = background_size
            char_x, char_y = character_position
            char_w, char_h = character_size
            
            if character_name in item_config.positions:
                pos_x_ratio, pos_y_ratio = item_config.positions[character_name]
            else:
                pos_x_ratio, pos_y_ratio = 0.5, 0.5
                
            item_x = int(char_x + char_w * pos_x_ratio)
            item_y = int(char_y + char_h * pos_y_ratio)
        else:
            # 従来の方法（正方形）
            (item_x, item_y), (item_width, item_height) = self.get_item_position_and_size(
                item_name,
                character_name,
                character_position,
                character_size,
                background_size,
            )

        # アイテム画像をリサイズ
        try:
            resized_item = cv2.resize(item_img, (item_width, item_height))
        except Exception as e:
            logger.error(f"Error resizing item {item_name}: {e}")
            return frame

        # アイテムを合成
        return self._composite_item_with_alpha(frame, resized_item, (item_x, item_y))

    def _composite_item_with_alpha(
        self, background: np.ndarray, item: np.ndarray, position: Tuple[int, int]
    ) -> np.ndarray:
        """アルファチャンネルを考慮したアイテム合成"""
        x, y = position
        result = background.copy()

        item_h, item_w = item.shape[:2]
        bg_h, bg_w = background.shape[:2]

        # 境界チェック
        if x < 0:
            item = item[:, -x:]
            item_w += x
            x = 0
        if y < 0:
            item = item[-y:, :]
            item_h += y
            y = 0
        if x + item_w > bg_w:
            item_w = bg_w - x
            if item_w > 0:
                item = item[:, :item_w]
        if y + item_h > bg_h:
            item_h = bg_h - y
            if item_h > 0:
                item = item[:item_h, :]

        # 有効な領域がない場合は元の画像を返す
        if item_w <= 0 or item_h <= 0:
            return result

        try:
            if item.shape[2] == 4:  # アルファチャンネル付き
                item_rgb = item[:, :, :3]
                item_alpha = item[:, :, 3] / 255.0
                item_alpha_expanded = item_alpha[:, :, np.newaxis]

                for c in range(3):
                    result[y : y + item_h, x : x + item_w, c] = (
                        item_alpha_expanded[:, :, 0] * item_rgb[:, :, c]
                        + (1 - item_alpha_expanded[:, :, 0])
                        * background[y : y + item_h, x : x + item_w, c]
                    )
            else:  # アルファチャンネルなし
                result[y : y + item_h, x : x + item_w] = item

        except Exception as e:
            logger.error(f"Error compositing item: {e}")

        return result

    def get_available_items(self) -> Dict[str, ItemConfig]:
        """利用可能なアイテム一覧を取得"""
        return self.available_items

    def get_items_by_category(self, category: str) -> Dict[str, ItemConfig]:
        """カテゴリ別アイテム一覧を取得"""
        return Items.get_by_category(category)

    def get_categories(self) -> List[str]:
        """利用可能なカテゴリ一覧を取得"""
        return Items.get_categories()

    def is_item_available(self, item_name: str) -> bool:
        """アイテムが利用可能かチェック"""
        if not item_name or item_name == "none":
            return True

        item_config = Items.get_item(item_name)
        if not item_config:
            return False

        item_path = Paths.get_item_file_path(item_config.category, item_name)
        return os.path.exists(item_path)
