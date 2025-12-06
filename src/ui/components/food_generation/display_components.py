import streamlit as st
from src.models.food_over import StoryOutline
from src.utils.logger import get_logger

logger = get_logger(__name__)


def display_json_debug(data, title="JSON Debug"):
    """JSONデータをデバッグ用に表示"""
    with st.expander(f"🔍 {title}", expanded=False):
        json_data = data.model_dump() if hasattr(data, "model_dump") else data
        st.json(json_data)


def display_outline_for_approval(outline: StoryOutline) -> None:
    """アウトラインを承認用に表示する

    Args:
        outline: 生成されたアウトライン
    """
    st.divider()
    st.markdown("## 📋 生成されたアウトライン")
    st.markdown("以下の内容で動画を生成します。確認して承認してください。")

    # タイトル
    st.success(f"### 🎬 {outline.title}")

    # 主要な情報を3カラムで表示
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📌 冒頭フック")
        st.info(outline.hook_scene_summary)

        st.markdown("#### 🎯 毎日食べる理由")
        st.info(outline.eating_reason)

    with col2:
        st.markdown("#### ⚡ 決定的イベント")
        st.warning(outline.critical_event)

        st.markdown("#### 💊 解決策")
        st.success(outline.solution)

    # 詳細情報をExpanderで表示
    with st.expander("📊 症状の段階的進行を確認", expanded=True):
        for i, symptom in enumerate(outline.symptom_progression, 1):
            st.markdown(f"**{i}. {symptom}**")

    with st.expander("🔬 医学的メカニズムを確認"):
        st.markdown(outline.medical_mechanism)

    with st.expander("🔍 完全なアウトラインデータ（JSON形式）"):
        st.json(outline.model_dump())

    st.divider()


