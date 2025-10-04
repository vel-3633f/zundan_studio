"""
ずんだもん動画生成アプリケーション設定

このパッケージではアプリケーション全体で使用される設定を一元管理します。
"""

# アプリケーション基本設定
from .app import AppConfig, SubtitleConfig, Paths, APP_CONFIG, SUBTITLE_CONFIG

# キャラクター + 表情設定  
from .characters import (
    CharacterConfig, 
    ExpressionConfig, 
    Characters, 
    Expressions
)

# 背景設定
from .content import (
    BackgroundConfig,
    Backgrounds,
)

# デフォルトデータ + UI設定
from .defaults import DefaultConversations, UIConfig, UI_CONFIG

# 後方互換性のため、よく使われるインスタンスをエクスポート
__all__ = [
    # 設定クラス
    "AppConfig",
    "CharacterConfig",
    "ExpressionConfig",
    "BackgroundConfig",
    "SubtitleConfig",
    "UIConfig",

    # データクラス
    "Characters",
    "Expressions",
    "Backgrounds",
    "DefaultConversations",
    "Paths",

    # インスタンス
    "APP_CONFIG",
    "SUBTITLE_CONFIG",
    "UI_CONFIG",
]