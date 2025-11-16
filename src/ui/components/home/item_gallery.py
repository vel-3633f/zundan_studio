"""アイテム画像ギャラリーコンポーネント"""

import streamlit as st
from typing import List, Dict, Optional
import os
import logging
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)


def get_item_info(item_name: str, items_dir: str) -> Optional[Dict]:
    """アイテム画像の情報を取得

    Args:
        item_name: アイテム名
        items_dir: アイテムディレクトリのパス

    Returns:
        Dict: アイテム情報、または存在しない場合None
    """
    # items直下を検索
    potential_path = os.path.join(items_dir, f"{item_name}.png")
    if os.path.exists(potential_path):
        return _get_image_info(potential_path)

    # サブディレクトリを再帰的に検索
    for root, dirs, files in os.walk(items_dir):
        if f"{item_name}.png" in files:
            full_path = os.path.join(root, f"{item_name}.png")
            return _get_image_info(full_path)

    return None


def _get_image_info(path: str) -> Dict:
    """画像ファイルの情報を取得

    Args:
        path: 画像ファイルのパス

    Returns:
        Dict: 画像情報
    """
    try:
        # ファイルサイズを取得
        file_size = os.path.getsize(path)
        file_size_kb = file_size / 1024

        # 画像サイズを取得
        img = None
        try:
            img = Image.open(path)
            img.load()
            width, height = img.size
            format_name = img.format or "Unknown"
        finally:
            if img:
                img.close()

        return {
            "exists": True,
            "path": path,
            "file_size_kb": file_size_kb,
            "width": width,
            "height": height,
            "format": format_name,
        }
    except Exception as e:
        return {
            "exists": True,
            "path": path,
            "error": str(e),
        }


def validate_item_name(item_name: str) -> bool:
    """アイテム名が3単語形式か検証

    Args:
        item_name: アイテム名

    Returns:
        bool: 有効な場合True
    """
    parts = item_name.split("_")
    if len(parts) != 3:
        return False
    return all(part.islower() and part.isalpha() for part in parts)


def render_item_status_check(item_names: List[str], items_dir: str) -> None:
    """アイテム画像の読み込み状態を確認して表示

    Args:
        item_names: アイテム名のリスト
        items_dir: アイテムディレクトリのパス
    """
    if not item_names:
        st.info("アイテム画像が見つかりません")
        return

    # 各アイテムの情報を収集
    item_statuses = []
    for item_name in item_names:
        info = get_item_info(item_name, items_dir)

        # 3単語形式のチェック
        naming_ok = validate_item_name(item_name)

        if info:
            if "error" in info:
                item_statuses.append(
                    {
                        "アイテム名": item_name,
                        "状態": "⚠️",
                        "ファイル": f"{item_name}.png",
                        "詳細": f"エラー: {info['error']}",
                    }
                )
            else:
                detail = f"{info['width']}x{info['height']}px, {info['file_size_kb']:.1f}KB, {info['format']}"
                if not naming_ok:
                    detail += " ⚠️ 命名規則違反"
                item_statuses.append(
                    {
                        "アイテム名": item_name,
                        "状態": "✅",
                        "ファイル": f"{item_name}.png",
                        "詳細": detail,
                    }
                )
        else:
            detail = "ファイルが見つかりません"
            if not naming_ok:
                detail += " ⚠️ 命名規則違反"
            item_statuses.append(
                {
                    "アイテム名": item_name,
                    "状態": "❌",
                    "ファイル": f"{item_name}.png",
                    "詳細": detail,
                }
            )

    # 統計情報を表示
    total = len(item_statuses)
    loaded = sum(1 for status in item_statuses if status["状態"] == "✅")
    errors = sum(1 for status in item_statuses if status["状態"] == "⚠️")
    missing = sum(1 for status in item_statuses if status["状態"] == "❌")

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
        item_statuses,
        use_container_width=True,
        hide_index=True,
    )


def render_item_upload_section(items_dir: str) -> None:
    """アイテム画像のアップロードセクションをレンダリング

    Args:
        items_dir: アイテムディレクトリのパス
    """
    st.markdown("**新規アップロード**")
    uploaded_file = st.file_uploader(
        "アイテム画像をアップロード",
        type=["png"],
        help="アイテム画像ファイル（PNG）を選択してください",
        key="item_uploader",
    )

    if uploaded_file:
        # デフォルトのファイル名（拡張子なし）を提案
        default_name = os.path.splitext(uploaded_file.name)[0]

        new_item_name = st.text_input(
            "保存名（拡張子なし）",
            value=default_name,
            help="アイテム画像のIDを入力してください\n命名規則: 3つの英単語をアンダースコアで区切る（例: steaming_hot_ramen）",
            key="new_item_name",
        )

        # 3単語形式のバリデーション
        if new_item_name.strip():
            parts = new_item_name.strip().split("_")
            if len(parts) != 3:
                st.warning(
                    f"⚠️ アイテム名は3つの英単語をアンダースコアで区切る形式にしてください\n"
                    f"現在: {len(parts)}単語 → 必要: 3単語\n"
                    f"例: steaming_hot_ramen, fresh_green_spinach"
                )
            elif not all(part.islower() and part.isalpha() for part in parts):
                st.warning(
                    "⚠️ 各単語は小文字の英字のみで構成してください\n"
                    "例: steaming_hot_ramen (OK) / Steaming_Hot_Ramen (NG)"
                )
            else:
                st.success("✅ 命名規則に適合しています")

        # プレビュー表示
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"プレビュー: {uploaded_file.name}", width=150)
            st.write(f"サイズ: {image.size[0]}x{image.size[1]}px")
        except Exception as e:
            st.error(f"画像の読み込みに失敗: {e}")

        if st.button("💾 アップロード", type="primary", key="upload_item_btn"):
            if new_item_name.strip():
                # 3単語形式のバリデーション
                parts = new_item_name.strip().split("_")
                if len(parts) != 3:
                    st.error(
                        f"❌ アイテム名は3つの英単語をアンダースコアで区切る形式にしてください\n"
                        f"例: steaming_hot_ramen, yellow_vitamin_capsules"
                    )
                elif not all(part.islower() and part.isalpha() for part in parts):
                    st.error(
                        "❌ 各単語は小文字の英字のみで構成してください\n"
                        "例: steaming_hot_ramen"
                    )
                else:
                    try:
                        # 保存先パス（items直下）
                        os.makedirs(items_dir, exist_ok=True)
                        save_path = os.path.join(items_dir, f"{new_item_name.strip()}.png")

                        # ファイルが既に存在するか確認
                        if os.path.exists(save_path):
                            st.warning(f"⚠️ '{new_item_name}' は既に存在します。上書きしますか？")
                            if st.button("上書き保存", key="overwrite_item_btn"):
                                image = Image.open(uploaded_file)
                                image.save(save_path)
                                st.success(f"✅ '{new_item_name}' を上書き保存しました！")
                                st.rerun()
                        else:
                            # 新規保存
                            image = Image.open(uploaded_file)
                            image.save(save_path)
                            st.success(f"✅ '{new_item_name}' をアップロードしました！")
                            logger.info(f"Uploaded new item: {save_path}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ アップロードに失敗: {e}")
                        logger.error(f"Failed to upload item: {e}")
            else:
                st.warning("保存名を入力してください")


def render_item_management_section(items_dir: str) -> None:
    """既存アイテムの管理セクションをレンダリング

    Args:
        items_dir: アイテムディレクトリのパス
    """
    st.markdown("**既存画像の管理**")

    # items配下の全PNGファイルを取得
    existing_items = []
    if os.path.exists(items_dir):
        for root, dirs, files in os.walk(items_dir):
            for filename in files:
                if filename.endswith(".png"):
                    item_id = os.path.splitext(filename)[0]
                    file_path = os.path.join(root, filename)
                    existing_items.append((item_id, file_path))

    if existing_items:
        # アイテムIDでソート
        existing_items.sort(key=lambda x: x[0])

        selected_item = st.selectbox(
            "管理するアイテムを選択",
            options=[item[0] for item in existing_items],
            key="manage_item_select",
        )

        if selected_item:
            # 選択されたアイテムのパスを取得
            selected_path = next(
                path for item_id, path in existing_items if item_id == selected_item
            )

            # プレビュー表示
            try:
                image = Image.open(selected_path)
                st.image(image, caption=f"{selected_item}.png", width=150)
                st.write(f"サイズ: {image.size[0]}x{image.size[1]}px")
                st.caption(f"パス: {selected_path}")
            except Exception as e:
                st.warning(f"プレビュー表示失敗: {e}")

            # 名前変更
            with st.expander("✏️ 名前を変更"):
                new_name = st.text_input(
                    "新しい名前（拡張子なし）",
                    value=selected_item,
                    key="rename_item_input",
                )
                if st.button("名前を変更", key="rename_item_btn"):
                    if new_name.strip() and new_name != selected_item:
                        try:
                            old_path = Path(selected_path)
                            new_path = old_path.parent / f"{new_name.strip()}.png"

                            if new_path.exists():
                                st.error(f"❌ '{new_name}' は既に存在します")
                            else:
                                old_path.rename(new_path)
                                st.success(
                                    f"✅ '{selected_item}' → '{new_name}' に変更しました"
                                )
                                logger.info(f"Renamed item: {old_path} -> {new_path}")
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ 名前変更に失敗: {e}")
                            logger.error(f"Failed to rename item: {e}")
                    elif new_name == selected_item:
                        st.info("同じ名前です")
                    else:
                        st.warning("新しい名前を入力してください")

            # 削除
            with st.expander("🗑️ 削除", expanded=False):
                st.warning(
                    f"⚠️ '{selected_item}.png' を削除しますか？この操作は取り消せません。"
                )
                confirm_delete = st.checkbox(
                    f"本当に削除する", key="confirm_delete_item"
                )
                if confirm_delete:
                    if st.button(
                        "🗑️ 削除を実行", type="secondary", key="delete_item_btn"
                    ):
                        try:
                            os.remove(selected_path)
                            st.success(f"✅ '{selected_item}' を削除しました")
                            logger.info(f"Deleted item: {selected_path}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 削除に失敗: {e}")
                            logger.error(f"Failed to delete item: {e}")
    else:
        st.info("管理するアイテム画像がありません")
