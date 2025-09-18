"""
背景 + アイテム設定
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class BackgroundConfig:
    """背景設定"""

    name: str
    display_name: str
    emoji: str
    description: str = ""


class Backgrounds:
    """背景定義"""

    DEFAULT = BackgroundConfig(
        name="default",
        display_name="デフォルト",
        emoji="🖼️",
        description="標準の背景画像",
    )

    BLUE_SKY = BackgroundConfig(
        name="blue_sky", display_name="青空", emoji="🌤️", description="青い空の背景"
    )

    SUNSET = BackgroundConfig(
        name="sunset", display_name="夕日", emoji="🌅", description="夕焼けの背景"
    )

    NIGHT = BackgroundConfig(
        name="night", display_name="夜空", emoji="🌃", description="夜の背景"
    )

    FOREST = BackgroundConfig(
        name="forest", display_name="森", emoji="🌲", description="森の背景"
    )

    OCEAN = BackgroundConfig(
        name="ocean", display_name="海", emoji="🌊", description="海の背景"
    )

    SAKURA = BackgroundConfig(
        name="sakura", display_name="桜", emoji="🌸", description="桜の背景"
    )

    SNOW = BackgroundConfig(
        name="snow", display_name="雪", emoji="❄️", description="雪の背景"
    )

    HOSPITAL_ROOM = BackgroundConfig(
        name="hospital_room", display_name="病室", emoji="🏥", description="病院の病室"
    )

    SUPERMARKET_AISLE = BackgroundConfig(
        name="supermarket_aisle", display_name="スーパー", emoji="🛒", description="スーパーマーケットの通路"
    )

    LIVING_ROOM = BackgroundConfig(
        name="living_room", display_name="リビング", emoji="🛋️", description="リビングルーム"
    )

    BEDROOM = BackgroundConfig(
        name="bedroom", display_name="寝室", emoji="🛏️", description="ベッドルーム"
    )

    LABORATORY = BackgroundConfig(
        name="laboratory", display_name="研究室", emoji="🧪", description="実験室・研究室"
    )

    @classmethod
    def get_all(cls) -> Dict[str, BackgroundConfig]:
        """全背景設定を取得"""
        return {
            "default": cls.DEFAULT,
            "blue_sky": cls.BLUE_SKY,
            "sunset": cls.SUNSET,
            "night": cls.NIGHT,
            "forest": cls.FOREST,
            "ocean": cls.OCEAN,
            "sakura": cls.SAKURA,
            "snow": cls.SNOW,
            "hospital_room": cls.HOSPITAL_ROOM,
            "supermarket_aisle": cls.SUPERMARKET_AISLE,
            "living_room": cls.LIVING_ROOM,
            "bedroom": cls.BEDROOM,
            "laboratory": cls.LABORATORY,
        }

    @classmethod
    def get_display_name(cls, name: str) -> str:
        """背景名から表示名を取得"""
        backgrounds = cls.get_all()
        if name in backgrounds:
            bg = backgrounds[name]
            return f"{bg.emoji} {bg.display_name}"
        return f"🖼️ {name}"

    @classmethod
    def get_supported_extensions(cls) -> set:
        """サポートされる画像拡張子を取得"""
        return {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


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
