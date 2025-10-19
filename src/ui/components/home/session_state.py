import streamlit as st
from config import DefaultConversations
from src.core.voice_generator import VoiceGenerator
import logging

logger = logging.getLogger(__name__)


def create_default_section_data():
    """デフォルト会話用のダミーセクションデータを作成"""
    sample_conversation = DefaultConversations.get_sample_conversation()

    # text_for_voicevoxフィールドを追加（ConversationSegmentモデルに合わせる）
    for segment in sample_conversation:
        if "text_for_voicevox" not in segment:
            # textをそのまま使用（ひらがな変換は後で行われる）
            segment["text_for_voicevox"] = segment["text"]
        if "character_expressions" not in segment:
            segment["character_expressions"] = {}

    # すべての会話を1つのセクションにまとめる
    return {
        "title": "サンプル会話",
        "sections": [
            {
                "section_name": "サンプルセクション",
                "scene_background": "blue_sky",
                "bgm_id": "honwaka",
                "bgm_volume": 0.25,
                "segments": sample_conversation,
            }
        ],
        "all_segments": sample_conversation,
    }


def init_session_state():
    """Initialize session state variables"""
    if "conversation_lines" not in st.session_state:
        st.session_state.conversation_lines = (
            DefaultConversations.get_sample_conversation()
        )

    # デフォルトのセクションデータを初期化
    if "loaded_json_data" not in st.session_state:
        st.session_state.loaded_json_data = create_default_section_data()

    for key, default in [
        ("generated_video_path", None),
        ("generation_in_progress", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default
