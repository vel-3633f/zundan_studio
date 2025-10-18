import streamlit as st
import os
import logging
from src.utils.utils import (
    setup_logging,
    ensure_directories,
)
from config import APP_CONFIG
from src.ui.components.home.session_state import init_session_state

setup_logging(debug=os.getenv("DEBUG_MODE", "false").lower() == "true")
logger = logging.getLogger(__name__)
ensure_directories()

st.set_page_config(
    page_title=f"{APP_CONFIG.title}",
    page_icon=APP_CONFIG.page_icon,
    layout=APP_CONFIG.layout,
    initial_sidebar_state="expanded",
)


def main():
    """Main application"""
    init_session_state()

    pages = {
        "🏠 ホーム": {
            "module": "src.ui.pages.home_page",
            "function": "render_home_page",
        },
        "📚 台本生成": {
            "module": "src.ui.pages.food_generation_page",
            "function": "render_food_overconsumption_page",
        },
        "📝 JSON編集": {
            "module": "src.ui.pages.json_editor_page",
            "function": "render_json_editor_page",
        },
        "🍔 食べ物管理": {
            "module": "src.ui.pages.food_management_page",
            "function": "render_food_management_page",
        },
    }

    page = st.sidebar.radio(
        "📄 ページ選択",
        options=list(pages.keys()),
        index=0,
    )

    if page in pages:
        page_config = pages[page]
        module = __import__(page_config["module"], fromlist=[page_config["function"]])
        render_function = getattr(module, page_config["function"])
        render_function()


if __name__ == "__main__":
    main()
