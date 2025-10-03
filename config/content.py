import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BackgroundConfig:
    """背景設定"""

    name: str
    display_name: str
    emoji: str
    description: str = ""


class Backgrounds:
    """背景定義"""

    _loaded_backgrounds: Dict[str, BackgroundConfig] = {}
    _default_backgrounds = {
        "default": BackgroundConfig(
            name="default",
            display_name="default",
            emoji="",
            description="標準の背景画像",
        )
    }

    @classmethod
    def get_all(cls) -> Dict[str, BackgroundConfig]:
        """全背景設定を取得（デフォルト + 読み込まれた背景）"""
        all_backgrounds = cls._default_backgrounds.copy()
        all_backgrounds.update(cls._loaded_backgrounds)
        return all_backgrounds

    @classmethod
    def get_display_name(cls, name: str) -> str:
        """背景名から表示名を取得"""
        backgrounds = cls.get_all()
        if name in backgrounds:
            bg = backgrounds[name]
            return bg.display_name
        return name

    @classmethod
    def get_supported_extensions(cls) -> set:
        """サポートされる画像拡張子を取得"""
        return {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

    @classmethod
    def is_valid_background(cls, name: str) -> bool:
        """指定された背景名が有効かチェック"""
        return name in cls.get_all()

    @classmethod
    def load_backgrounds_from_names(cls, background_names: List[str]) -> None:
        """背景名のリストから背景設定を動的に作成"""
        cls._loaded_backgrounds = {}

        for bg_name in background_names:
            if bg_name == "default":
                continue  # デフォルトは既にある

            config = BackgroundConfig(
                name=bg_name,
                display_name=bg_name,
                emoji="",
                description=f"背景: {bg_name}",
            )
            cls._loaded_backgrounds[bg_name] = config

        logger.info(
            f"Created {len(cls._loaded_backgrounds)} background configurations from names"
        )
