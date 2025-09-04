"""
ずんだもん動画生成アプリケーション設定

このファイルではアプリケーション全体で使用される設定を一元管理します。
"""

from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import os

# ============================
# アプリケーション基本設定
# ============================


@dataclass
class AppConfig:
    """アプリケーション基本設定"""

    title: str = "🎭 ずんだもん会話動画生成アプリ"
    description: str = (
        "ずんだもん（右側・緑枠）とゲストキャラクター（左側）の会話動画を作成できます"
    )
    page_icon: str = "🎭"
    layout: str = "wide"

    # 動画設定
    fps: int = 30
    resolution: Tuple[int, int] = (1280, 720)

    # 音声パラメータデフォルト値
    default_speed: float = 1.0
    default_pitch: float = 0.0
    default_intonation: float = 1.0
    default_subtitles: bool = True


# ============================
# キャラクター設定
# ============================


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


class Characters:
    """キャラクター定義"""

    ZUNDAMON = CharacterConfig(
        name="zundamon",
        speaker_id=3,
        position="right",
        subtitle_color=(34, 139, 34),  # 緑
        size_ratio=2.2,
        x_offset_ratio=0.75,
        y_offset_ratio=0.05,
        display_name="ずんだもん",
        emoji="🟢",
        display_position="right",
    )

    METAN = CharacterConfig(
        name="metan",
        speaker_id=2,
        position="left",
        subtitle_color=(255, 105, 180),  # ピンク
        size_ratio=2.2,
        x_offset_ratio=0.25,
        y_offset_ratio=0.2,
        display_name="四国めたん",
        emoji="🩷",
        display_position="left",
    )

    TSUMUGI = CharacterConfig(
        name="tsumugi",
        speaker_id=8,
        position="left",
        subtitle_color=(255, 215, 0),  # 黄色
        size_ratio=2.2,
        x_offset_ratio=0.25,
        y_offset_ratio=0.2,
        display_name="春日部つむぎ",
        emoji="💛",
        display_position="left",
    )

    @classmethod
    def get_all(cls) -> Dict[str, CharacterConfig]:
        """全キャラクター設定を取得"""
        return {"zundamon": cls.ZUNDAMON, "metan": cls.METAN, "tsumugi": cls.TSUMUGI}

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


# ============================
# 背景設定
# ============================


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


# ============================
# 字幕設定
# ============================


@dataclass
class SubtitleConfig:
    """字幕設定"""

    font_size: int = 38
    font_color: Tuple[int, int, int] = (50, 50, 50)
    outline_color: Tuple[int, int, int] = (255, 255, 255)
    outline_width: int = 2
    background_color: Tuple[int, int, int, int] = (255, 255, 255, 245)
    border_width: int = 5
    padding_x: int = 18
    padding_top: int = 8
    padding_bottom: int = 21
    margin_bottom: int = 50
    max_chars_per_line: int = 30
    border_radius: int = 18


# ============================
# パス設定
# ============================


class Paths:
    """パス設定"""

    @staticmethod
    def get_project_root() -> str:
        """プロジェクトルートディレクトリを取得"""
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_assets_dir() -> str:
        """アセットディレクトリを取得"""
        return os.path.join(Paths.get_project_root(), "assets")

    @staticmethod
    def get_backgrounds_dir() -> str:
        """背景画像ディレクトリを取得"""
        return os.path.join(Paths.get_assets_dir(), "backgrounds")

    @staticmethod
    def get_character_dir(character_name: str) -> str:
        """キャラクター画像ディレクトリを取得"""
        return os.path.join(Paths.get_assets_dir(), character_name)

    @staticmethod
    def get_fonts_dir() -> str:
        """フォントディレクトリを取得"""
        return os.path.join(Paths.get_assets_dir(), "fonts")

    @staticmethod
    def get_temp_dir() -> str:
        """一時ファイルディレクトリを取得"""
        return os.path.join(Paths.get_project_root(), "temp")

    @staticmethod
    def get_outputs_dir() -> str:
        """出力ディレクトリを取得"""
        return os.path.join(Paths.get_project_root(), "outputs")


# ============================
# デフォルト会話データ
# ============================


class DefaultConversations:
    """デフォルト会話データ"""

    @staticmethod
    def get_sample_conversation() -> List[Dict[str, str]]:
        """サンプル会話を取得"""
        return [
            {
                "speaker": "zundamon",
                "text": "こんにちはなのだ！今日もいい天気なのだ！",
                "background": "blue_sky",
                "expression": "happy",
                "visible_characters": ["zundamon", "metan"],
            },
            {
                "speaker": "metan",
                "text": "こんにちは〜！本当にいい天気だっぺ〜",
                "background": "blue_sky",
                "expression": "normal",
                "visible_characters": ["zundamon", "metan"],
            },
            {
                "speaker": "zundamon",
                "text": "今日のゲストを紹介するのだ！",
                "background": "default",
                "expression": "happy",
                "visible_characters": ["zundamon"],
            },
            {
                "speaker": "tsumugi",
                "text": "春日部つむぎです。よろしくお願いします！",
                "background": "sakura",
                "expression": "normal",
                "visible_characters": ["zundamon", "tsumugi"],
            },
            {
                "speaker": "zundamon",
                "text": "今日は何をするのだ？",
                "background": "default",
                "expression": "thinking",
                "visible_characters": ["zundamon", "tsumugi"],
            },
            {
                "speaker": "tsumugi",
                "text": "一緒にお散歩でもしませんか？",
                "background": "sunset",
                "expression": "happy",
                "visible_characters": ["zundamon", "tsumugi"],
            },
        ]

    @staticmethod
    def get_reset_conversation() -> List[Dict[str, str]]:
        """リセット用会話を取得"""
        return [
            {
                "speaker": "zundamon",
                "text": "こんにちはなのだ！",
                "background": "default",
                "expression": "normal",
                "visible_characters": ["zundamon", "metan"],
            },
            {
                "speaker": "metan",
                "text": "こんにちは〜だっぺ！",
                "background": "blue_sky",
                "expression": "normal",
                "visible_characters": ["zundamon", "metan"],
            },
        ]


# ============================
# UI設定
# ============================


class UIConfig:
    """UI設定"""

    # スライダー設定
    speed_range: Tuple[float, float, float, float] = (
        0.5,
        2.0,
        1.0,
        0.1,
    )  # min, max, default, step
    pitch_range: Tuple[float, float, float, float] = (-0.15, 0.15, 0.0, 0.01)
    intonation_range: Tuple[float, float, float, float] = (0.0, 2.0, 1.0, 0.1)

    # テキストエリア設定
    text_area_height: int = 80

    # カラム設定
    main_columns: List[int] = [3, 1]
    input_columns: List[int] = [
        1,
        3,
        1,
        1,
        2,
        1,
    ]  # 話者、テキスト、背景、表情、表示キャラ、削除
    button_columns: List[int] = [1, 1, 1]
    generate_columns: List[int] = [1, 2, 1]


# ============================
# 設定インスタンス
# ============================

# グローバル設定インスタンス
APP_CONFIG = AppConfig()
SUBTITLE_CONFIG = SubtitleConfig()
UI_CONFIG = UIConfig()
