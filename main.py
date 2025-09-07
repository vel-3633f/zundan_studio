import streamlit as st
import os
import logging
import json

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


def load_user_config():
    """ユーザー設定を読み込み"""
    config_file = "temp/user_config.json"
    try:
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                user_config = json.load(f)

            # セッションにユーザー設定を保存
            if "user_config" not in st.session_state:
                st.session_state.user_config = user_config
                logger.info("ユーザー設定を読み込みました")

    except Exception as e:
        logger.warning(f"ユーザー設定の読み込みに失敗: {e}")


def get_effective_config(config_key, default_value, config_path=None):
    """有効な設定値を取得（ユーザー設定優先）"""
    if hasattr(st.session_state, "user_config") and st.session_state.user_config:
        try:
            if config_path:
                value = st.session_state.user_config
                for key in config_path:
                    value = value[key]
                return value
            else:
                # 単純な設定
                return st.session_state.user_config.get(config_key, default_value)
        except (KeyError, TypeError):
            pass

    return default_value


# ユーザー設定を読み込み
load_user_config()

# Page config - ユーザー設定があれば適用
page_title = (
    get_effective_config("title", APP_CONFIG.title, ["app", "title"])
    if hasattr(st.session_state, "user_config") and st.session_state.user_config
    else APP_CONFIG.title
)

st.set_page_config(
    page_title=f"🏠 {APP_CONFIG.title}",  # メインページであることを明示
    page_icon=APP_CONFIG.page_icon,
    layout=APP_CONFIG.layout,
    initial_sidebar_state="expanded",
)


def main():
    """Main application"""
    init_session_state()

    # Header
    st.title(f"🏠 {APP_CONFIG.title}")
    st.markdown(APP_CONFIG.description)

    # ページナビゲーションヒント
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📄 その他のページ**")
    st.sidebar.markdown("- ⚙️ Config Editor: 設定値の編集")

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

    # Conversation input section
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
