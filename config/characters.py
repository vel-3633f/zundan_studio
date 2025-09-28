"""
キャラクター + 表情設定
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ExpressionConfig:
    """表情設定"""

    name: str
    display_name: str
    emoji: str
    description: str = ""


@dataclass
class CharacterConfig:
    """キャラクター設定"""

    name: str
    speaker_id: int
    position: str
    subtitle_color: Tuple[int, int, int]
    size_ratio: float
    x_offset_ratio: float
    y_offset_ratio: float
    display_name: str
    emoji: str
    display_position: str
    default_speed: float = 1.0
    default_pitch: float = 0.0
    default_intonation: float = 1.0


class Characters:
    """キャラクター定義"""

    ZUNDAMON = CharacterConfig(
        name="zundamon",
        speaker_id=3,
        position="right",
        subtitle_color=(34, 139, 34),  # 緑
        size_ratio=1.5,
        x_offset_ratio=0.78,
        y_offset_ratio=0.05,
        display_name="ずんだもん",
        emoji="🟢",
        display_position="right",
        default_speed=1.2,  # 元気で明るいキャラなので少し速め
        default_pitch=0.0,
        default_intonation=1.4,  # 抑揚を強めに
    )

    METAN = CharacterConfig(
        name="metan",
        speaker_id=2,
        position="left",
        subtitle_color=(255, 105, 180),  # ピンク
        size_ratio=1.5,
        x_offset_ratio=0.25,
        y_offset_ratio=0.2,
        display_name="四国めたん",
        emoji="🩷",
        display_position="left",
        default_speed=1.0,  # 優しい感じなので標準的な速度
        default_pitch=0.0,
        default_intonation=1.2,  # 抑揚は控えめ
    )

    TSUMUGI = CharacterConfig(
        name="tsumugi",
        speaker_id=8,
        position="left",
        subtitle_color=(255, 215, 0),  # 黄色
        size_ratio=1.5,
        x_offset_ratio=0.25,
        y_offset_ratio=0.2,
        display_name="春日部つむぎ",
        emoji="💛",
        display_position="left",
        default_speed=1,  # 上品で落ち着いた感じなので少し遅め
        default_pitch=0.0,
        default_intonation=1.2,  # 適度な抑揚
    )

    NARRATOR = CharacterConfig(
        name="narrator",
        speaker_id=13,  # VOICEVOXナレーション用
        position="narrator",  # ナレーター専用ポジション
        subtitle_color=(100, 100, 100),  # ダークグレー
        size_ratio=0.0,  # キャラクター画像は表示しない
        x_offset_ratio=0.5,
        y_offset_ratio=0.5,
        display_name="ナレーター",
        emoji="🎙️",
        display_position="ナレーション",
        default_speed=1,  # 落ち着いた感じで遅め
        default_pitch=0.0,
        default_intonation=1,  # 抑揚は控えめ
    )

    @classmethod
    def get_all(cls) -> Dict[str, CharacterConfig]:
        """全キャラクター設定を取得"""
        return {
            "zundamon": cls.ZUNDAMON,
            "metan": cls.METAN,
            "tsumugi": cls.TSUMUGI,
            "narrator": cls.NARRATOR,
        }

    @classmethod
    def get_display_options(cls) -> List[Tuple[str, str]]:
        """UI表示用のキャラクター選択肢を取得"""
        return [
            (
                "zundamon",
                f"{cls.ZUNDAMON.emoji} {cls.ZUNDAMON.display_name} ({cls.ZUNDAMON.display_position})",
            ),
            (
                "metan",
                f"{cls.METAN.emoji} {cls.METAN.display_name} ({cls.METAN.display_position})",
            ),
            (
                "tsumugi",
                f"{cls.TSUMUGI.emoji} {cls.TSUMUGI.display_name} ({cls.TSUMUGI.display_position})",
            ),
            (
                "narrator",
                f"{cls.NARRATOR.emoji} {cls.NARRATOR.display_name} ({cls.NARRATOR.display_position})",
            ),
        ]


class Expressions:
    """表情定義"""

    NORMAL = ExpressionConfig(
        name="normal", display_name="通常", emoji="😊", description="通常の表情"
    )

    HAPPY = ExpressionConfig(
        name="happy", display_name="喜び", emoji="😄", description="嬉しい表情"
    )

    SAD = ExpressionConfig(
        name="sad", display_name="悲しみ", emoji="😢", description="悲しい表情"
    )

    ANGRY = ExpressionConfig(
        name="angry", display_name="怒り", emoji="😠", description="怒った表情"
    )

    SURPRISED = ExpressionConfig(
        name="surprised", display_name="驚き", emoji="😮", description="驚いた表情"
    )

    THINKING = ExpressionConfig(
        name="thinking", display_name="考え中", emoji="🤔", description="考えている表情"
    )

    WORRIED = ExpressionConfig(
        name="worried", display_name="心配", emoji="😟", description="心配している表情"
    )

    EXCITED = ExpressionConfig(
        name="excited", display_name="興奮", emoji="🤩", description="興奮している表情"
    )

    SICK = ExpressionConfig(
        name="sick", display_name="体調不良", emoji="🤢", description="具合が悪い表情"
    )

    SERIOUS = ExpressionConfig(
        name="serious", display_name="真剣", emoji="😤", description="真剣な表情"
    )

    @classmethod
    def get_all(cls) -> Dict[str, ExpressionConfig]:
        """全表情設定を取得"""
        return {
            "normal": cls.NORMAL,
            "happy": cls.HAPPY,
            "sad": cls.SAD,
            "angry": cls.ANGRY,
            "surprised": cls.SURPRISED,
            "thinking": cls.THINKING,
            "worried": cls.WORRIED,
            "excited": cls.EXCITED,
            "sick": cls.SICK,
            "serious": cls.SERIOUS,
        }

    @classmethod
    def get_display_name(cls, name: str) -> str:
        """表情名から表示名を取得"""
        expressions = cls.get_all()
        if name in expressions:
            expr = expressions[name]
            return f"{expr.emoji} {expr.display_name}"
        return f"😊 {name}"

    @classmethod
    def get_available_names(cls) -> List[str]:
        """利用可能な表情名のリストを取得"""
        return list(cls.get_all().keys())
