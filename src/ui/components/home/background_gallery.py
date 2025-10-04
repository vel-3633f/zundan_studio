import streamlit as st
from typing import List
import os
from config import Paths, Backgrounds


def render_background_gallery(background_options: List[str]) -> None:
    """背景画像の一覧を表示"""
    st.subheader("📸 利用可能な背景一覧")

    if not background_options or (len(background_options) == 1 and background_options[0] == "default"):
        st.info("背景画像が見つかりません")
        return

    # 背景画像ディレクトリのパスを取得
    backgrounds_dir = Paths.get_backgrounds_dir()

    # 利用可能な画像拡張子
    valid_extensions = Backgrounds.get_supported_extensions()

    # グリッドレイアウトで背景を表示（3列）
    cols_per_row = 3

    # 背景オプションをフィルタリング（defaultを除外）
    display_backgrounds = [bg for bg in background_options if bg != "default"]

    if not display_backgrounds:
        st.info("カスタム背景画像はありません")
        return

    # 行ごとに処理
    for i in range(0, len(display_backgrounds), cols_per_row):
        cols = st.columns(cols_per_row)

        for j, bg_name in enumerate(display_backgrounds[i:i + cols_per_row]):
            with cols[j]:
                # 背景画像ファイルを探す
                image_path = None
                for ext in valid_extensions:
                    potential_path = os.path.join(backgrounds_dir, f"{bg_name}{ext}")
                    if os.path.exists(potential_path):
                        image_path = potential_path
                        break

                # 画像を表示
                if image_path and os.path.exists(image_path):
                    st.image(
                        image_path,
                        caption=Backgrounds.get_display_name(bg_name),
                        use_container_width=True
                    )
                else:
                    # 画像が見つからない場合はプレースホルダー
                    st.info(f"🖼️ {Backgrounds.get_display_name(bg_name)}")

    st.markdown("---")
