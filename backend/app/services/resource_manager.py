import logging
import os
import cv2
from typing import Dict, List

logger = logging.getLogger(__name__)


class ResourceManager:
    """リソース管理クラス"""

    def __init__(self, video_processor):
        self.video_processor = video_processor

    def load_character_images(self) -> Dict:
        """キャラクター画像の読み込み"""
        character_images = self.video_processor.load_all_character_images()
        if not character_images:
            logger.error("No character images loaded")
            return None
        return character_images

    def load_backgrounds(self) -> Dict:
        """背景画像の読み込み"""
        backgrounds = self.video_processor.load_backgrounds()
        if not backgrounds:
            logger.error("No background images loaded")
            return None
        return backgrounds

    def generate_blink_timings(self, total_duration: float) -> List:
        """瞬きタイミングの生成"""
        blink_timings = []
        for char_name in self.video_processor.characters.keys():
            char_blink_timings = self.video_processor.generate_blink_timings(
                total_duration, char_name
            )
            blink_timings.extend(char_blink_timings)
        return blink_timings

    def validate_resources(self, character_images: Dict, backgrounds: Dict) -> bool:
        """リソースの検証"""
        return character_images is not None and backgrounds is not None

    def load_item_images(self) -> Dict:
        """教育アイテム画像を動的に読み込む

        assets/items/ 配下の全てのPNG画像を再帰的に読み込みます。
        画像ファイル名（拡張子なし）がアイテムIDとして使用されます。

        Returns:
            Dict[str, np.ndarray]: アイテムID -> 画像データの辞書
        """
        items = {}
        item_base_dir = "assets/items"

        if not os.path.exists(item_base_dir):
            logger.warning(f"Item directory not found: {item_base_dir}")
            return items

        # assets/items/ 配下の全てのPNGファイルを再帰的に検索
        for root, dirs, files in os.walk(item_base_dir):
            for file in files:
                if file.lower().endswith('.png'):
                    # ファイル名（拡張子なし）をアイテムIDとして使用
                    item_id = os.path.splitext(file)[0]
                    file_path = os.path.join(root, file)

                    # 画像を読み込み
                    img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
                    if img is not None:
                        items[item_id] = img
                        # 相対パスを表示
                        rel_path = os.path.relpath(file_path, item_base_dir)
                        logger.info(f"Loaded item image: '{item_id}' from items/{rel_path}")
                    else:
                        logger.warning(f"Failed to load item image: {file_path}")

        logger.info(f"Total item images loaded: {len(items)} from {item_base_dir}")
        if len(items) == 0:
            logger.info(f"No item images found. Place PNG files in {item_base_dir}/ to use them.")

        return items
