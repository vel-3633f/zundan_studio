import streamlit as st
import logging
from datetime import datetime
from src.services.database.food_repository import FoodRepository

logger = logging.getLogger(__name__)


def render_food_management_page():
    """Render food management page."""
    st.title("🍔 食べ物管理")
    st.markdown("---")

    repo = FoodRepository()

    st.subheader("📝 新しい食べ物を追加")
    with st.form("add_food_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_food_name = st.text_input(
                "食べ物の名前", placeholder="例: カレーライス"
            )
        with col2:
            submit_button = st.form_submit_button("➕ 追加", use_container_width=True)

        if submit_button:
            if new_food_name.strip():
                try:
                    with st.spinner("追加中..."):
                        repo.add_food(new_food_name.strip())
                    st.success(f"✅ 「{new_food_name}」を追加しました！")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 追加に失敗しました: {str(e)}")
            else:
                st.warning("⚠️ 食べ物の名前を入力してください")

    st.markdown("---")
    st.subheader("📋 食べ物リスト")

    try:
        with st.spinner("読み込み中..."):
            foods = repo.get_all_foods()

        if not foods:
            st.info(
                "まだ食べ物が登録されていません。上のフォームから追加してください。"
            )
            return

        for food in foods:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    st.markdown(f"### {food['name']}")

                with col2:
                    is_generated = st.checkbox(
                        "動画生成済み",
                        value=food["is_generated"],
                        key=f"check_{food['id']}",
                    )

                    if is_generated != food["is_generated"]:
                        video_info = None
                        if is_generated:
                            video_info = st.text_input(
                                "メモ（任意）",
                                key=f"info_{food['id']}",
                                placeholder="例: YouTube動画ID",
                            )

                        try:
                            with st.spinner("更新中..."):
                                repo.update_generation_status(
                                    food["id"], is_generated, video_info
                                )
                            st.success("✅ 更新しました")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 更新に失敗: {str(e)}")

                with col3:
                    if food.get("generated_at"):
                        generated_date = datetime.fromisoformat(
                            food["generated_at"].replace("Z", "+00:00")
                        )
                        st.caption(
                            f"生成日時: {generated_date.strftime('%Y-%m-%d %H:%M')}"
                        )
                    if food.get("video_info"):
                        st.caption(f"メモ: {food['video_info']}")

                with col4:
                    if st.button("🗑️", key=f"delete_{food['id']}", help="削除"):
                        try:
                            with st.spinner("削除中..."):
                                repo.delete_food(food["id"])
                            st.success("✅ 削除しました")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 削除に失敗: {str(e)}")

                st.markdown("---")

        st.caption(
            f"合計: {len(foods)}件 | 生成済み: {sum(1 for f in foods if f['is_generated'])}件"
        )

    except Exception as e:
        st.error(f"❌ データの読み込みに失敗しました: {str(e)}")
        logger.error(f"Failed to load foods: {e}")
