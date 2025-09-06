import streamlit as st
import json
import os
import sys
from typing import Dict, Any, Tuple

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import APP_CONFIG, SUBTITLE_CONFIG, UI_CONFIG, Characters, Paths


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


def render_config_editor():
    """設定編集ページをレンダリング"""
    st.title("⚙️ 設定エディタ")
    st.markdown("アプリケーションの各種設定値を編集できます。")

    editor = ConfigEditor()
    config = editor.load_user_config()

    # タブで設定を分割
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🎬 動画設定", "📝 字幕設定", "🖥️ UI設定", "🎭 キャラクター設定"]
    )

    with tab1:
        render_app_settings(config)

    with tab2:
        render_subtitle_settings(config)

    with tab3:
        render_ui_settings(config)

    with tab4:
        render_character_settings(config)

    st.markdown("---")

    # 保存・リセットボタン
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💾 設定を保存", type="primary", use_container_width=True):
            editor.save_user_config(config)
            editor.apply_config_to_session(config)
            st.success("設定を保存しました！")
            st.rerun()

    with col2:
        if st.button("🔄 デフォルトに戻す", use_container_width=True):
            config = editor.get_default_config()
            editor.save_user_config(config)
            editor.apply_config_to_session(config)
            st.success("デフォルト設定に戻しました！")
            st.rerun()

    with col3:
        if st.button("📥 現在の設定をダウンロード", use_container_width=True):
            config_json = json.dumps(config, indent=2, ensure_ascii=False)
            st.download_button(
                label="設定ファイルをダウンロード",
                data=config_json,
                file_name="zundan_config.json",
                mime="application/json",
                use_container_width=True,
            )


def render_app_settings(config: Dict[str, Any]):
    """アプリケーション設定のレンダリング"""
    st.subheader("動画基本設定")

    col1, col2 = st.columns(2)

    with col1:
        config["app"]["fps"] = st.number_input(
            "FPS (フレーム/秒)",
            min_value=15,
            max_value=60,
            value=config["app"]["fps"],
            step=1,
            help="動画のフレームレート",
        )

        config["app"]["default_speed"] = st.slider(
            "デフォルト読み上げ速度",
            min_value=0.5,
            max_value=2.0,
            value=config["app"]["default_speed"],
            step=0.1,
            help="音声の再生速度",
        )

        config["app"]["default_pitch"] = st.slider(
            "デフォルトピッチ",
            min_value=-0.15,
            max_value=0.15,
            value=config["app"]["default_pitch"],
            step=0.01,
            help="音声の高さ調整",
        )

    with col2:
        width = st.number_input(
            "動画幅",
            min_value=640,
            max_value=1920,
            value=config["app"]["resolution"][0],
            step=16,
            help="動画の横幅（ピクセル）",
        )

        height = st.number_input(
            "動画高さ",
            min_value=360,
            max_value=1080,
            value=config["app"]["resolution"][1],
            step=16,
            help="動画の高さ（ピクセル）",
        )

        config["app"]["resolution"] = [width, height]

        config["app"]["default_intonation"] = st.slider(
            "デフォルト抑揚",
            min_value=0.0,
            max_value=2.0,
            value=config["app"]["default_intonation"],
            step=0.1,
            help="音声の抑揚の強さ",
        )

        config["app"]["default_subtitles"] = st.checkbox(
            "デフォルトで字幕を表示",
            value=config["app"]["default_subtitles"],
            help="字幕表示のデフォルト設定",
        )


def render_subtitle_settings(config: Dict[str, Any]):
    """字幕設定のレンダリング"""
    st.subheader("字幕表示設定")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**フォント設定**")
        config["subtitle"]["font_size"] = st.number_input(
            "フォントサイズ",
            min_value=12,
            max_value=72,
            value=config["subtitle"]["font_size"],
            step=1,
        )

        font_color = st.color_picker(
            "フォント色",
            value=f"#{config['subtitle']['font_color'][0]:02x}{config['subtitle']['font_color'][1]:02x}{config['subtitle']['font_color'][2]:02x}",
            help="字幕テキストの色",
        )
        config["subtitle"]["font_color"] = [
            int(font_color[1:3], 16),
            int(font_color[3:5], 16),
            int(font_color[5:7], 16),
        ]

        outline_color = st.color_picker(
            "アウトライン色",
            value=f"#{config['subtitle']['outline_color'][0]:02x}{config['subtitle']['outline_color'][1]:02x}{config['subtitle']['outline_color'][2]:02x}",
            help="文字の縁取り色",
        )
        config["subtitle"]["outline_color"] = [
            int(outline_color[1:3], 16),
            int(outline_color[3:5], 16),
            int(outline_color[5:7], 16),
        ]

        config["subtitle"]["outline_width"] = st.number_input(
            "アウトライン幅",
            min_value=1,
            max_value=5,
            value=config["subtitle"]["outline_width"],
            step=1,
        )

    with col2:
        st.markdown("**背景・レイアウト設定**")

        # 背景色（RGBA）
        bg_col1, bg_col2 = st.columns([3, 1])
        with bg_col1:
            bg_color = st.color_picker(
                "背景色",
                value=f"#{config['subtitle']['background_color'][0]:02x}{config['subtitle']['background_color'][1]:02x}{config['subtitle']['background_color'][2]:02x}",
                help="字幕背景の色",
            )
            config["subtitle"]["background_color"][:3] = [
                int(bg_color[1:3], 16),
                int(bg_color[3:5], 16),
                int(bg_color[5:7], 16),
            ]

        with bg_col2:
            alpha = st.number_input(
                "透明度",
                min_value=0,
                max_value=255,
                value=config["subtitle"]["background_color"][3],
                step=1,
                help="0=透明, 255=不透明",
            )
            config["subtitle"]["background_color"][3] = alpha

        config["subtitle"]["border_width"] = st.number_input(
            "枠線幅",
            min_value=0,
            max_value=10,
            value=config["subtitle"]["border_width"],
            step=1,
        )

        config["subtitle"]["border_radius"] = st.number_input(
            "角の丸み",
            min_value=0,
            max_value=50,
            value=config["subtitle"]["border_radius"],
            step=1,
        )

        config["subtitle"]["margin_bottom"] = st.number_input(
            "下マージン",
            min_value=10,
            max_value=200,
            value=config["subtitle"]["margin_bottom"],
            step=5,
            help="画面下端からの距離",
        )

    st.markdown("**パディング設定**")
    pad_col1, pad_col2, pad_col3, pad_col4 = st.columns(4)

    with pad_col1:
        config["subtitle"]["padding_x"] = st.number_input(
            "左右パディング",
            min_value=5,
            max_value=50,
            value=config["subtitle"]["padding_x"],
            step=1,
        )

    with pad_col2:
        config["subtitle"]["padding_top"] = st.number_input(
            "上パディング",
            min_value=5,
            max_value=30,
            value=config["subtitle"]["padding_top"],
            step=1,
        )

    with pad_col3:
        config["subtitle"]["padding_bottom"] = st.number_input(
            "下パディング",
            min_value=5,
            max_value=50,
            value=config["subtitle"]["padding_bottom"],
            step=1,
        )

    with pad_col4:
        config["subtitle"]["max_chars_per_line"] = st.number_input(
            "1行最大文字数",
            min_value=10,
            max_value=100,
            value=config["subtitle"]["max_chars_per_line"],
            step=1,
        )


def render_ui_settings(config: Dict[str, Any]):
    """UI設定のレンダリング"""
    st.subheader("ユーザーインターフェース設定")

    st.markdown("**スライダー範囲設定**")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**速度スライダー**")
        speed_min = st.number_input(
            "最小値", value=config["ui"]["speed_range"][0], step=0.1, key="speed_min"
        )
        speed_max = st.number_input(
            "最大値", value=config["ui"]["speed_range"][1], step=0.1, key="speed_max"
        )
        speed_default = st.number_input(
            "デフォルト",
            value=config["ui"]["speed_range"][2],
            step=0.1,
            key="speed_default",
        )
        speed_step = st.number_input(
            "ステップ",
            value=config["ui"]["speed_range"][3],
            step=0.01,
            key="speed_step",
        )
        config["ui"]["speed_range"] = [speed_min, speed_max, speed_default, speed_step]

    with col2:
        st.markdown("**ピッチスライダー**")
        pitch_min = st.number_input(
            "最小値", value=config["ui"]["pitch_range"][0], step=0.01, key="pitch_min"
        )
        pitch_max = st.number_input(
            "最大値", value=config["ui"]["pitch_range"][1], step=0.01, key="pitch_max"
        )
        pitch_default = st.number_input(
            "デフォルト",
            value=config["ui"]["pitch_range"][2],
            step=0.01,
            key="pitch_default",
        )
        pitch_step = st.number_input(
            "ステップ",
            value=config["ui"]["pitch_range"][3],
            step=0.001,
            key="pitch_step",
        )
        config["ui"]["pitch_range"] = [pitch_min, pitch_max, pitch_default, pitch_step]

    with col3:
        st.markdown("**抑揚スライダー**")
        into_min = st.number_input(
            "最小値",
            value=config["ui"]["intonation_range"][0],
            step=0.1,
            key="into_min",
        )
        into_max = st.number_input(
            "最大値",
            value=config["ui"]["intonation_range"][1],
            step=0.1,
            key="into_max",
        )
        into_default = st.number_input(
            "デフォルト",
            value=config["ui"]["intonation_range"][2],
            step=0.1,
            key="into_default",
        )
        into_step = st.number_input(
            "ステップ",
            value=config["ui"]["intonation_range"][3],
            step=0.01,
            key="into_step",
        )
        config["ui"]["intonation_range"] = [into_min, into_max, into_default, into_step]

    st.markdown("**その他UI設定**")
    config["ui"]["text_area_height"] = st.number_input(
        "テキストエリア高さ",
        min_value=40,
        max_value=200,
        value=config["ui"]["text_area_height"],
        step=10,
        help="会話入力テキストエリアの高さ（ピクセル）",
    )


def render_character_settings(config: Dict[str, Any]):
    """キャラクター設定のレンダリング"""
    st.subheader("キャラクター表示設定")

    st.markdown("**ずんだもん設定**")

    col1, col2 = st.columns(2)

    with col1:
        config["characters"]["zundamon"]["size_ratio"] = st.slider(
            "サイズ倍率",
            min_value=0.5,
            max_value=3.0,
            value=config["characters"]["zundamon"]["size_ratio"],
            step=0.1,
            help="キャラクターの表示サイズ",
        )

        config["characters"]["zundamon"]["x_offset_ratio"] = st.slider(
            "X位置（横方向）",
            min_value=0.0,
            max_value=1.0,
            value=config["characters"]["zundamon"]["x_offset_ratio"],
            step=0.01,
            help="画面幅に対する横方向位置の比率",
        )

        config["characters"]["zundamon"]["y_offset_ratio"] = st.slider(
            "Y位置（縦方向）",
            min_value=0.0,
            max_value=1.0,
            value=config["characters"]["zundamon"]["y_offset_ratio"],
            step=0.01,
            help="画面高さに対する縦方向位置の比率",
        )

    with col2:
        subtitle_color = st.color_picker(
            "字幕枠色",
            value=f"#{config['characters']['zundamon']['subtitle_color'][0]:02x}{config['characters']['zundamon']['subtitle_color'][1]:02x}{config['characters']['zundamon']['subtitle_color'][2]:02x}",
            help="このキャラクターの字幕枠の色",
        )
        config["characters"]["zundamon"]["subtitle_color"] = [
            int(subtitle_color[1:3], 16),
            int(subtitle_color[3:5], 16),
            int(subtitle_color[5:7], 16),
        ]

        st.markdown("**プレビュー**")
        st.markdown(
            f"**位置**: X={config['characters']['zundamon']['x_offset_ratio']:.2f}, Y={config['characters']['zundamon']['y_offset_ratio']:.2f}"
        )
        st.markdown(
            f"**サイズ**: {config['characters']['zundamon']['size_ratio']:.1f}倍"
        )

        # 色プレビュー
        color = config["characters"]["zundamon"]["subtitle_color"]
        st.markdown(
            f"""
        <div style="background-color: rgb({color[0]}, {color[1]}, {color[2]}); 
                    color: white; padding: 10px; border-radius: 5px; text-align: center;">
            字幕枠色プレビュー
        </div>
        """,
            unsafe_allow_html=True,
        )


# Streamlitマルチページでは直接実行される
render_config_editor()
