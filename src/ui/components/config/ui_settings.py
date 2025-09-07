import streamlit as st
from typing import Dict, Any
from .common_ui import slider_range_setting, number_input_with_range


def render_ui_settings(config: Dict[str, Any]):
    """UI設定のレンダリング"""
    st.subheader("ユーザーインターフェース設定")

    st.markdown("**スライダー範囲設定**")

    col1, col2, col3 = st.columns(3)

    with col1:
        config["ui"]["speed_range"] = slider_range_setting(
            "速度スライダー", config["ui"]["speed_range"], 0.01, "speed"
        )

    with col2:
        config["ui"]["pitch_range"] = slider_range_setting(
            "ピッチスライダー", config["ui"]["pitch_range"], 0.001, "pitch"
        )

    with col3:
        config["ui"]["intonation_range"] = slider_range_setting(
            "抑揚スライダー", config["ui"]["intonation_range"], 0.01, "into"
        )

    st.markdown("**その他UI設定**")
    config["ui"]["text_area_height"] = number_input_with_range(
        "テキストエリア高さ",
        config["ui"]["text_area_height"],
        40,
        200,
        10,
        "会話入力テキストエリアの高さ（ピクセル）",
    )
