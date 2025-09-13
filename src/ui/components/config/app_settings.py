import streamlit as st
from typing import Dict, Any
from .common_ui import number_input_with_range, slider_with_range


def render_app_settings(config: Dict[str, Any]):
    """アプリケーション設定のレンダリング"""
    st.subheader("動画基本設定")

    col1, col2 = st.columns(2)

    with col1:
        config["app"]["fps"] = number_input_with_range(
            "FPS (フレーム/秒)", config["app"]["fps"], 15, 60, 1, "動画のフレームレート"
        )

        config["app"]["default_speed"] = slider_with_range(
            "デフォルト読み上げ速度",
            config["app"]["default_speed"],
            0.5,
            2.0,
            0.1,
            "音声の再生速度",
        )

        config["app"]["default_pitch"] = slider_with_range(
            "デフォルトピッチ",
            config["app"]["default_pitch"],
            -0.15,
            0.15,
            0.01,
            "音声の高さ調整",
        )

    with col2:
        width = number_input_with_range(
            "動画幅",
            config["app"]["resolution"][0],
            640,
            1920,
            16,
            "動画の横幅（ピクセル）",
        )

        height = number_input_with_range(
            "動画高さ",
            config["app"]["resolution"][1],
            360,
            1080,
            16,
            "動画の高さ（ピクセル）",
        )

        config["app"]["resolution"] = [width, height]

        config["app"]["default_intonation"] = slider_with_range(
            "デフォルト抑揚",
            config["app"]["default_intonation"],
            0.0,
            2.0,
            0.1,
            "音声の抑揚の強さ",
        )

        config["app"]["default_subtitles"] = st.checkbox(
            "デフォルトで字幕を表示",
            value=config["app"]["default_subtitles"],
            help="字幕表示のデフォルト設定",
        )
