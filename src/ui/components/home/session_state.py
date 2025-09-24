import streamlit as st
from config import DefaultConversations
from src.core.voice_generator import VoiceGenerator
import logging

logger = logging.getLogger(__name__)


def init_session_state():
    """Initialize session state variables"""
    if "conversation_lines" not in st.session_state:
        st.session_state.conversation_lines = (
            DefaultConversations.get_sample_conversation()
        )

    for key, default in [
        ("generated_video_path", None),
        ("generation_in_progress", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default
