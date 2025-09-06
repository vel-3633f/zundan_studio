import streamlit as st
from config import (
    UI_CONFIG,
    Characters,
    DefaultConversations,
)


def render_control_buttons() -> None:
    """Render control buttons for adding/resetting conversations"""
    col1, col2, col3 = st.columns(UI_CONFIG.button_columns)

    zundamon_config = Characters.ZUNDAMON
    metan_config = Characters.METAN

    with col1:
        if st.button(
            f"➕ {zundamon_config.display_name}を追加",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.conversation_lines.append(
                {
                    "speaker": "zundamon",
                    "text": "",
                    "background": "default",
                    "expression": "normal",
                    "item": "none",
                    "visible_characters": ["zundamon"],
                }
            )
            st.rerun()

    with col2:
        if st.button(
            f"➕ {metan_config.display_name}を追加",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.conversation_lines.append(
                {
                    "speaker": "metan",
                    "text": "",
                    "background": "default",
                    "expression": "normal",
                    "item": "none",
                    "visible_characters": ["zundamon", "metan"],
                }
            )
            st.rerun()

    with col3:
        if st.button(
            f"➕ {Characters.NARRATOR.display_name}を追加",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.conversation_lines.append(
                {
                    "speaker": "narrator",
                    "text": "",
                    "background": "default",
                    "expression": "normal",
                    "item": "none",
                    "visible_characters": ["zundamon"],  # デフォルトでずんだもんを表示
                }
            )
            st.rerun()

    # リセットボタンを別の行に配置
    col_reset = st.columns(1)[0]
    with col_reset:
        if st.button("🔄 会話をリセット", use_container_width=True):
            st.session_state.conversation_lines = (
                DefaultConversations.get_reset_conversation()
            )
            st.rerun()
