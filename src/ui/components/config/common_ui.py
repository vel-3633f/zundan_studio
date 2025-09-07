import streamlit as st
from typing import List, Tuple


def color_picker_with_rgb(
    label: str, rgb_color: List[int], help_text: str = None
) -> List[int]:
    """RGB色をcolor_pickerで編集する共通コンポーネント

    Args:
        label: ラベル
        rgb_color: [R, G, B] の配列
        help_text: ヘルプテキスト

    Returns:
        [R, G, B] の配列
    """
    hex_color = f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
    selected_color = st.color_picker(label, value=hex_color, help=help_text)

    return [
        int(selected_color[1:3], 16),
        int(selected_color[3:5], 16),
        int(selected_color[5:7], 16),
    ]


def slider_range_setting(
    title: str, current_range: List[float], min_step: float = 0.01, key_prefix: str = ""
) -> List[float]:
    """スライダー範囲設定の共通コンポーネント

    Args:
        title: スライダーのタイトル
        current_range: [min, max, default, step] の配列
        min_step: ステップの最小値
        key_prefix: Streamlitのkeyプレフィックス

    Returns:
        [min, max, default, step] の配列
    """
    st.markdown(f"**{title}**")

    min_val = st.number_input(
        "最小値", value=current_range[0], step=min_step, key=f"{key_prefix}_min"
    )
    max_val = st.number_input(
        "最大値", value=current_range[1], step=min_step, key=f"{key_prefix}_max"
    )
    default_val = st.number_input(
        "デフォルト",
        value=current_range[2],
        step=min_step,
        key=f"{key_prefix}_default",
    )
    step_val = st.number_input(
        "ステップ",
        value=current_range[3],
        step=min_step / 10,
        key=f"{key_prefix}_step",
    )

    return [min_val, max_val, default_val, step_val]


def number_input_with_range(
    label: str,
    value: int,
    min_value: int,
    max_value: int,
    step: int = 1,
    help_text: str = None,
) -> int:
    """範囲付き数値入力の共通コンポーネント"""
    return st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        help=help_text,
    )


def slider_with_range(
    label: str,
    value: float,
    min_value: float,
    max_value: float,
    step: float = 0.1,
    help_text: str = None,
) -> float:
    """範囲付きスライダーの共通コンポーネント"""
    return st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        help=help_text,
    )


def color_preview(color: List[int], text: str = "プレビュー") -> None:
    """色のプレビュー表示"""
    st.markdown(
        f"""
        <div style="background-color: rgb({color[0]}, {color[1]}, {color[2]}); 
                    color: white; padding: 10px; border-radius: 5px; text-align: center;">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def background_color_with_alpha(
    label: str, rgba_color: List[int], help_text: str = None
) -> List[int]:
    """背景色（RGBA）設定の共通コンポーネント

    Args:
        label: ラベル
        rgba_color: [R, G, B, A] の配列
        help_text: ヘルプテキスト

    Returns:
        [R, G, B, A] の配列
    """
    bg_col1, bg_col2 = st.columns([3, 1])

    with bg_col1:
        rgb_part = color_picker_with_rgb(label, rgba_color[:3], help_text)

    with bg_col2:
        alpha = st.number_input(
            "透明度",
            min_value=0,
            max_value=255,
            value=rgba_color[3],
            step=1,
            help="0=透明, 255=不透明",
        )

    return rgb_part + [alpha]
