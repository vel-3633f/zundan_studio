"""
背景 + アイテム設定
"""

import json
import os
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
            description="標準の背景画像"
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
                description=f"背景: {bg_name}"
            )
            cls._loaded_backgrounds[bg_name] = config

        logger.info(f"Created {len(cls._loaded_backgrounds)} background configurations from names")


@dataclass
class ItemConfig:
    """アイテム設定"""

    name: str
    display_name: str
    category: str
    emoji: str = "📦"
    # キャラクターごとの位置調整（キャラクター名をキー）
    positions: Dict[str, Tuple[float, float]] = None  # (x_ratio, y_ratio)
    # キャラクターごとのサイズ調整
    sizes: Dict[str, float] = None  # size_ratio
    # アイテム固有のサイズ比率（キャラクター共通）
    base_size: float = 0.15
    # アスペクト比を維持するか
    maintain_aspect_ratio: bool = True
    # 最大幅・高さ制限（背景サイズの比率）
    max_width_ratio: float = 0.3
    max_height_ratio: float = 0.3
    description: str = ""

    def __post_init__(self):
        if self.positions is None:
            # デフォルト位置（キャラクターの手元あたり）
            self.positions = {
                "zundamon": (0.1, 0.35),  # 右手
                "metan": (0.9, 0.35),  # 左手
                "tsumugi": (0.9, 0.35),  # 左手
            }
        if self.sizes is None:
            # デフォルトサイズ（キャラクター別の微調整）
            self.sizes = {
                "zundamon": 1.0,  # base_sizeに対する倍率
                "metan": 1.0,
                "tsumugi": 1.0,
            }

    def get_size_for_character(self, character_name: str) -> float:
        """キャラクター用の最終サイズを取得"""
        char_multiplier = self.sizes.get(character_name, 1.0)
        return self.base_size * char_multiplier


class Items:
    """アイテム設定管理クラス"""

    # 食べ物カテゴリのアイテム
    CHOCOLATE_BAR = ItemConfig(
        name="chocolate_bar",
        display_name="チョコレートバー",
        category="food",
        emoji="🍫",
        description="チョコレートバー",
        positions={
            "zundamon": (0.1, 0.35),  # 右手
            "metan": (0.9, 0.35),  # 左手
            "tsumugi": (0.9, 0.35),  # 左手
        },
        base_size=0.12
    )

    @classmethod
    def get_all(cls) -> Dict[str, ItemConfig]:
        """すべてのアイテム設定を取得"""
        items = {}
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, ItemConfig):
                items[attr_value.name] = attr_value
        return items

    @classmethod
    def get_by_category(cls, category: str) -> Dict[str, ItemConfig]:
        """カテゴリ別でアイテムを取得"""
        all_items = cls.get_all()
        return {
            name: item for name, item in all_items.items() if item.category == category
        }

    @classmethod
    def get_categories(cls) -> List[str]:
        """利用可能なカテゴリリストを取得"""
        all_items = cls.get_all()
        categories = list(set(item.category for item in all_items.values()))
        return sorted(categories)

    @classmethod
    def get_item(cls, name: str) -> ItemConfig:
        """特定のアイテム設定を取得"""
        all_items = cls.get_all()
        return all_items.get(name, None)
