import streamlit as st
import json
import os
import time
import shutil
import tempfile
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


def load_json_file(file_path: Path, max_retries: int = 3, retry_delay: float = 0.2, use_temp_copy: bool = True) -> Optional[Dict[str, Any]]:
    """JSONファイルを読み込み（リトライ＋一時ファイルコピー機能付き）

    Args:
        file_path: JSONファイルのパス
        max_retries: 最大リトライ回数（デフォルト: 3）
        retry_delay: リトライ間隔（秒、デフォルト: 0.2）
        use_temp_copy: 一時ファイルにコピーしてから読み込むか（デフォルト: True、デッドロック回避）

    Returns:
        JSONデータ（Dict）または失敗時にNone
    """
    # ファイルが存在するか確認
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        st.error(f"ファイルが見つかりません: {file_path}")
        return None

    for attempt in range(max_retries):
        tmp_path = None
        try:
            if use_temp_copy:
                # 一時ファイルにコピーしてから読み込む（デッドロック回避）
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
                    tmp_path = tmp_file.name

                # ファイルをコピー
                shutil.copy2(str(file_path), tmp_path)
                logger.debug(f"Copied {file_path.name} to temporary file: {tmp_path}")

                # 一時ファイルから読み込み
                with open(tmp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded JSON file via temp copy: {file_path.name}")
                    return data
            else:
                # 直接読み込み
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded JSON file: {file_path.name}")
                    return data

        except (OSError, IOError) as e:
            # Errno 35 (Resource deadlock avoided) や他のIOエラーをキャッチ
            if attempt < max_retries - 1:
                logger.warning(
                    f"File read attempt {attempt + 1}/{max_retries} failed for {file_path.name}: {e}. Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Failed to load JSON file {file_path.name} after {max_retries} attempts: {e}")
                st.error(f"ファイル読み込みエラー（{max_retries}回リトライ後）: {e}")
                return None

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path.name}: {e}")
            st.error(f"JSON形式エラー: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error loading {file_path.name}: {e}", exc_info=True)
            st.error(f"予期しないエラー: {e}")
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


def save_json_file(file_path: Path, data: Dict[str, Any], max_retries: int = 3, retry_delay: float = 0.2) -> bool:
    """JSONファイルを保存（リトライ機能付き）

    Args:
        file_path: JSONファイルのパス
        data: 保存するJSONデータ
        max_retries: 最大リトライ回数（デフォルト: 3）
        retry_delay: リトライ間隔（秒、デフォルト: 0.2）

    Returns:
        成功時True、失敗時False
    """
    for attempt in range(max_retries):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Successfully saved JSON file: {file_path.name}")
            return True

        except (OSError, IOError) as e:
            # Errno 35 (Resource deadlock avoided) や他のIOエラーをキャッチ
            if attempt < max_retries - 1:
                logger.warning(
                    f"File write attempt {attempt + 1}/{max_retries} failed for {file_path.name}: {e}. Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Failed to save JSON file {file_path.name} after {max_retries} attempts: {e}")
                st.error(f"ファイル保存エラー（{max_retries}回リトライ後）: {e}")
                return False

        except Exception as e:
            logger.error(f"Unexpected error saving {file_path.name}: {e}", exc_info=True)
            st.error(f"予期しないエラー: {e}")
            return False

    return False


def validate_json_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """JSONデータの妥当性チェック"""
    try:
        # Pydanticモデルで検証
        FoodOverconsumptionScript(**data)
        return True, "バリデーション成功"
    except Exception as e:
        return False, f"バリデーションエラー: {str(e)}"


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

    # 表情・表示キャラクター
    col1, col2 = st.columns([1, 2])

    with col1:
        # 表情選択（後方互換性のため維持）
        expressions = Expressions.get_all()
        expression_options = [
            (name, config.display_name) for name, config in expressions.items()
        ]

        expression_index = 0
        if segment.get("expression") in expressions:
            expression_index = list(expressions.keys()).index(segment["expression"])

        expression = st.selectbox(
            "話者の表情",
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

    # 各キャラクターの表情を個別に設定
    st.write("**各キャラクターの表情**")
    character_expressions = segment.get("character_expressions", {})

    # visible_charactersに基づいて表情選択UIを表示
    if visible_characters:
        expr_cols = st.columns(len(visible_characters))
        updated_character_expressions = {}

        for idx, char_name in enumerate(visible_characters):
            with expr_cols[idx]:
                char_display_name = dict(character_options).get(char_name, char_name)

                # デフォルト値の決定
                if char_name in character_expressions:
                    default_expr = character_expressions[char_name]
                elif char_name == speaker:
                    default_expr = expression
                else:
                    default_expr = "normal"

                # 表情選択
                expr_index = 0
                if default_expr in expressions:
                    expr_index = list(expressions.keys()).index(default_expr)

                selected_expr = st.selectbox(
                    f"{char_display_name}",
                    options=[name for name, _ in expression_options],
                    format_func=lambda x: dict(expression_options)[x],
                    index=expr_index,
                    key=f"char_expr_{section_name}_{segment_index}_{char_name}",
                )

                updated_character_expressions[char_name] = selected_expr
    else:
        updated_character_expressions = {}

    return {
        "speaker": speaker,
        "text": text,
        "expression": expression,
        "visible_characters": visible_characters,
        "character_expressions": updated_character_expressions,
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
                "text_for_voicevox": "",
                "expression": "normal",
                "visible_characters": ["zundamon"],
                "character_expressions": {"zundamon": "normal"},
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

    # display_itemの画像チェック
    st.markdown("---")
    st.subheader("🖼️ アイテム画像チェック")

    item_check_result = check_display_item_images(json_data)

    if not item_check_result["item_ids"]:
        st.info("ℹ️ このJSONファイルには display_item が使用されていません。")
    else:
        # 使用されているアイテムID一覧
        st.write(f"**使用されているアイテムID**: {len(item_check_result['item_ids'])}個")

        col1, col2 = st.columns(2)

        with col1:
            # 存在する画像
            if item_check_result["found"]:
                st.success(f"✅ 画像あり ({len(item_check_result['found'])}個)")
                with st.expander("詳細を表示"):
                    for item_id in item_check_result["found"]:
                        st.write(f"- `{item_id}.png` ✓")
            else:
                st.info("存在する画像: なし")

        with col2:
            # 存在しない画像
            if item_check_result["missing"]:
                st.error(f"❌ 画像なし ({len(item_check_result['missing'])}個)")
                with st.expander("詳細を表示", expanded=True):
                    st.warning("以下の画像ファイルを `assets/items/` に配置してください:")
                    for item_id in item_check_result["missing"]:
                        st.write(f"- `{item_id}.png` ⚠️")
            else:
                st.success("✅ すべての画像が揃っています！")

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
