from typing import Tuple
from dataclasses import dataclass
import os
from pathlib import Path


@dataclass
class AppConfig:
    """アプリケーション基本設定"""

    title: str = "ずんだもん会話動画生成アプリ"
    description: str = (
        "ずんだもん（右側・緑枠）とゲストキャラクター（左側）の会話動画を作成できます"
    )
    page_icon: str = "🎭"
    layout: str = "wide"

    fps: int = 30
    resolution: Tuple[int, int] = (1280, 720)

    default_speed: float = 1.0
    default_pitch: float = 0.0
    default_intonation: float = 1.0
    default_subtitles: bool = True


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
    max_chars_per_line: int = 25
    border_radius: int = 18


class Paths:
    """パス設定"""

    @staticmethod
    def get_project_root() -> str:
        """プロジェクトルートディレクトリを取得"""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    def get_temp_dir() -> str:
        """一時ファイルディレクトリを取得"""
        return os.path.join(Paths.get_project_root(), "temp")

    @staticmethod
    def get_outputs_dir() -> str:
        """出力ディレクトリを取得"""
        return os.path.join(Paths.get_project_root(), "outputs")


# グローバル設定インスタンス
APP_CONFIG = AppConfig()
SUBTITLE_CONFIG = SubtitleConfig()


PROMPTS_DIR = Path("src/prompts")
SYSTEM_PROMPT_FILE = PROMPTS_DIR / "food_system_template.md"
USER_PROMPT_FILE = PROMPTS_DIR / "food_user_template.md"

TAVILY_SEARCH_RESULTS_COUNT = 3
