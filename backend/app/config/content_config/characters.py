"""
キャラクター + 表情設定
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ExpressionConfig:
    """表情設定"""

    name: str
    display_name: str
    emoji: str
    description: str = ""


@dataclass
class ExpressionVoiceConfig:
    speed: float
    pitch: float
    intonation: float = 1.0


ZUNDAMON_EXPRESSION_VOICE_MAP: Dict[str, ExpressionVoiceConfig] = {
    "excited": ExpressionVoiceConfig(speed=1.3, pitch=0.05, intonation=1.4),
    "angry": ExpressionVoiceConfig(speed=1.25, pitch=0.02, intonation=1.3),
    "normal": ExpressionVoiceConfig(speed=1.2, pitch=0.01, intonation=1.4),
    "happy": ExpressionVoiceConfig(speed=1.25, pitch=0.05, intonation=1.4),
    "surprised": ExpressionVoiceConfig(speed=1.25, pitch=0.05, intonation=1.3),
    "thinking": ExpressionVoiceConfig(speed=1.1, pitch=0.01, intonation=1.2),
    "sad": ExpressionVoiceConfig(speed=1.15, pitch=0.01, intonation=1.1),
    "worried": ExpressionVoiceConfig(speed=1.15, pitch=0.01, intonation=1.2),
    "sick": ExpressionVoiceConfig(speed=1.15, pitch=0.01, intonation=1.1),
}


METAN_EXPRESSION_VOICE_MAP: Dict[str, ExpressionVoiceConfig] = {
    "excited": ExpressionVoiceConfig(speed=1.25, pitch=0.03, intonation=1.3),
    "angry": ExpressionVoiceConfig(speed=1.25, pitch=0.02, intonation=1.3),
    "normal": ExpressionVoiceConfig(speed=1.25, pitch=0.01, intonation=1.2),
    "happy": ExpressionVoiceConfig(speed=1.25, pitch=0.02, intonation=1.3),
    "surprised": ExpressionVoiceConfig(speed=1.3, pitch=0.1, intonation=1.3),
    "thinking": ExpressionVoiceConfig(speed=1.2, pitch=0.01, intonation=1.1),
    "sad": ExpressionVoiceConfig(speed=1.2, pitch=0.01, intonation=1.1),
    "worried": ExpressionVoiceConfig(speed=1.3, pitch=0.02, intonation=1.2),
    "sick": ExpressionVoiceConfig(speed=1.15, pitch=0.01, intonation=1.1),
}


TSUMUGI_EXPRESSION_VOICE_MAP: Dict[str, ExpressionVoiceConfig] = {
    "excited": ExpressionVoiceConfig(speed=1.25, pitch=0.01, intonation=1.3),
    "angry": ExpressionVoiceConfig(speed=1.25, pitch=0.01, intonation=1.3),
    "normal": ExpressionVoiceConfig(speed=1.25, pitch=0.01, intonation=1.2),
    "happy": ExpressionVoiceConfig(speed=1.25, pitch=0.01, intonation=1.3),
    "surprised": ExpressionVoiceConfig(speed=1.25, pitch=0.01, intonation=1.3),
    "thinking": ExpressionVoiceConfig(speed=1.15, pitch=0.01, intonation=1.1),
    "sad": ExpressionVoiceConfig(speed=1.15, pitch=0.01, intonation=1.1),
    "worried": ExpressionVoiceConfig(speed=1.25, pitch=0.01, intonation=1.2),
    "sick": ExpressionVoiceConfig(speed=1.15, pitch=0.01, intonation=1.1),
}


NARRATOR_EXPRESSION_VOICE_MAP: Dict[str, ExpressionVoiceConfig] = {
    "normal": ExpressionVoiceConfig(speed=1.15, pitch=0.01, intonation=1.2),
    "excited": ExpressionVoiceConfig(speed=1.25, pitch=0.05, intonation=1.4),
    "thinking": ExpressionVoiceConfig(speed=1.1, pitch=0.01, intonation=1.1),
    "sad": ExpressionVoiceConfig(speed=1.1, pitch=0.01, intonation=1.1),
}


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
    expression_voice_map: Dict[str, ExpressionVoiceConfig] = field(default_factory=dict)


class Characters:
    """キャラクター定義"""

    ZUNDAMON = CharacterConfig(
        name="zundamon",
        speaker_id=3,
        position="right",
        subtitle_color=(34, 139, 34),
        size_ratio=1.5,
        x_offset_ratio=0.78,
        y_offset_ratio=0.05,
        display_name="ずんだもん",
        emoji="🟢",
        display_position="right",
        default_speed=1.2,
        default_pitch=0.0,
        default_intonation=1.5,
        expression_voice_map=ZUNDAMON_EXPRESSION_VOICE_MAP,
    )

    METAN = CharacterConfig(
        name="metan",
        speaker_id=2,
        position="left",
        subtitle_color=(255, 105, 180),
        size_ratio=1.5,
        x_offset_ratio=0.25,
        y_offset_ratio=0.2,
        display_name="四国めたん",
        emoji="🩷",
        display_position="left",
        default_speed=1.0,
        default_pitch=0.0,
        default_intonation=1.2,
        expression_voice_map=METAN_EXPRESSION_VOICE_MAP,
    )

    TSUMUGI = CharacterConfig(
        name="tsumugi",
        speaker_id=8,
        position="left",
        subtitle_color=(255, 215, 0),
        size_ratio=1.5,
        x_offset_ratio=0.25,
        y_offset_ratio=0.2,
        display_name="春日部つむぎ",
        emoji="💛",
        display_position="left",
        default_speed=1,
        default_pitch=0.0,
        default_intonation=1.2,
        expression_voice_map=TSUMUGI_EXPRESSION_VOICE_MAP,
    )

    NARRATOR = CharacterConfig(
        name="narrator",
        speaker_id=13,
        position="narrator",
        subtitle_color=(100, 100, 100),
        size_ratio=0.0,
        x_offset_ratio=0.5,
        y_offset_ratio=0.5,
        display_name="ナレーター",
        emoji="🎙️",
        display_position="ナレーション",
        default_speed=1,
        default_pitch=0.0,
        default_intonation=1,
        expression_voice_map=NARRATOR_EXPRESSION_VOICE_MAP,
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
