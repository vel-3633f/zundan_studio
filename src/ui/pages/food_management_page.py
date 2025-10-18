import streamlit as st
import logging
from datetime import datetime, timezone, timedelta
from src.services.database.food_repository import FoodRepository

logger = logging.getLogger(__name__)

# 日本時間のタイムゾーン
JST = timezone(timedelta(hours=9))


def render_food_management_page():
    """Render food management page."""
    st.title("🍔 食べ物管理")
    st.markdown("---")

    repo = FoodRepository()

    # 折りたたみ可能な追加セクション
    with st.expander("➕ 新しい食べ物を追加", expanded=False):
        # タブで単一追加と一括追加を切り替え
        tab1, tab2 = st.tabs(["単一追加", "一括追加（JSON）"])

        with tab1:
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

        with tab2:
            st.markdown("""
            **📋 JSON形式の説明**

            以下のいずれかの形式で入力してください：

            **形式1: 配列形式**
            ```json
            ["カレーライス", "ラーメン", "寿司", "ピザ"]
            ```

            **形式2: オブジェクト配列形式**
            ```json
            [
              {"name": "カレーライス"},
              {"name": "ラーメン"},
              {"name": "寿司"}
            ]
            ```
            """)

            with st.form("bulk_add_food_form", clear_on_submit=True):
                json_input = st.text_area(
                    "JSON形式で食べ物を入力",
                    placeholder='["カレーライス", "ラーメン", "寿司"]',
                    height=150
                )
                bulk_submit = st.form_submit_button("➕ 一括追加", use_container_width=True)

                if bulk_submit:
                    if json_input.strip():
                        try:
                            import json
                            foods_data = json.loads(json_input)

                            # データ形式の検証と正規化
                            food_names = []
                            if isinstance(foods_data, list):
                                for item in foods_data:
                                    if isinstance(item, str):
                                        food_names.append(item.strip())
                                    elif isinstance(item, dict) and "name" in item:
                                        food_names.append(item["name"].strip())
                                    else:
                                        st.error("❌ JSON形式が正しくありません。上記の形式例を参考にしてください。")
                                        food_names = []
                                        break
                            else:
                                st.error("❌ JSON形式が正しくありません。配列形式で入力してください。")
                                food_names = []

                            if food_names:
                                # 空の名前をフィルタリング
                                food_names = [name for name in food_names if name]

                                if not food_names:
                                    st.warning("⚠️ 有効な食べ物の名前がありません")
                                else:
                                    with st.spinner(f"{len(food_names)}件追加中..."):
                                        success_count = 0
                                        error_count = 0
                                        for name in food_names:
                                            try:
                                                repo.add_food(name)
                                                success_count += 1
                                            except Exception as e:
                                                logger.error(f"Failed to add food '{name}': {e}")
                                                error_count += 1

                                        if error_count == 0:
                                            st.success(f"✅ {success_count}件の食べ物を追加しました！")
                                        else:
                                            st.warning(f"⚠️ {success_count}件成功、{error_count}件失敗しました")

                                        st.rerun()

                        except json.JSONDecodeError as e:
                            st.error(f"❌ JSON解析エラー: {str(e)}\n\n上記の形式例を参考にしてください。")
                        except Exception as e:
                            st.error(f"❌ 追加に失敗しました: {str(e)}")
                    else:
                        st.warning("⚠️ JSONデータを入力してください")

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

        # 食べ物名の配列をコピー用に表示
        import json
        food_names = [food["name"] for food in foods]
        food_names_json = json.dumps(food_names, ensure_ascii=False)

        with st.expander("📋 食べ物リストをコピー", expanded=False):
            st.code(food_names_json, language="json")
            st.caption("👆 上のテキストを選択してコピーできます")

        # 並び替え: is_generated が False のものを上に、True のものを下に
        sorted_foods = sorted(foods, key=lambda x: (x["is_generated"], x["name"]))

        # セッションステートで編集中のIDを管理
        if "editing_food_id" not in st.session_state:
            st.session_state.editing_food_id = None

        # テーブルヘッダー
        header_cols = st.columns([4, 2, 2, 1, 1])
        with header_cols[0]:
            st.markdown("**食べ物名**")
        with header_cols[1]:
            st.markdown("**生成日時**")
        with header_cols[2]:
            st.markdown("**状態**")
        with header_cols[3]:
            st.markdown("**編集**")
        with header_cols[4]:
            st.markdown("**削除**")

        st.markdown("---")

        for food in sorted_foods:
            is_editing = st.session_state.editing_food_id == food["id"]

            if is_editing:
                # 編集モード
                col1, col2, col3 = st.columns([4, 2, 2])

                with col1:
                    new_name = st.text_input(
                        "名前を編集",
                        value=food["name"],
                        key=f"edit_input_{food['id']}",
                        label_visibility="collapsed",
                    )

                with col2:
                    if st.button("💾 保存", key=f"save_{food['id']}"):
                        if new_name.strip():
                            try:
                                with st.spinner("保存中..."):
                                    repo.update_food_name(food["id"], new_name.strip())
                                st.success("✅ 保存しました")
                                st.session_state.editing_food_id = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ 保存に失敗: {str(e)}")
                        else:
                            st.warning("⚠️ 名前を入力してください")

                with col3:
                    if st.button("❌ キャンセル", key=f"cancel_{food['id']}"):
                        st.session_state.editing_food_id = None
                        st.rerun()

            else:
                # 通常モード
                col1, col2, col3, col4, col5 = st.columns([4, 2, 2, 1, 1])

                with col1:
                    st.markdown(food['name'])

                with col2:
                    if food.get("generated_at"):
                        # UTCからJSTに変換
                        generated_date = datetime.fromisoformat(
                            food["generated_at"].replace("Z", "+00:00")
                        )
                        jst_date = generated_date.astimezone(JST)
                        st.markdown(f"{jst_date.strftime('%m/%d %H:%M')}")
                    else:
                        st.markdown("—")

                with col3:
                    # 動画生成済みチェックボックス
                    is_generated = st.checkbox(
                        "生成済み",
                        value=food["is_generated"],
                        key=f"check_{food['id']}",
                        label_visibility="collapsed",
                    )

                    # チェックボックスの状態が変更された場合、即座に更新
                    if is_generated != food["is_generated"]:
                        try:
                            with st.spinner("更新中..."):
                                repo.update_generation_status(
                                    food["id"],
                                    is_generated,
                                    None,
                                )
                            st.success("✅ 更新しました")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 更新に失敗: {str(e)}")

                with col4:
                    if st.button("✏️", key=f"edit_{food['id']}", help="編集"):
                        st.session_state.editing_food_id = food["id"]
                        st.rerun()

                with col5:
                    if st.button("🗑️", key=f"delete_{food['id']}", help="削除"):
                        try:
                            with st.spinner("削除中..."):
                                repo.delete_food(food["id"])
                            st.success("✅ 削除しました")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 削除に失敗: {str(e)}")

        st.caption(
            f"合計: {len(foods)}件 | 生成済み: {sum(1 for f in foods if f['is_generated'])}件"
        )

    except Exception as e:
        st.error(f"❌ データの読み込みに失敗しました: {str(e)}")
        logger.error(f"Failed to load foods: {e}")
