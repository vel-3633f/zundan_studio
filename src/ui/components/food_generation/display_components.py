import streamlit as st
from src.utils.logger import get_logger

logger = get_logger(__name__)


def display_json_debug(data, title="JSON Debug"):
    """JSONデータをデバッグ用に表示"""
    with st.expander(f"🔍 {title}", expanded=False):
        json_data = data.model_dump() if hasattr(data, "model_dump") else data
        st.json(json_data)


