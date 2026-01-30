"""
ずんだもん動画生成アプリケーション設定

このパッケージではアプリケーション全体で使用される設定を一元管理します。
"""

from .app import AppConfig, SubtitleConfig, Paths, APP_CONFIG, SUBTITLE_CONFIG

from .content_config.characters import (
    CharacterConfig,
    ExpressionConfig,
    Characters,
    Expressions,
)

from .content_config.content import (
    BackgroundConfig,
    Backgrounds,
)

from .resource_config.defaults import DefaultConversations, UIConfig, UI_CONFIG

__all__ = [
    "AppConfig",
    "CharacterConfig",
    "ExpressionConfig",
    "BackgroundConfig",
    "SubtitleConfig",
    "UIConfig",
    "Characters",
    "Expressions",
    "Backgrounds",
    "DefaultConversations",
    "Paths",
    "APP_CONFIG",
    "SUBTITLE_CONFIG",
    "UI_CONFIG",
]
