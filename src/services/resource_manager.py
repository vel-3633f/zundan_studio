import logging
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
