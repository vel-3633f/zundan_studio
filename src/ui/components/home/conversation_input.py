import streamlit as st
from typing import List
from config import (
    UI_CONFIG,
    Characters,
    Backgrounds,
    Expressions,
)


def render_conversation_input(
    background_options: List[str],
    expression_options: List[str],
) -> None:
    """Render conversation input interface"""
    st.subheader("会話内容")

    for i, line in enumerate(st.session_state.conversation_lines):
        if "background" not in line:
            line["background"] = "default"
        if "expression" not in line:
            line["expression"] = "normal"
        if "visible_characters" not in line:
            line["visible_characters"] = ["zundamon", line.get("speaker", "zundamon")]

        # Get character info from config
        characters = Characters.get_all()
        char_config = characters[line["speaker"]]

        with st.container():
            cols = st.columns(UI_CONFIG.input_columns)

            # Speaker selection
            with cols[0]:
                char_options = Characters.get_display_options()
                current_char_index = next(
                    (
                        idx
                        for idx, opt in enumerate(char_options)
                        if opt[0] == line["speaker"]
                    ),
                    0,
                )

                selected_option = st.selectbox(
                    "話者",
                    options=[opt[0] for opt in char_options],
                    format_func=lambda x: next(
                        opt[1] for opt in char_options if opt[0] == x
                    ),
                    key=f"speaker_{i}",
                    index=current_char_index,
                )
                line["speaker"] = selected_option

            # Text input
            with cols[1]:
                if line["speaker"] == "narrator":
                    label_text = (
                        f"{char_config.emoji} {char_config.display_name}のナレーション"
                    )
                    placeholder_text = "ナレーション内容を入力してください..."
                else:
                    label_text = f"{char_config.emoji} {char_config.display_name} ({char_config.display_position}) のセリフ"
                    placeholder_text = (
                        f"{char_config.display_name}が話す内容を入力してください..."
                    )

                line["text"] = st.text_area(
                    label_text,
                    value=line["text"],
                    height=UI_CONFIG.text_area_height,
                    key=f"text_{i}",
                    placeholder=placeholder_text,
                )

            with cols[2]:
                st.write("背景")
                current_bg_index = (
                    background_options.index(line["background"])
                    if line["background"] in background_options
                    else 0
                )

                line["background"] = st.selectbox(
                    "背景選択",
                    options=background_options,
                    key=f"background_{i}",
                    index=current_bg_index,
                    format_func=Backgrounds.get_display_name,
                    label_visibility="collapsed",
                )

            # Expression selection
            with cols[3]:
                st.write("表情")
                current_expr_index = (
                    expression_options.index(line["expression"])
                    if line["expression"] in expression_options
                    else 0
                )

                line["expression"] = st.selectbox(
                    "表情選択",
                    options=expression_options,
                    key=f"expression_{i}",
                    index=current_expr_index,
                    format_func=Expressions.get_display_name,
                    label_visibility="collapsed",
                )

            # Visible characters selection
            with cols[4]:
                st.write("表示キャラクター")
                # ナレーター以外のキャラクターのみを表示選択肢に含める
                char_options = [
                    opt
                    for opt in Characters.get_display_options()
                    if opt[0] != "narrator"
                ]
                char_names = [opt[0] for opt in char_options]
                char_display_names = {
                    opt[0]: opt[1].split(" ")[1] for opt in char_options
                }

                # ナレーターの場合、話者を自動追加しない
                if line["speaker"] == "narrator":
                    # visible_charactersからnarratorを除外
                    line["visible_characters"] = [
                        char
                        for char in line["visible_characters"]
                        if char != "narrator"
                    ]
                    help_text = "ナレーション中に表示するキャラクターを選択"
                else:
                    help_text = "このセリフの間に表示するキャラクターを選択"

                line["visible_characters"] = st.multiselect(
                    "表示キャラクター選択",
                    options=char_names,
                    default=line["visible_characters"],
                    key=f"visible_chars_{i}",
                    format_func=lambda x: char_display_names.get(x, x),
                    label_visibility="collapsed",
                    help=help_text,
                )

                # 話者がナレーター以外で、含まれていない場合は自動で追加
                if (
                    line["speaker"] != "narrator"
                    and line["speaker"] not in line["visible_characters"]
                ):
                    line["visible_characters"].append(line["speaker"])

        if i < len(st.session_state.conversation_lines) - 1:
            st.markdown("---")
