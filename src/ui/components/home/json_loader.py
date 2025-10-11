import json
import streamlit as st
from typing import Dict, List, Any, Optional
import logging
import os
from pathlib import Path
from config import Paths

logger = logging.getLogger(__name__)


def get_json_files_list() -> List[str]:
    """outputs/jsonディレクトリのJSONファイル一覧を取得"""
    try:
        json_dir = os.path.join(Paths.get_outputs_dir(), "json")
        if not os.path.exists(json_dir):
            return []

        json_files = []
        for file in os.listdir(json_dir):
            if file.endswith(".json"):
                json_files.append(file)

        return sorted(json_files, reverse=True)  # 新しい順にソート
    except Exception as e:
        logger.error(f"Failed to get JSON files list: {e}")
        return []


def load_json_file(filename: str) -> Optional[Dict[str, Any]]:
    """outputs/jsonディレクトリからJSONファイルを読み込み"""
    try:
        json_dir = os.path.join(Paths.get_outputs_dir(), "json")
        file_path = os.path.join(json_dir, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON file {filename}: {e}")
        return None


def validate_json_structure(data: Dict[str, Any]) -> bool:
    """JSONファイルの構造を検証"""
    required_fields = ["all_segments"]
    if not all(field in data for field in required_fields):
        return False

    if not isinstance(data["all_segments"], list):
        return False

    for segment in data["all_segments"]:
        if not isinstance(segment, dict):
            return False

        required_segment_fields = [
            "speaker",
            "text",
            "expression",
            "visible_characters",
        ]
        if not all(field in segment for field in required_segment_fields):
            return False

    return True


def validate_and_clean_data(
    data: Dict[str, Any],
    available_characters: List[str],
    available_backgrounds: List[str],
    available_expressions: List[str],
) -> Dict[str, Any]:
    """JSONデータを検証・クリーニング"""
    cleaned_segments = []

    for segment in data.get("all_segments", []):
        # キャラクター検証
        speaker = segment.get("speaker", "zundamon")
        if speaker not in available_characters:
            logger.warning(f"Unknown speaker '{speaker}', using 'zundamon'")
            speaker = "zundamon"

        # 表情検証
        expression = segment.get("expression", "normal")
        if expression not in available_expressions:
            logger.warning(f"Unknown expression '{expression}', using 'normal'")
            expression = "normal"

        # 表示キャラクター検証・クリーニング
        visible_characters = segment.get("visible_characters", [])
        cleaned_visible_chars = []
        for char in visible_characters:
            if char in available_characters and char != "narrator":
                cleaned_visible_chars.append(char)

        # 話者がナレーター以外で、リストに含まれていない場合は追加
        if speaker != "narrator" and speaker not in cleaned_visible_chars:
            cleaned_visible_chars.append(speaker)

        cleaned_segment = {
            "speaker": speaker,
            "text": segment.get("text", ""),
            "expression": expression,
            "visible_characters": cleaned_visible_chars,
        }
        cleaned_segments.append(cleaned_segment)

    return {**data, "all_segments": cleaned_segments}


def extract_backgrounds_from_json(data: Dict[str, Any]) -> List[str]:
    """JSONデータから使用されている背景名を抽出"""
    backgrounds = set()

    # セクションから背景を抽出
    sections = data.get("sections", [])
    for section in sections:
        scene_background = section.get("scene_background", "default")
        if scene_background:
            backgrounds.add(scene_background)

    # セグメントから背景を抽出（もしあれば）
    all_segments = data.get("all_segments", [])
    for segment in all_segments:
        background = segment.get("background")
        if background:
            backgrounds.add(background)

    # defaultは常に含める
    backgrounds.add("default")

    return sorted(list(backgrounds))


def convert_json_to_conversation_lines(
    data: Dict[str, Any],
    available_characters: List[str] = None,
    available_backgrounds: List[str] = None,
    available_expressions: List[str] = None,
) -> List[Dict[str, Any]]:
    """JSONデータを会話入力UI用のフォーマットに変換"""
    if not validate_json_structure(data):
        raise ValueError("Invalid JSON structure")

    # デフォルト値設定
    if available_characters is None:
        available_characters = ["zundamon", "metan", "tsumugi", "narrator"]
    if available_backgrounds is None:
        available_backgrounds = ["default"]
    if available_expressions is None:
        available_expressions = [
            "normal",
            "happy",
            "sad",
            "angry",
            "surprised",
            "worried",
            "excited",
            "sick",
            "thinking",
            "serious",
        ]

    # データクリーニング
    data = validate_and_clean_data(
        data, available_characters, available_backgrounds, available_expressions
    )

    conversation_lines = []
    sections = data.get("sections", [])
    all_segments = data.get("all_segments", [])

    # セクションの背景情報をマッピング
    section_backgrounds = {}
    if sections:
        for section in sections:
            section_name = section.get("section_name", "")
            scene_background = section.get("scene_background", "default")
            # 背景の検証
            if scene_background not in available_backgrounds:
                logger.warning(
                    f"Unknown background '{scene_background}', using 'default'"
                )
                scene_background = "default"
            section_backgrounds[section_name] = scene_background

    # セグメントを変換
    current_section_idx = 0
    segments_processed = 0
    current_background = "default"

    for segment in all_segments:
        # セクションの背景を決定（セクション情報がある場合）
        if sections and current_section_idx < len(sections):
            section = sections[current_section_idx]
            section_segments = section.get("segments", [])

            if segments_processed >= len(section_segments):
                current_section_idx += 1
                segments_processed = 0
                if current_section_idx < len(sections):
                    current_background = sections[current_section_idx].get(
                        "scene_background", "default"
                    )
            else:
                current_background = section.get("scene_background", "default")
                segments_processed += 1

        # セグメントを変換
        conversation_line = {
            "speaker": segment["speaker"],
            "text": segment["text"],
            "background": current_background,
            "expression": segment["expression"],
            "visible_characters": segment["visible_characters"].copy(),
        }

        conversation_lines.append(conversation_line)

    return conversation_lines


def load_json_to_session_state(
    filename: str,
    available_characters: List[str] = None,
    available_backgrounds: List[str] = None,
    available_expressions: List[str] = None,
) -> Optional[Dict[str, Any]]:
    """JSONファイルをセッション状態に読み込み"""
    try:
        # JSONファイルを読み込み
        data = load_json_file(filename)
        if not data:
            st.error("JSONファイルの読み込みに失敗しました")
            return None

        # 構造を検証
        if not validate_json_structure(data):
            st.error("JSONファイルの構造が正しくありません。required: all_segments")
            return None

        # 会話データに変換（利用可能なオプションを渡す）
        conversation_lines = convert_json_to_conversation_lines(
            data, available_characters, available_backgrounds, available_expressions
        )

        # セッション状態に設定
        st.session_state.conversation_lines = conversation_lines
        st.session_state.loaded_json_data = data  # 背景抽出用にJSONデータを保存

        # メタデータも保存（オプション）
        metadata = {
            "title": data.get("title", "Untitled"),
            "food_name": data.get("food_name", "Unknown"),
            "estimated_duration": data.get("estimated_duration", "Unknown"),
            "total_segments": len(conversation_lines),
        }

        return metadata

    except Exception as e:
        st.error(f"ファイルの読み込みに失敗しました: {str(e)}")
        logger.error(f"File load error: {e}")
        return None


def render_json_selector(
    available_characters: List[str] = None,
    available_backgrounds: List[str] = None,
    available_expressions: List[str] = None,
) -> None:
    """JSONファイル選択機能をレンダリング"""
    st.subheader("JSONファイルから会話を読み込み")

    # JSONファイル一覧を取得
    json_files = get_json_files_list()

    if not json_files:
        st.warning("📂 outputs/jsonディレクトリにJSONファイルが見つかりません")
        st.markdown("---")
        return

    # ファイル選択プルダウン
    selected_file = st.selectbox(
        "会話JSONファイルを選択してください",
        options=[""] + json_files,
        format_func=lambda x: "ファイルを選択..." if x == "" else x,
        help="outputs/jsonディレクトリのJSONファイルから選択できます",
        key="json_selector",
    )

    if selected_file and selected_file != "":
        # ファイル情報を表示
        st.info(f"📄 選択ファイル: {selected_file}")

        # プレビューを表示
        try:
            data = load_json_file(selected_file)
            if data:
                # メタデータ表示
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("タイトル", data.get("title", "N/A"))
                with col2:
                    st.metric("セグメント数", len(data.get("all_segments", [])))
                with col3:
                    st.metric("推定時間", data.get("estimated_duration", "N/A"))

                # 読み込みボタン
                if st.button(
                    "🔄 JSONファイルから会話を読み込み",
                    type="primary",
                    use_container_width=True,
                ):
                    metadata = load_json_to_session_state(
                        selected_file,
                        available_characters,
                        available_backgrounds,
                        available_expressions,
                    )
                    if metadata:
                        st.success(
                            f"✅ 会話を読み込みました！ ({metadata['total_segments']}個のセリフ)"
                        )
                        st.rerun()
            else:
                st.error("ファイルの読み込みに失敗しました")

        except Exception as e:
            st.error(f"ファイルの処理中にエラーが発生しました: {str(e)}")

    st.markdown("---")
