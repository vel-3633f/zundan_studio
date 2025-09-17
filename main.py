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

    # ページ設定
    pages = {
        "🏠 ホーム": {
            "module": "src.ui.pages.home_page",
            "function": "render_home_page",
        },
        "📚 記事紹介": {
            "module": "src.ui.pages.article_introduction_page",
            "function": "render_food_overconsumption_page",
        },
        "📝 JSON編集": {
            "module": "src.ui.pages.json_editor_page",
            "function": "render_json_editor_page",
        },
        "⚙️ 設定": {
            "module": "src.ui.pages.config_page",
            "function": "render_config_page",
        },
    }

    page = st.sidebar.radio(
        "📄 ページ選択",
        options=list(pages.keys()),
        index=0,
    )

    # 選択されたページを動的にインポートして実行
    if page in pages:
        page_config = pages[page]
        module = __import__(page_config["module"], fromlist=[page_config["function"]])
        render_function = getattr(module, page_config["function"])
        render_function()


if __name__ == "__main__":
    main()
