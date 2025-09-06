import streamlit as st
import os
import logging

from src.utils.utils import (
    setup_logging,
    ensure_directories,
)
from config import (
    APP_CONFIG,
    UI_CONFIG,
    Expressions,
    Items,
)
from src.video_generator import VideoGenerator

from src.ui.components.session_state import (
    init_session_state,
    check_voicevox_connection,
)
from src.ui.components.conversation_input import render_conversation_input
from src.ui.components.control_buttons import render_control_buttons
from src.ui.components.sidebar import render_sidebar
from src.ui.components.results import render_results
from src.ui.components.video_generation import generate_conversation_video

# Setup
setup_logging(debug=os.getenv("DEBUG_MODE", "false").lower() == "true")
logger = logging.getLogger(__name__)
ensure_directories()

# Page config
st.set_page_config(
    page_title=APP_CONFIG.title,
    page_icon=APP_CONFIG.page_icon,
    layout=APP_CONFIG.layout,
    initial_sidebar_state="expanded",
)


def main():
    """Main application"""
    init_session_state()

    # Header
    st.title(APP_CONFIG.title)
    st.markdown(APP_CONFIG.description)

    # Check VOICEVOX connection
    if not check_voicevox_connection():
        st.error(
            "⚠️ VOICEVOX APIに接続できません。Dockerコンテナが起動しているか確認してください。"
        )
        st.info("コマンド: `docker-compose up voicevox`")
        return

    st.success("✅ VOICEVOX API接続完了")

    # Sidebar
    speed, pitch, intonation, enable_subtitles, conversation_mode = render_sidebar()

    # Main content
    col1, col2 = st.columns(UI_CONFIG.main_columns)

    with col1:
        background_options = [
            "default"
        ] + VideoGenerator().video_processor.get_background_names()
        expression_options = Expressions.get_available_names()
        item_options = ["none"] + list(Items.get_all().keys())

        render_conversation_input(background_options, expression_options, item_options)
        render_control_buttons()

        st.markdown("---")

        # Generation button
        _, col_gen, _ = st.columns(UI_CONFIG.generate_columns)
        with col_gen:
            valid_lines = [
                line
                for line in st.session_state.conversation_lines
                if line["text"].strip()
            ]
            has_valid_text = bool(valid_lines)

            if has_valid_text:
                st.info(f"📝 {len(valid_lines)}個のセリフが生成対象です")

            if st.button(
                "🎭 会話動画を生成",
                type="primary",
                disabled=not has_valid_text or st.session_state.generation_in_progress,
                use_container_width=True,
                help="入力されたセリフから会話動画を生成します",
            ):

                st.session_state.generation_in_progress = True

                try:
                    with col2:
                        st.header("生成状況")
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        status_text.text("生成中...")

                    result = generate_conversation_video(
                        conversations=valid_lines,
                        speed=speed,
                        pitch=pitch,
                        intonation=intonation,
                        progress_bar=progress_bar,
                        status_text=status_text,
                        enable_subtitles=enable_subtitles,
                        conversation_mode=conversation_mode,
                    )

                    if result:
                        st.session_state.generated_video_path = result
                        st.success("🎉 会話動画生成完了！")

                finally:
                    st.session_state.generation_in_progress = False

    with col2:
        if not st.session_state.generation_in_progress:
            st.header("生成状況")
            st.progress(0)
            st.text("待機中...")

    # Results
    render_results()

    # Footer
    st.markdown("---")
    st.markdown(
        """
    **注意事項:**
    - 生成には時間がかかる場合があります
    - 長いテキストほど処理時間が長くなります
    - 各セリフごとに背景を変更できます
    """
    )


if __name__ == "__main__":
    main()
