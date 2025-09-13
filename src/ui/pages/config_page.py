import streamlit as st
import json
import os
import sys

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.components.config import (
    ConfigEditor,
    render_app_settings,
    render_subtitle_settings,
    render_ui_settings,
    render_character_settings,
)


def render_config_editor():
    """設定編集ページをレンダリング"""
    st.title("⚙️ 設定エディタ")
    st.markdown("アプリケーションの各種設定値を編集できます。")

    editor = ConfigEditor()
    config = editor.load_user_config()

    # タブで設定を分割
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🎬 動画設定", "📝 字幕設定", "🖥️ UI設定", "🎭 キャラクター設定"]
    )

    with tab1:
        render_app_settings(config)

    with tab2:
        render_subtitle_settings(config)

    with tab3:
        render_ui_settings(config)

    with tab4:
        render_character_settings(config)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💾 設定を保存", type="primary", use_container_width=True):
            editor.save_user_config(config)
            editor.apply_config_to_session(config)
            st.success("設定を保存しました！")
            st.rerun()

    with col2:
        if st.button("🔄 デフォルトに戻す", use_container_width=True):
            config = editor.get_default_config()
            editor.save_user_config(config)
            editor.apply_config_to_session(config)
            st.success("デフォルト設定に戻しました！")
            st.rerun()

    with col3:
        if st.button("📥 現在の設定をダウンロード", use_container_width=True):
            config_json = json.dumps(config, indent=2, ensure_ascii=False)
            st.download_button(
                label="設定ファイルをダウンロード",
                data=config_json,
                file_name="zundan_config.json",
                mime="application/json",
                use_container_width=True,
            )


def render_config_page():
    """Config Editor ページをレンダリング"""
    render_config_editor()
