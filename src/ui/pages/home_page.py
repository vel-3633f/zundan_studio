import streamlit as st
import logging

from src.services.video_generator import VideoGenerator
from config import APP_CONFIG, UI_CONFIG, Expressions, Items, Backgrounds
from src.ui.components.home.conversation_input import render_conversation_input
from src.ui.components.home.sidebar import render_sidebar
from src.ui.components.home.results import render_results
from src.ui.components.home.video_generation import generate_conversation_video
from src.ui.components.home.json_loader import render_json_selector, extract_backgrounds_from_json
from config import Characters

logger = logging.getLogger(__name__)


def render_home_page():
    """ホームページをレンダリング"""
    # Header
    st.title(f"🏠 {APP_CONFIG.title}")
    st.markdown(APP_CONFIG.description)

    # Sidebar
    enable_subtitles, conversation_mode = render_sidebar()

    # JSONファイルから背景を抽出（読み込まれている場合）
    background_options = ["default"]
    if hasattr(st.session_state, 'loaded_json_data') and st.session_state.loaded_json_data:
        # JSONから背景名を抽出
        json_backgrounds = extract_backgrounds_from_json(st.session_state.loaded_json_data)
        # 背景設定を動的に作成
        Backgrounds.load_backgrounds_from_names(json_backgrounds)
        background_options = json_backgrounds
        logger.info(f"Using backgrounds from JSON: {json_backgrounds}")
        # デバッグ情報を表示
        st.info(f"🎬 JSONファイルから {len(json_backgrounds)} の背景を読み込みました: {', '.join(json_backgrounds)}")
    else:
        # 従来通り画像ファイルから背景を取得
        background_options = [
            "default"
        ] + VideoGenerator().video_processor.get_background_names()
        logger.info(f"Using backgrounds from image files: {background_options}")

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
