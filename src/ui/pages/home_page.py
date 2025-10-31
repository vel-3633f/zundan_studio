import streamlit as st
import logging

from src.services.video_generator import VideoGenerator
from src.core.video_processor import VideoProcessor
from config import APP_CONFIG, UI_CONFIG, Expressions, Backgrounds
from src.ui.components.home.conversation_input import render_conversation_input
from src.ui.components.home.sidebar import render_sidebar
from src.ui.components.home.results import render_results
from src.ui.components.home.video_generation import generate_conversation_video
from src.ui.components.home.json_loader import (
    render_json_selector,
    extract_backgrounds_from_json,
    render_item_images_status_check,
)
from src.ui.components.home.background_gallery import render_background_status_check
from src.ui.components.home.section_bgm_editor import (
    render_section_bgm_editor,
    apply_bgm_settings_to_sections,
)
from config import Characters

logger = logging.getLogger(__name__)


@st.cache_data
def get_background_names_cached():
    """背景名を取得（キャッシュ版）"""
    processor = VideoProcessor()
    names = processor.get_background_names()
    del processor
    return names


def render_home_page():
    """ホームページをレンダリング"""
    st.title(f"🏠 {APP_CONFIG.title}")
    st.markdown(APP_CONFIG.description)

    enable_subtitles, conversation_mode = render_sidebar()

    background_options = ["default"] + get_background_names_cached()

    if (
        hasattr(st.session_state, "loaded_json_data")
        and st.session_state.loaded_json_data
    ):
        json_backgrounds = extract_backgrounds_from_json(
            st.session_state.loaded_json_data
        )
        Backgrounds.load_backgrounds_from_names(json_backgrounds)
        background_options = json_backgrounds
        logger.info(f"Using backgrounds from JSON: {json_backgrounds}")
        st.info(
            f"🎬 JSONファイルから {len(json_backgrounds)} の背景を読み込みました: {', '.join(json_backgrounds)}"
        )
    else:
        logger.info(f"Using backgrounds from image files: {background_options}")

    expression_options = Expressions.get_available_names()

    available_characters = list(Characters.get_all().keys())

    current_background_options = background_options
    render_json_selector(available_characters, current_background_options, expression_options)

    # タブでリソースチェックを統合表示
    st.subheader("📋 リソース読み込み状態チェック")
    tab1, tab2 = st.tabs(["🖼️ 背景画像", "🎨 アイテム画像"])

    with tab1:
        render_background_status_check(background_options)

    with tab2:
        loaded_json_data = getattr(st.session_state, "loaded_json_data", None)
        render_item_images_status_check(loaded_json_data)

    render_section_bgm_editor()

    render_conversation_input(background_options, expression_options)

    st.markdown("---")

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

                sections = None
                if hasattr(st.session_state, "loaded_json_data") and st.session_state.loaded_json_data:
                    from src.models.food_over import VideoSection
                    sections_data = st.session_state.loaded_json_data.get("sections", [])
                    if sections_data:
                        sections_data = apply_bgm_settings_to_sections(sections_data)
                        sections = [VideoSection(**section_data) for section_data in sections_data]
                        logger.info(f"セクション情報を使用: {len(sections)}セクション")

                result = generate_conversation_video(
                    conversations=valid_lines,
                    progress_bar=progress_bar,
                    status_text=status_text,
                    enable_subtitles=enable_subtitles,
                    conversation_mode=conversation_mode,
                    sections=sections,
                )

                if result:
                    st.session_state.generated_video_path = result
                    st.success("🎉 会話動画生成完了！")

                    if "section_bgm_settings" in st.session_state:
                        del st.session_state.section_bgm_settings
                        logger.info("Cleared section_bgm_settings from session_state")

            finally:
                st.session_state.generation_in_progress = False

    render_results()
