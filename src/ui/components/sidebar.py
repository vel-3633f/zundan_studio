import streamlit as st
from config import UI_CONFIG, APP_CONFIG
from src.utils.utils import (
    cleanup_temp_files,
    cleanup_all_generated_files,
    get_generated_files_info,
)


def render_sidebar() -> tuple:
    """Render sidebar and return parameters"""
    with st.sidebar:
        st.header("音声パラメータ")

        speed_range = UI_CONFIG.speed_range
        pitch_range = UI_CONFIG.pitch_range
        intonation_range = UI_CONFIG.intonation_range

        speed = st.slider("話速", *speed_range, help="話すスピードを調整")
        pitch = st.slider("音高", *pitch_range, help="声の高さを調整")
        intonation = st.slider("抑揚", *intonation_range, help="抑揚の強さを調整")

        st.markdown("---")
        st.header("ファイル管理")

        file_info = get_generated_files_info()
        if file_info["total_count"] > 0:
            st.info(
                f"📁 生成済みファイル: {file_info['total_count']}個 ({file_info['total_size_mb']:.1f}MB)"
            )
        else:
            st.info("📁 生成済みファイルなし")

        if st.button(
            "🗑️ 全ファイル削除",
            help="動画・音声・一時ファイルを含む全ての生成ファイルを削除",
            type="secondary",
            use_container_width=True,
        ):
            if file_info["total_count"] > 0:
                deleted_count = cleanup_all_generated_files()
                st.success(f"全ファイル({deleted_count}個)を削除しました")
                st.session_state.generated_video_path = None
                st.rerun()
            else:
                deleted_count = cleanup_temp_files()
                if deleted_count > 0:
                    st.success(f"一時ファイル({deleted_count}個)を削除しました")
                else:
                    st.info("削除するファイルがありませんでした")

    enable_subtitles = APP_CONFIG.default_subtitles
    conversation_mode = "duo"

    return speed, pitch, intonation, enable_subtitles, conversation_mode
