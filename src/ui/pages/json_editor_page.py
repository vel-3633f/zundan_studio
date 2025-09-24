import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.models.food_over import (
    FoodOverconsumptionScript,
)
from config.characters import Characters, Expressions
from src.utils.logger import get_logger

logger = get_logger(__name__)

JSON_OUTPUT_DIR = Path("outputs/json")


def get_json_files() -> List[Path]:
    """outputs/jsonディレクトリ内のJSONファイル一覧を取得"""
    if not JSON_OUTPUT_DIR.exists():
        return []

    json_files = list(JSON_OUTPUT_DIR.glob("*.json"))
    return sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """JSONファイルを読み込み"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"JSONファイル読み込みエラー: {e}")
        st.error(f"ファイル読み込みエラー: {e}")
        return None


def save_json_file(file_path: Path, data: Dict[str, Any]) -> bool:
    """JSONファイルを保存"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"JSONファイル保存エラー: {e}")
        st.error(f"ファイル保存エラー: {e}")
        return False


def validate_json_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """JSONデータの妥当性チェック"""
    try:
        # Pydanticモデルで検証
        FoodOverconsumptionScript(**data)
        return True, "バリデーション成功"
    except Exception as e:
        return False, f"バリデーションエラー: {str(e)}"


def render_segment_editor(
    segment: Dict[str, Any], segment_index: int, section_name: str
) -> Dict[str, Any]:
    """単一セグメントの編集UI"""

    # キャラクター設定
    characters = Characters.get_all()
    character_options = [
        (name, config.display_name) for name, config in characters.items()
    ]

    # 話者とセリフを横並びで表示
    speaker_col, text_col = st.columns([1, 3])

    with speaker_col:
        # 話者選択
        speaker_index = 0
        if segment.get("speaker") in characters:
            speaker_index = list(characters.keys()).index(segment["speaker"])

        speaker = st.selectbox(
            "話者",
            options=[name for name, _ in character_options],
            format_func=lambda x: dict(character_options)[x],
            index=speaker_index,
            key=f"speaker_{section_name}_{segment_index}",
        )

    with text_col:
        # セリフ編集
        text = st.text_area(
            "セリフ",
            value=segment.get("text", ""),
            key=f"text_{section_name}_{segment_index}",
            height=60,
        )

    # 表情・表示キャラクター・アイテムを横並びで表示
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        # 表情選択
        expressions = Expressions.get_all()
        expression_options = [
            (name, config.display_name) for name, config in expressions.items()
        ]

        expression_index = 0
        if segment.get("expression") in expressions:
            expression_index = list(expressions.keys()).index(segment["expression"])

        expression = st.selectbox(
            "表情",
            options=[name for name, _ in expression_options],
            format_func=lambda x: dict(expression_options)[x],
            index=expression_index,
            key=f"expression_{section_name}_{segment_index}",
        )

    with col2:
        # 表示キャラクター選択（複数選択）
        visible_characters = st.multiselect(
            "表示キャラクター",
            options=[name for name, _ in character_options],
            default=segment.get("visible_characters", []),
            format_func=lambda x: dict(character_options)[x],
            key=f"visible_{section_name}_{segment_index}",
        )

    with col3:
        # ずんだもんのアイテム設定のみ表示
        zundamon_item = "none"
        if "zundamon" in visible_characters:
            zundamon_item = st.text_input(
                "ずんだもんアイテム",
                value=segment.get("character_items", {}).get("zundamon", "none"),
                key=f"item_zundamon_{section_name}_{segment_index}",
            )

    # キャラクターアイテム辞書を構築（ずんだもん以外は自動でnone）
    character_items = {}
    for char in visible_characters:
        if char == "zundamon":
            character_items[char] = zundamon_item
        else:
            character_items[char] = "none"

    return {
        "speaker": speaker,
        "text": text,
        "expression": expression,
        "visible_characters": visible_characters,
        "character_items": character_items,
    }


def render_section_editor(
    section: Dict[str, Any], section_index: int
) -> Dict[str, Any]:
    """セクション編集UI"""
    with st.expander(
        f"📁 セクション {section_index + 1}: {section.get('section_name', 'Unknown')}",
        expanded=True,
    ):
        # セクション名
        section_name = st.text_input(
            "セクション名",
            value=section.get("section_name", ""),
            key=f"section_name_{section_index}",
        )

        # 背景シーン
        scene_background = st.text_input(
            "背景シーン",
            value=section.get("scene_background", ""),
            key=f"scene_background_{section_index}",
        )

        # セグメント編集
        segments = section.get("segments", [])
        edited_segments = []

        st.write("### セグメント")

        for seg_index, segment in enumerate(segments):
            with st.container():
                edited_segment = render_segment_editor(
                    segment, seg_index, f"sec{section_index}"
                )
                edited_segments.append(edited_segment)

                # セグメント削除ボタン
                if st.button(
                    f"🗑️ セグメント {seg_index + 1} を削除",
                    key=f"del_segment_{section_index}_{seg_index}",
                ):
                    st.session_state[f"delete_segment_{section_index}_{seg_index}"] = (
                        True
                    )
                    st.rerun()

                st.divider()

        # セグメント追加ボタン
        if st.button(f"➕ セグメントを追加", key=f"add_segment_{section_index}"):
            new_segment = {
                "speaker": "zundamon",
                "text": "",
                "expression": "normal",
                "visible_characters": ["zundamon"],
                "character_items": {"zundamon": "none"},
            }
            segments.append(new_segment)
            st.rerun()

        return {
            "section_name": section_name,
            "scene_background": scene_background,
            "segments": edited_segments,
        }


def render_json_editor():
    """JSON編集ページのメイン関数"""
    st.title("📝 JSON脚本エディタ")
    st.markdown("生成されたJSON脚本ファイルを選択して編集できます。")

    # JSONファイル一覧取得
    json_files = get_json_files()

    if not json_files:
        st.warning("📁 outputs/jsonディレクトリにJSONファイルが見つかりません。")
        st.info("先に「記事紹介」ページで動画脚本を生成してください。")
        return

    # ファイル選択
    file_options = [(f.name, f) for f in json_files]
    selected_file_name = st.selectbox(
        "編集するJSONファイルを選択",
        options=[name for name, _ in file_options],
        index=0,
    )

    selected_file = dict(file_options)[selected_file_name]

    # ファイル情報表示
    st.info(f"📄 選択中: {selected_file.name}")

    # JSONデータ読み込み
    json_data = load_json_file(selected_file)
    if json_data is None:
        return

    # 編集フォーム
    st.markdown("---")
    st.subheader("📋 基本情報")

    # タイトル編集
    title = st.text_input("タイトル", value=json_data.get("title", ""))

    # 食べ物名編集
    food_name = st.text_input("食べ物名", value=json_data.get("food_name", ""))

    # 推定時間編集
    estimated_duration = st.text_input(
        "推定時間", value=json_data.get("estimated_duration", "")
    )

    # セクション編集
    st.markdown("---")
    st.subheader("🎬 セクション編集")

    sections = json_data.get("sections", [])
    edited_sections = []

    for section_index, section in enumerate(sections):
        edited_section = render_section_editor(section, section_index)
        edited_sections.append(edited_section)

    # セクション追加ボタン
    if st.button("➕ セクションを追加"):
        new_section = {
            "section_name": "新しいセクション",
            "scene_background": "default",
            "segments": [],
        }
        sections.append(new_section)
        st.rerun()

    # 保存・バリデーションボタン
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💾 保存", type="primary", use_container_width=True):
            # 編集データを構築
            updated_data = {
                "title": title,
                "food_name": food_name,
                "estimated_duration": estimated_duration,
                "sections": edited_sections,
                "all_segments": [],  # セクションから自動生成
            }

            # all_segments生成
            all_segments = []
            for section in edited_sections:
                all_segments.extend(section["segments"])
            updated_data["all_segments"] = all_segments

            # バリデーション
            is_valid, validation_message = validate_json_data(updated_data)

            if is_valid:
                # 保存
                if save_json_file(selected_file, updated_data):
                    st.success("✅ 保存しました！")
                    st.rerun()
            else:
                st.error(f"❌ {validation_message}")

    with col2:
        if st.button("🔍 バリデーションチェック", use_container_width=True):
            # バリデーションのみ実行
            test_data = {
                "title": title,
                "food_name": food_name,
                "estimated_duration": estimated_duration,
                "sections": edited_sections,
                "all_segments": [],
            }

            # all_segments生成
            all_segments = []
            for section in edited_sections:
                all_segments.extend(section["segments"])
            test_data["all_segments"] = all_segments

            is_valid, validation_message = validate_json_data(test_data)

            if is_valid:
                st.success("✅ バリデーション成功")
            else:
                st.error(f"❌ {validation_message}")

    with col3:
        if st.button("📥 JSONをダウンロード", use_container_width=True):
            # 現在の編集内容をダウンロード
            download_data = {
                "title": title,
                "food_name": food_name,
                "estimated_duration": estimated_duration,
                "sections": edited_sections,
                "all_segments": [],
            }

            # all_segments生成
            all_segments = []
            for section in edited_sections:
                all_segments.extend(section["segments"])
            download_data["all_segments"] = all_segments

            json_str = json.dumps(download_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="JSONファイルをダウンロード",
                data=json_str,
                file_name=f"edited_{selected_file_name}",
                mime="application/json",
                use_container_width=True,
            )


def render_json_editor_page():
    """JSON編集ページをレンダリング"""
    render_json_editor()
