import streamlit as st
from typing import Dict, Any
from .common_ui import (
    color_picker_with_rgb,
    number_input_with_range,
    background_color_with_alpha,
)


def render_subtitle_settings(config: Dict[str, Any]):
    """字幕設定のレンダリング"""
    st.subheader("字幕表示設定")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**フォント設定**")
        config["subtitle"]["font_size"] = number_input_with_range(
            "フォントサイズ", config["subtitle"]["font_size"], 12, 72, 1
        )

        config["subtitle"]["font_color"] = color_picker_with_rgb(
            "フォント色", config["subtitle"]["font_color"], "字幕テキストの色"
        )

        config["subtitle"]["outline_color"] = color_picker_with_rgb(
            "アウトライン色", config["subtitle"]["outline_color"], "文字の縁取り色"
        )

        config["subtitle"]["outline_width"] = number_input_with_range(
            "アウトライン幅", config["subtitle"]["outline_width"], 1, 5, 1
        )

    with col2:
        st.markdown("**背景・レイアウト設定**")

        config["subtitle"]["background_color"] = background_color_with_alpha(
            "背景色", config["subtitle"]["background_color"], "字幕背景の色"
        )

        config["subtitle"]["border_width"] = number_input_with_range(
            "枠線幅", config["subtitle"]["border_width"], 0, 10, 1
        )

        config["subtitle"]["border_radius"] = number_input_with_range(
            "角の丸み", config["subtitle"]["border_radius"], 0, 50, 1
        )

        config["subtitle"]["margin_bottom"] = number_input_with_range(
            "下マージン",
            config["subtitle"]["margin_bottom"],
            10,
            200,
            5,
            "画面下端からの距離",
        )

    st.markdown("**パディング設定**")
    pad_col1, pad_col2, pad_col3, pad_col4 = st.columns(4)

    with pad_col1:
        config["subtitle"]["padding_x"] = number_input_with_range(
            "左右パディング", config["subtitle"]["padding_x"], 5, 50, 1
        )

    with pad_col2:
        config["subtitle"]["padding_top"] = number_input_with_range(
            "上パディング", config["subtitle"]["padding_top"], 5, 30, 1
        )

    with pad_col3:
        config["subtitle"]["padding_bottom"] = number_input_with_range(
            "下パディング", config["subtitle"]["padding_bottom"], 5, 50, 1
        )

    with pad_col4:
        config["subtitle"]["max_chars_per_line"] = number_input_with_range(
            "1行最大文字数", config["subtitle"]["max_chars_per_line"], 10, 100, 1
        )
