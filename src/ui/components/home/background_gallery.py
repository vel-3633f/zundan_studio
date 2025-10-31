import streamlit as st
from typing import List, Dict, Optional
import os
import logging
from config import Paths, Backgrounds
from PIL import Image

logger = logging.getLogger(__name__)


def get_background_info(bg_name: str, backgrounds_dir: str, valid_extensions: List[str]) -> Optional[Dict]:
    """背景画像の情報を取得"""
    for ext in valid_extensions:
        potential_path = os.path.join(backgrounds_dir, f"{bg_name}{ext}")
        if os.path.exists(potential_path):
            try:
                # ファイルサイズを取得
                file_size = os.path.getsize(potential_path)
                file_size_kb = file_size / 1024

                # 画像サイズを取得（デッドロック回避のため、即座にロードして閉じる）
                img = None
                try:
                    img = Image.open(potential_path)
                    img.load()  # 画像データを即座にメモリにロード
                    width, height = img.size
                    format_name = img.format or "Unknown"
                finally:
                    if img:
                        img.close()  # 明示的にファイルハンドルを閉じる

                return {
                    "exists": True,
                    "path": potential_path,
                    "extension": ext,
                    "file_size_kb": file_size_kb,
                    "width": width,
                    "height": height,
                    "format": format_name,
                }
            except OSError as e:
                # ファイルロック関連のエラーの場合、基本情報のみ返す
                if e.errno == 35:  # Resource deadlock avoided
                    return {
                        "exists": True,
                        "path": potential_path,
                        "extension": ext,
                        "file_size_kb": file_size_kb,
                        "width": "N/A",
                        "height": "N/A",
                        "format": "PNG (locked)",
                        "warning": "ファイルロック中（サイズ情報のみ取得）",
                    }
                return {
                    "exists": True,
                    "path": potential_path,
                    "extension": ext,
                    "error": str(e),
                }
            except Exception as e:
                return {
                    "exists": True,
                    "path": potential_path,
                    "extension": ext,
                    "error": str(e),
                }

    return None


def render_background_status_check(background_options: List[str]) -> None:
    """背景画像の読み込み状態を確認して表示"""
    if not background_options or (len(background_options) == 1 and background_options[0] == "default"):
        st.info("背景画像が見つかりません")
        return

    # 背景画像ディレクトリのパスを取得
    backgrounds_dir = Paths.get_backgrounds_dir()

    # 利用可能な画像拡張子
    valid_extensions = Backgrounds.get_supported_extensions()

    # 背景オプションをフィルタリング（defaultを除外）
    display_backgrounds = [bg for bg in background_options if bg != "default"]

    if not display_backgrounds:
        st.info("カスタム背景画像はありません")
        return

    # 各背景の情報を収集
    background_statuses = []
    for bg_name in display_backgrounds:
        info = get_background_info(bg_name, backgrounds_dir, valid_extensions)
        display_name = Backgrounds.get_display_name(bg_name)

        if info:
            if "error" in info:
                background_statuses.append({
                    "背景名": display_name,
                    "状態": "⚠️",
                    "ファイル": f"{bg_name}{info['extension']}",
                    "詳細": f"エラー: {info['error']}",
                })
            elif "warning" in info:
                background_statuses.append({
                    "背景名": display_name,
                    "状態": "✅",
                    "ファイル": f"{bg_name}{info['extension']}",
                    "詳細": f"{info['file_size_kb']:.1f}KB ({info['warning']})",
                })
            else:
                background_statuses.append({
                    "背景名": display_name,
                    "状態": "✅",
                    "ファイル": f"{bg_name}{info['extension']}",
                    "詳細": f"{info['width']}x{info['height']}px, {info['file_size_kb']:.1f}KB, {info['format']}",
                })
        else:
            background_statuses.append({
                "背景名": display_name,
                "状態": "❌",
                "ファイル": bg_name,
                "詳細": "ファイルが見つかりません",
            })

    # 統計情報を表示
    total = len(background_statuses)
    loaded = sum(1 for status in background_statuses if status["状態"] == "✅")
    errors = sum(1 for status in background_statuses if status["状態"] == "⚠️")
    missing = sum(1 for status in background_statuses if status["状態"] == "❌")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("合計", total)
    with col2:
        st.metric("読み込み成功", loaded)
    with col3:
        st.metric("エラー", errors)
    with col4:
        st.metric("未検出", missing)

    # テーブルで詳細を表示
    st.dataframe(
        background_statuses,
        use_container_width=True,
        hide_index=True,
    )

    # 画像管理機能
    st.markdown("---")
    st.markdown("### 📤 背景画像の管理")

    col_upload, col_manage = st.columns([1, 1])

    with col_upload:
        st.markdown("**新規アップロード**")
        uploaded_file = st.file_uploader(
            "背景画像をアップロード",
            type=["png", "jpg", "jpeg", "webp"],
            help="背景画像ファイルを選択してください",
            key="background_uploader"
        )

        if uploaded_file:
            # ファイル名から拡張子を取得
            file_ext = os.path.splitext(uploaded_file.name)[1]
            # デフォルトのファイル名（拡張子なし）を提案
            default_name = os.path.splitext(uploaded_file.name)[0]

            new_bg_name = st.text_input(
                "保存名（拡張子なし）",
                value=default_name,
                help="背景画像の名前を入力してください（例: kitchen, bedroom）",
                key="new_bg_name"
            )

            # プレビュー表示
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"プレビュー: {uploaded_file.name}", width=200)
                st.write(f"サイズ: {image.size[0]}x{image.size[1]}px")
            except Exception as e:
                st.error(f"画像の読み込みに失敗: {e}")

            if st.button("💾 アップロード", type="primary", key="upload_bg_btn"):
                if new_bg_name.strip():
                    try:
                        # 保存先パス
                        save_path = os.path.join(backgrounds_dir, f"{new_bg_name.strip()}{file_ext}")

                        # ファイルが既に存在するか確認
                        if os.path.exists(save_path):
                            st.warning(f"⚠️ '{new_bg_name}' は既に存在します。上書きしますか？")
                            if st.button("上書き保存", key="overwrite_bg_btn"):
                                image = Image.open(uploaded_file)
                                image.save(save_path)
                                st.success(f"✅ '{new_bg_name}' を上書き保存しました！")
                                st.rerun()
                        else:
                            # 新規保存
                            image = Image.open(uploaded_file)
                            image.save(save_path)
                            st.success(f"✅ '{new_bg_name}' をアップロードしました！")
                            logger.info(f"Uploaded new background: {save_path}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ アップロードに失敗: {e}")
                        logger.error(f"Failed to upload background: {e}")
                else:
                    st.warning("保存名を入力してください")

    with col_manage:
        st.markdown("**既存画像の管理**")

        if display_backgrounds:
            selected_bg = st.selectbox(
                "管理する背景を選択",
                options=display_backgrounds,
                format_func=lambda x: Backgrounds.get_display_name(x),
                key="manage_bg_select"
            )

            if selected_bg:
                # 画像情報を取得
                bg_info = get_background_info(selected_bg, backgrounds_dir, valid_extensions)

                if bg_info and bg_info.get("exists"):
                    # プレビュー表示
                    try:
                        image = Image.open(bg_info["path"])
                        st.image(image, caption=f"{Backgrounds.get_display_name(selected_bg)}", width=200)
                        if "width" in bg_info and "height" in bg_info:
                            st.write(f"サイズ: {bg_info['width']}x{bg_info['height']}px")
                    except Exception as e:
                        st.warning(f"プレビュー表示失敗: {e}")

                    # 名前変更
                    with st.expander("✏️ 名前を変更"):
                        new_name = st.text_input(
                            "新しい名前（拡張子なし）",
                            value=selected_bg,
                            key="rename_bg_input"
                        )
                        if st.button("名前を変更", key="rename_bg_btn"):
                            if new_name.strip() and new_name != selected_bg:
                                try:
                                    old_path = bg_info["path"]
                                    new_path = os.path.join(backgrounds_dir, f"{new_name.strip()}{bg_info['extension']}")

                                    if os.path.exists(new_path):
                                        st.error(f"❌ '{new_name}' は既に存在します")
                                    else:
                                        os.rename(old_path, new_path)
                                        st.success(f"✅ '{selected_bg}' → '{new_name}' に変更しました")
                                        logger.info(f"Renamed background: {old_path} -> {new_path}")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 名前変更に失敗: {e}")
                                    logger.error(f"Failed to rename background: {e}")
                            elif new_name == selected_bg:
                                st.info("同じ名前です")
                            else:
                                st.warning("新しい名前を入力してください")

                    # 削除
                    with st.expander("🗑️ 削除", expanded=False):
                        st.warning(f"⚠️ '{Backgrounds.get_display_name(selected_bg)}' を削除しますか？この操作は取り消せません。")
                        confirm_delete = st.checkbox(f"本当に削除する", key="confirm_delete_bg")
                        if confirm_delete:
                            if st.button("🗑️ 削除を実行", type="secondary", key="delete_bg_btn"):
                                try:
                                    os.remove(bg_info["path"])
                                    st.success(f"✅ '{selected_bg}' を削除しました")
                                    logger.info(f"Deleted background: {bg_info['path']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 削除に失敗: {e}")
                                    logger.error(f"Failed to delete background: {e}")
                else:
                    st.warning("選択した背景の情報が取得できません")
        else:
            st.info("管理する背景画像がありません")
