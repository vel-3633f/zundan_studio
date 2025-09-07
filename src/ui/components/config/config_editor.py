import streamlit as st
import json
import os
import sys
from typing import Dict, Any

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import APP_CONFIG, SUBTITLE_CONFIG, UI_CONFIG, Characters


class ConfigEditor:
    """設定編集クラス"""

    CONFIG_FILE = "temp/user_config.json"

    def __init__(self):
        self.ensure_config_file()

    def ensure_config_file(self):
        """設定ファイルの初期化"""
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        if not os.path.exists(self.CONFIG_FILE):
            self.save_default_config()

    def load_user_config(self) -> Dict[str, Any]:
        """ユーザー設定を読み込み"""
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_config()

    def save_user_config(self, config: Dict[str, Any]):
        """ユーザー設定を保存"""
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を取得"""
        return {
            "app": {
                "fps": APP_CONFIG.fps,
                "resolution": list(APP_CONFIG.resolution),
                "default_speed": APP_CONFIG.default_speed,
                "default_pitch": APP_CONFIG.default_pitch,
                "default_intonation": APP_CONFIG.default_intonation,
                "default_subtitles": APP_CONFIG.default_subtitles,
            },
            "subtitle": {
                "font_size": SUBTITLE_CONFIG.font_size,
                "font_color": list(SUBTITLE_CONFIG.font_color),
                "outline_color": list(SUBTITLE_CONFIG.outline_color),
                "outline_width": SUBTITLE_CONFIG.outline_width,
                "background_color": list(SUBTITLE_CONFIG.background_color),
                "border_width": SUBTITLE_CONFIG.border_width,
                "padding_x": SUBTITLE_CONFIG.padding_x,
                "padding_top": SUBTITLE_CONFIG.padding_top,
                "padding_bottom": SUBTITLE_CONFIG.padding_bottom,
                "margin_bottom": SUBTITLE_CONFIG.margin_bottom,
                "max_chars_per_line": SUBTITLE_CONFIG.max_chars_per_line,
                "border_radius": SUBTITLE_CONFIG.border_radius,
            },
            "ui": {
                "speed_range": list(UI_CONFIG.speed_range),
                "pitch_range": list(UI_CONFIG.pitch_range),
                "intonation_range": list(UI_CONFIG.intonation_range),
                "text_area_height": UI_CONFIG.text_area_height,
            },
            "characters": {
                "zundamon": {
                    "size_ratio": Characters.ZUNDAMON.size_ratio,
                    "x_offset_ratio": Characters.ZUNDAMON.x_offset_ratio,
                    "y_offset_ratio": Characters.ZUNDAMON.y_offset_ratio,
                    "subtitle_color": list(Characters.ZUNDAMON.subtitle_color),
                }
            },
        }

    def save_default_config(self):
        """デフォルト設定をファイルに保存"""
        self.save_user_config(self.get_default_config())

    def apply_config_to_session(self, config: Dict[str, Any]):
        """設定をセッションに適用（実行時のみ有効）"""
        # セッション状態に設定を保存
        if "user_config" not in st.session_state:
            st.session_state.user_config = {}

        st.session_state.user_config = config
