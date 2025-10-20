"""セクションBGM編集コンポーネント

ホームページでセクションごとのBGM設定を編集できるUIを提供
"""

import streamlit as st
from typing import Dict, List, Any
import logging
from config.bgm_library import BGM_LIBRARY, get_bgm_track

logger = logging.getLogger(__name__)


def get_bgm_options() -> List[tuple]:
    """BGM選択肢を取得（id, 表示名）のタプルリスト"""
    options = []
    for bgm_id, track in BGM_LIBRARY.items():
        display_name = f"{track.name} ({track.mood})"
        options.append((bgm_id, display_name))
    return options


def render_section_bgm_editor() -> None:
    """セクションごとのBGM編集UIを表示"""

    # セッション状態にセクションデータがない場合は何もしない
    if "loaded_json_data" not in st.session_state:
        return

    data = st.session_state.loaded_json_data

    # sectionsがない場合は何もしない
    if "sections" not in data or not data["sections"]:
        return

    st.subheader("🎵 セクションBGM設定")

    # セクションBGM設定を初期化（まだ無い場合、またはセクション数が変わった場合）
    current_section_count = len(data["sections"])
    need_reinit = False

    if "section_bgm_settings" not in st.session_state:
        need_reinit = True
    else:
        # 既存の設定があるセクション数を確認
        existing_section_count = len([k for k in st.session_state.section_bgm_settings.keys() if k.startswith("section_")])
        if existing_section_count != current_section_count:
            need_reinit = True
            logger.info(f"Section count changed from {existing_section_count} to {current_section_count}, re-initializing")

    if need_reinit:
        st.session_state.section_bgm_settings = {}
        for idx, section in enumerate(data["sections"]):
            section_key = f"section_{idx}"
            st.session_state.section_bgm_settings[section_key] = {
                "bgm_id": section.get("bgm_id", "none"),
                "bgm_volume": section.get("bgm_volume", 0.25),
            }
        logger.info(f"Initialized section_bgm_settings for {current_section_count} sections")

    bgm_options = get_bgm_options()

    # エクスパンダーでセクションごとに表示
    for idx, section in enumerate(data["sections"]):
        section_key = f"section_{idx}"
        section_name = section.get("section_name", f"セクション {idx + 1}")
        segment_count = len(section.get("segments", []))

        with st.expander(f"📝 {section_name} ({segment_count}セリフ)", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                # BGM選択
                current_bgm_id = st.session_state.section_bgm_settings[section_key]["bgm_id"]

                # 現在のBGMのインデックスを取得
                current_index = 0
                for i, (bgm_id, _) in enumerate(bgm_options):
                    if bgm_id == current_bgm_id:
                        current_index = i
                        break

                selected_bgm = st.selectbox(
                    "BGM選択",
                    options=[opt[0] for opt in bgm_options],
                    format_func=lambda x: next(opt[1] for opt in bgm_options if opt[0] == x),
                    key=f"bgm_select_{section_key}",
                    index=current_index,
                )

                # セッション状態を更新
                st.session_state.section_bgm_settings[section_key]["bgm_id"] = selected_bgm

                # BGMの説明を表示
                if selected_bgm != "none":
                    track = get_bgm_track(selected_bgm)
                    if track:
                        st.caption(f"💡 {track.description}")

            with col2:
                # 音量調整
                current_volume = st.session_state.section_bgm_settings[section_key]["bgm_volume"]

                volume = st.slider(
                    "音量",
                    min_value=0.0,
                    max_value=1.0,
                    value=current_volume,
                    step=0.05,
                    key=f"bgm_volume_{section_key}",
                )

                # セッション状態を更新
                st.session_state.section_bgm_settings[section_key]["bgm_volume"] = volume

    # 設定情報の表示
    st.caption("💡 各セクションに異なるBGMを設定できます。動画生成時にこの設定が適用されます。")


def apply_bgm_settings_to_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """セクションデータにBGM設定を適用

    Args:
        sections: セクションデータのリスト

    Returns:
        BGM設定が適用されたセクションデータ
    """
    if "section_bgm_settings" not in st.session_state:
        return sections

    updated_sections = []
    for idx, section in enumerate(sections):
        section_key = f"section_{idx}"

        # セクションのコピーを作成
        updated_section = section.copy()

        # BGM設定を適用
        if section_key in st.session_state.section_bgm_settings:
            bgm_settings = st.session_state.section_bgm_settings[section_key]
            updated_section["bgm_id"] = bgm_settings["bgm_id"]
            updated_section["bgm_volume"] = bgm_settings["bgm_volume"]

        updated_sections.append(updated_section)

    return updated_sections
