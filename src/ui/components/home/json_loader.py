import json
import streamlit as st
from typing import Dict, List, Any, Optional
import logging
import os
import time
import shutil
import tempfile
from pathlib import Path
from config import Paths

logger = logging.getLogger(__name__)


def check_display_item_images(data: Dict[str, Any]) -> Dict[str, Any]:
    """display_itemで使用されている画像の存在チェック

    Args:
        data: JSONデータ

    Returns:
        {
            "item_ids": List[str],  # 使用されているアイテムID一覧
            "missing": List[str],   # 存在しない画像のアイテムID
            "found": List[str],     # 存在する画像のアイテムID
        }
    """
    item_ids = set()
    items_dir = Path("assets/items")

    # 全セクションのセグメントから display_item を収集
    sections = data.get("sections", [])
    for section in sections:
        segments = section.get("segments", [])
        for segment in segments:
            display_item = segment.get("display_item")
            if display_item and display_item != "none":
                item_ids.add(display_item)

    # 各アイテムIDの画像ファイルが存在するかチェック
    missing = []
    found = []

    for item_id in sorted(item_ids):
        # assets/items/ 配下を再帰的に探索
        image_found = False
        if items_dir.exists():
            for root, dirs, files in os.walk(items_dir):
                if f"{item_id}.png" in files:
                    image_found = True
                    break

        if image_found:
            found.append(item_id)
        else:
            missing.append(item_id)

    return {
        "item_ids": sorted(item_ids),
        "missing": missing,
        "found": found,
    }


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


def load_json_file(filename: str, max_retries: int = 3, retry_delay: float = 0.2, use_temp_copy: bool = True) -> Optional[Dict[str, Any]]:
    """outputs/jsonディレクトリからJSONファイルを読み込み（リトライ＋一時ファイルコピー機能付き）

    Args:
        filename: JSONファイル名
        max_retries: 最大リトライ回数（デフォルト: 3）
        retry_delay: リトライ間隔（秒、デフォルト: 0.2）
        use_temp_copy: 一時ファイルにコピーしてから読み込むか（デフォルト: True、デッドロック回避）

    Returns:
        JSONデータ（Dict）または失敗時にNone
    """
    json_dir = os.path.join(Paths.get_outputs_dir(), "json")
    file_path = os.path.join(json_dir, filename)

    # ファイルが存在するか確認
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    for attempt in range(max_retries):
        tmp_path = None
        try:
            if use_temp_copy:
                # 一時ファイルにコピーしてから読み込む（デッドロック回避）
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
                    tmp_path = tmp_file.name

                # ファイルをコピー（バイナリモードで高速コピー）
                shutil.copy2(file_path, tmp_path)
                logger.debug(f"Copied {filename} to temporary file: {tmp_path}")

                # 一時ファイルから読み込み
                with open(tmp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded JSON file via temp copy: {filename}")
                    return data
            else:
                # 直接読み込み
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded JSON file: {filename}")
                    return data

        except (OSError, IOError) as e:
            # Errno 35 (Resource deadlock avoided) や他のIOエラーをキャッチ
            if attempt < max_retries - 1:
                logger.warning(
                    f"File read attempt {attempt + 1}/{max_retries} failed for {filename}: {e}. Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Failed to load JSON file {filename} after {max_retries} attempts: {e}")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {filename}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error loading {filename}: {e}", exc_info=True)
            return None

        finally:
            # 一時ファイルをクリーンアップ
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                    logger.debug(f"Cleaned up temporary file: {tmp_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file {tmp_path}: {cleanup_error}")

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

        # character_expressionsの処理（後方互換性）
        character_expressions = segment.get("character_expressions", {})

        # character_expressionsが空の場合、expressionから自動生成
        if not character_expressions and cleaned_visible_chars:
            character_expressions = {}
            for char in cleaned_visible_chars:
                if char == speaker:
                    character_expressions[char] = expression
                else:
                    character_expressions[char] = "normal"

        cleaned_segment = {
            "speaker": speaker,
            "text": segment.get("text", ""),
            "text_for_voicevox": segment.get("text_for_voicevox", segment.get("text", "")),
            "expression": expression,
            "visible_characters": cleaned_visible_chars,
            "character_expressions": character_expressions,
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

            # 現在のセクションの背景を使用
            current_background = section.get("scene_background", "default")

        # セグメントを変換
        conversation_line = {
            "speaker": segment["speaker"],
            "text": segment["text"],
            "text_for_voicevox": segment.get("text_for_voicevox", segment["text"]),
            "background": current_background,
            "expression": segment["expression"],
            "visible_characters": segment["visible_characters"].copy(),
            "character_expressions": segment.get("character_expressions", {}).copy(),
        }

        conversation_lines.append(conversation_line)

        # セグメントを処理した後にカウントアップし、次のセクションに移るか判定
        if sections and current_section_idx < len(sections):
            segments_processed += 1
            section = sections[current_section_idx]
            section_segments = section.get("segments", [])

            # このセクションの全セグメントを処理し終えたら次のセクションへ
            if segments_processed >= len(section_segments):
                current_section_idx += 1
                segments_processed = 0

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

        # JSONから背景情報を抽出
        json_backgrounds = extract_backgrounds_from_json(data)

        # 抽出した背景をavailable_backgroundsとして使用
        if json_backgrounds:
            available_backgrounds = json_backgrounds
            logger.info(f"Extracted {len(json_backgrounds)} backgrounds from JSON: {json_backgrounds}")

        # 会話データに変換（利用可能なオプションを渡す）
        conversation_lines = convert_json_to_conversation_lines(
            data, available_characters, available_backgrounds, available_expressions
        )

        # セッション状態に設定
        st.session_state.conversation_lines = conversation_lines
        st.session_state.loaded_json_data = data  # 背景抽出用にJSONデータを保存

        # section_bgm_settingsをクリアして再初期化を促す
        if "section_bgm_settings" in st.session_state:
            del st.session_state.section_bgm_settings
            logger.info("Cleared section_bgm_settings to trigger re-initialization")

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

                # display_itemの画像チェック
                st.markdown("---")
                st.write("**🖼️ アイテム画像チェック**")

                item_check_result = check_display_item_images(data)

                if not item_check_result["item_ids"]:
                    st.info("ℹ️ このJSONファイルには display_item が使用されていません。")
                else:
                    # 使用されているアイテムID一覧
                    st.write(f"使用アイテムID: {len(item_check_result['item_ids'])}個")

                    col_found, col_missing = st.columns(2)

                    with col_found:
                        # 存在する画像
                        if item_check_result["found"]:
                            st.success(f"✅ 画像あり: {len(item_check_result['found'])}個")
                            with st.expander("詳細"):
                                for item_id in item_check_result["found"]:
                                    st.write(f"- `{item_id}.png` ✓")
                        else:
                            st.info("存在する画像: なし")

                    with col_missing:
                        # 存在しない画像
                        if item_check_result["missing"]:
                            st.error(f"❌ 画像なし: {len(item_check_result['missing'])}個")
                            with st.expander("詳細", expanded=True):
                                st.warning("以下の画像を `assets/items/` に配置してください:")
                                for item_id in item_check_result["missing"]:
                                    st.write(f"- `{item_id}.png` ⚠️")
                        else:
                            st.success("✅ すべての画像が揃っています！")

                st.markdown("---")

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
