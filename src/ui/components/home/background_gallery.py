import streamlit as st
from typing import List, Dict, Optional
import os
from config import Paths, Backgrounds
from PIL import Image


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
    st.subheader("📋 背景画像読み込み状態チェック")

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

    st.markdown("---")
