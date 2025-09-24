import streamlit as st
import logging

from src.video_generator import VideoGenerator
from config import APP_CONFIG, UI_CONFIG, Expressions, Items
from src.ui.components.conversation_input import render_conversation_input
from src.ui.components.sidebar import render_sidebar
from src.ui.components.results import render_results
from src.ui.components.video_generation import generate_conversation_video
from src.ui.components.json_loader import render_json_selector
from config import Characters

logger = logging.getLogger(__name__)


def render_home_page():
    """ホームページをレンダリング"""
    # Header
    st.title(f"🏠 {APP_CONFIG.title}")
    st.markdown(APP_CONFIG.description)

    # Sidebar
    speed, pitch, intonation, enable_subtitles, conversation_mode = render_sidebar()

    background_options = [
        "default"
    ] + VideoGenerator().video_processor.get_background_names()
    expression_options = Expressions.get_available_names()
    item_options = ["none"] + list(Items.get_all().keys())

    available_characters = list(Characters.get_all().keys())
    render_json_selector(available_characters, background_options, expression_options)

    render_conversation_input(background_options, expression_options, item_options)

    st.markdown("---")

    # Generation button
    _, col_gen, _ = st.columns(UI_CONFIG.generate_columns)
    with col_gen:
        valid_lines = [
            line for line in st.session_state.conversation_lines if line["text"].strip()
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

    # Results
    render_results()
