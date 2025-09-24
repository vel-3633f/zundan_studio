import streamlit as st
import os


def render_results() -> None:
    """Render generation results"""
    if not (
        st.session_state.generated_video_path
        and os.path.exists(st.session_state.generated_video_path)
    ):
        return

    st.header("生成結果")
    st.video(st.session_state.generated_video_path)

    with open(st.session_state.generated_video_path, "rb") as f:
        st.download_button(
            label="📥 動画をダウンロード",
            data=f.read(),
            file_name=os.path.basename(st.session_state.generated_video_path),
            mime="video/mp4",
            type="secondary",
            use_container_width=True,
        )
