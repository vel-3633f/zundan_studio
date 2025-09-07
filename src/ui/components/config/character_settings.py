import streamlit as st
from typing import Dict, Any
from .common_ui import slider_with_range, color_picker_with_rgb, color_preview


def render_character_settings(config: Dict[str, Any]):
    """キャラクター設定のレンダリング"""
    st.subheader("キャラクター表示設定")

    st.markdown("**ずんだもん設定**")

    col1, col2 = st.columns(2)

    with col1:
        config["characters"]["zundamon"]["size_ratio"] = slider_with_range(
            "サイズ倍率",
            config["characters"]["zundamon"]["size_ratio"],
            0.5,
            3.0,
            0.1,
            "キャラクターの表示サイズ",
        )

        config["characters"]["zundamon"]["x_offset_ratio"] = slider_with_range(
            "X位置（横方向）",
            config["characters"]["zundamon"]["x_offset_ratio"],
            0.0,
            1.0,
            0.01,
            "画面幅に対する横方向位置の比率",
        )

        config["characters"]["zundamon"]["y_offset_ratio"] = slider_with_range(
            "Y位置（縦方向）",
            config["characters"]["zundamon"]["y_offset_ratio"],
            0.0,
            1.0,
            0.01,
            "画面高さに対する縦方向位置の比率",
        )

    with col2:
        config["characters"]["zundamon"]["subtitle_color"] = color_picker_with_rgb(
            "字幕枠色",
            config["characters"]["zundamon"]["subtitle_color"],
            "このキャラクターの字幕枠の色",
        )

        st.markdown("**プレビュー**")
        st.markdown(
            f"**位置**: X={config['characters']['zundamon']['x_offset_ratio']:.2f}, Y={config['characters']['zundamon']['y_offset_ratio']:.2f}"
        )
        st.markdown(
            f"**サイズ**: {config['characters']['zundamon']['size_ratio']:.1f}倍"
        )

        # 色プレビュー
        color_preview(
            config["characters"]["zundamon"]["subtitle_color"], "字幕枠色プレビュー"
        )
