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
    """アウトラインを承認用に表示する（8セクション構造対応）

    Args:
        outline: 生成されたアウトライン
    """
    st.divider()
    st.markdown("## 📋 生成されたアウトライン")
    st.markdown("以下の内容で動画を生成します。確認して承認してください。")

    # タイトルと食べ物名
    st.success(f"### 🎬 {outline.title}")
    st.info(f"**対象食品**: {outline.food_name}")

    st.markdown("---")
    st.markdown("### 📖 8つのセクション構成")

    # セクション1-4
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 1️⃣ 冒頭フック・危機の予告")
        st.info(outline.hook_content)

        st.markdown("#### 2️⃣ 食品解説・背景情報")
        st.info(outline.background_content)

        st.markdown("#### 3️⃣ 日常導入・理由付け")
        st.info(outline.daily_content)

        st.markdown("#### 4️⃣ 楽観期・ハネムーン期")
        st.info(outline.honeymoon_content)

    with col2:
        st.markdown("#### 5️⃣ 異変期・段階的悪化")
        with st.container():
            for i, symptom in enumerate(outline.deterioration_content, 1):
                st.markdown(f"**第{i}段階**: {symptom}")

        st.markdown("#### 6️⃣ 危機・転機となる決定的イベント")
        st.warning(outline.crisis_content)

        st.markdown("#### 7️⃣ 真相解明・学習フェーズ")
        st.info(outline.learning_content)

        st.markdown("#### 8️⃣ 回復・新しい習慣")
        st.success(outline.recovery_content)

    # 完全なデータをExpanderで表示
    with st.expander("🔍 完全なアウトラインデータ（JSON形式）"):
        st.json(outline.model_dump())

    st.divider()


