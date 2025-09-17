import streamlit as st
import os
import logging
import json

from src.utils.utils import (
    setup_logging,
    ensure_directories,
)
from config import APP_CONFIG

from src.ui.components.session_state import init_session_state

# Setup
setup_logging(debug=os.getenv("DEBUG_MODE", "false").lower() == "true")
logger = logging.getLogger(__name__)
ensure_directories()


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
                return st.session_state.user_config.get(config_key, default_value)
        except (KeyError, TypeError):
            pass

    return default_value


page_title = (
    get_effective_config("title", APP_CONFIG.title, ["app", "title"])
    if hasattr(st.session_state, "user_config") and st.session_state.user_config
    else APP_CONFIG.title
)

st.set_page_config(
    page_title=f"{APP_CONFIG.title}",
    page_icon=APP_CONFIG.page_icon,
    layout=APP_CONFIG.layout,
    initial_sidebar_state="expanded",
)


def main():
    """Main application"""
    init_session_state()

    # ページ選択
    page = st.sidebar.selectbox(
        "📄 ページ選択", options=["🏠 ホーム", "📚 記事紹介", "📝 JSON編集", "設定"], index=0
    )

    if page == "🏠 ホーム":
        from src.ui.pages.home_page import render_home_page

        render_home_page()
    elif page == "📚 記事紹介":
        from src.ui.pages.article_introduction_page import (
            render_food_overconsumption_page,
        )

        render_food_overconsumption_page()
    elif page == "📝 JSON編集":
        from src.ui.pages.json_editor_page import render_json_editor_page

        render_json_editor_page()
    elif page == "設定":
        from src.ui.pages.config_page import render_config_page

        render_config_page()


if __name__ == "__main__":
    main()
