import logging
from typing import List, Dict

from app.config import APP_CONFIG, SUBTITLE_CONFIG, Characters

from .video_processor_image_loader import ImageLoaderMixin
from .video_processor_compositor import CompositorMixin
from .video_processor_subtitle import SubtitleMixin
from .video_processor_animation import AnimationMixin

logger = logging.getLogger(__name__)


class VideoProcessor(ImageLoaderMixin, CompositorMixin, SubtitleMixin, AnimationMixin):
    def __init__(self):
        self.fps = APP_CONFIG.fps
        self.resolution = APP_CONFIG.resolution
        self.characters = Characters.get_all()
        self.subtitle_config = SUBTITLE_CONFIG

        self._cached_font = None
        self._resize_cache = {}
        
        # SubtitleMixinで使用するbudouxパーサーを初期化
        from budoux import load_default_japanese_parser
        self._budoux_parser = load_default_japanese_parser()

        self.blink_config = {
            "min_interval": 2.0,
            "max_interval": 6.0,
            "duration": 0.15,
        }
