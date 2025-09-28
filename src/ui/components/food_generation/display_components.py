"""Display components for food generation UI"""

import streamlit as st
import json
from typing import Dict, List, Any
from pathlib import Path

from src.models.food_over import FoodOverconsumptionScript
from config.app import SYSTEM_PROMPT_FILE, USER_PROMPT_FILE
from src.utils.logger import get_logger
from .data_models import Characters, Expressions

logger = get_logger(__name__)


def display_json_debug(data: Any, title: str = "JSON Debug"):
    """JSONデータをデバッグ用に表示する（大きなJSONに対応）"""
    with st.expander(f"🔍 {title}", expanded=False):
        # データの準備
        if isinstance(data, (dict, list)):
            json_data = data
        elif hasattr(data, "model_dump"):
            json_data = data.model_dump()
        else:
            json_data = data

        try:
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
            json_size = len(json_str.encode("utf-8"))

            # サイズ情報を表示
            size_mb = json_size / (1024 * 1024)
            if size_mb > 1:
                st.info(f"📊 JSONサイズ: {size_mb:.2f} MB ({json_size:,} bytes)")
            else:
                size_kb = json_size / 1024
                st.info(f"📊 JSONサイズ: {size_kb:.1f} KB ({json_size:,} bytes)")

            # 大きなJSONの場合の表示オプション
            if json_size > 50000:  # 50KB以上の場合
                st.warning("⚠️ 大きなJSONファイルです。表示方法を選択してください。")

                # 表示オプション
                display_option = st.radio(
                    "表示方法を選択:",
                    ["要約表示", "セクション別表示", "完全表示", "ダウンロードのみ"],
                    key=f"json_display_option_{hash(str(json_data))}",
                )

                if display_option == "要約表示":
                    # 基本情報のみ表示
                    summary = {}
                    if isinstance(json_data, dict):
                        for key, value in json_data.items():
                            if isinstance(value, list):
                                summary[key] = f"[{len(value)} items]"
                            elif isinstance(value, dict):
                                summary[key] = f"{{dict with {len(value)} keys}}"
                            else:
                                summary[key] = value
                    st.json(summary)

                elif display_option == "セクション別表示":
                    # セクションごとに表示
                    if isinstance(json_data, dict) and "sections" in json_data:
                        # メタデータ
                        metadata = {
                            k: v for k, v in json_data.items() if k != "sections"
                        }
                        st.subheader("📋 メタデータ")
                        st.json(metadata)

                        # セクションごと
                        st.subheader("📑 セクション")
                        for i, section in enumerate(json_data.get("sections", [])):
                            with st.expander(
                                f"セクション {i+1}: {section.get('section_name', 'Unknown')}"
                            ):
                                st.json(section)
                    else:
                        st.json(json_data)

                elif display_option == "完全表示":
                    # st.codeを使用して完全表示
                    st.code(json_str, language="json")

                elif display_option == "ダウンロードのみ":
                    st.info("💾 ダウンロードボタンのみ表示")

                # ダウンロードボタンを常に表示
                st.download_button(
                    label="📥 JSONファイルをダウンロード",
                    data=json_str,
                    file_name=f"{title.replace(' ', '_')}.json",
                    mime="application/json",
                )

            else:
                # 小さなJSONの場合は通常通り表示
                st.json(json_data)

        except Exception as e:
            logger.error(f"JSON変換エラー: {e}")
            st.error(f"JSON変換エラー: {e}")
            st.text(str(data))


def display_raw_llm_output(output: str, title: str = "LLM Raw Output"):
    """LLMの生出力を表示する"""
    with st.expander(f"🤖 {title}", expanded=False):
        st.code(output, language="json")


def display_search_results_debug(search_results: Dict[str, List[str]]):
    """検索結果をデバッグ用に表示する"""
    with st.expander("🔍 Tavily検索結果", expanded=False):
        sections = [
            ("overeating", "食べ過ぎに関する検索結果"),
            ("benefits", "メリットに関する検索結果"),
            ("disadvantages", "デメリットに関する検索結果"),
        ]

        for key, title in sections:
            st.subheader(title)
            if search_results.get(key):
                for i, content in enumerate(search_results[key], 1):
                    st.text_area(f"結果 {i}", content, height=100, key=f"{key}_{i}")
            else:
                st.info("検索結果が見つかりませんでした")


def display_scene_and_items_info(data: Dict):
    """シーンとアイテム情報を表示する"""
    st.markdown("### 🎨 シーン・アイテム情報")

    sections = data.get("sections", [])
    if not sections:
        st.info("シーン・アイテム情報が見つかりませんでした")
        return

    # セクション別のシーン情報を取得
    section_scenes = {}
    character_items_all = {}

    for section in sections:
        section_name = section.get("section_name", "Unknown")
        scene_background = section.get("scene_background", "")
        section_scenes[section_name] = scene_background

        # セクション内のアイテム情報を収集
        for segment in section.get("segments", []):
            if "character_items" in segment and segment["character_items"]:
                for char, item in segment["character_items"].items():
                    if char not in character_items_all:
                        character_items_all[char] = set()
                    character_items_all[char].add(item)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎬 セクション別シーン")
        if section_scenes:
            for section_name, scene in section_scenes.items():
                st.write(f"**{section_name}**: {scene}")
        else:
            st.info("シーン情報が見つかりませんでした")

    with col2:
        st.subheader("🎯 キャラクター別アイテム")
        if character_items_all:
            for char, items in character_items_all.items():
                char_display = Characters.get_display_name(char)
                st.write(f"**{char_display}**:")
                for item in sorted(items):
                    st.write(f"  • {item}")
        else:
            st.info("アイテム情報が見つかりませんでした")

    # 詳細なJSON表示
    with st.expander("🔍 シーン・アイテム詳細情報（JSON）", expanded=False):
        scene_items_data = {
            "section_scenes": section_scenes,
            "character_items": {
                char: list(items) for char, items in character_items_all.items()
            },
            "section_details": [
                {
                    "section_name": section.get("section_name", "Unknown"),
                    "scene_background": section.get("scene_background", ""),
                    "segment_count": len(section.get("segments", [])),
                }
                for section in sections
            ],
        }
        st.json(scene_items_data)


def merge_short_segments(segments: List[Dict]) -> List[Dict]:
    """短いセリフを結合する処理"""
    if not segments:
        return []

    merged = []
    current_segment = None

    for segment in segments:
        text_length = len(segment.get("text", ""))

        # 30文字以下の短いセリフで、同じキャラクターの場合は結合を検討
        if (
            text_length <= 30
            and current_segment
            and current_segment.get("speaker") == segment.get("speaker")
            and len(current_segment.get("text", "")) <= 50
        ):  # 結合後も適度な長さに

            # テキストを結合
            current_segment["text"] += segment.get("text", "")
            current_segment["is_merged"] = True
        else:
            # 前のセグメントがあれば追加
            if current_segment:
                merged.append(current_segment)

            # 新しいセグメントを開始
            current_segment = segment.copy()

    # 最後のセグメントを追加
    if current_segment:
        merged.append(current_segment)

    return merged


def display_food_script_preview(script_data: FoodOverconsumptionScript):
    """食べ物摂取過多動画脚本プレビューを表示（改良版）"""
    from .utils import estimate_video_duration

    try:
        data = script_data.model_dump()
    except Exception as e:
        logger.error(f"スクリプトデータの変換エラー: {e}")
        st.error("スクリプトデータの読み込みに失敗しました")
        return

    if not data or "all_segments" not in data:
        logger.warning("表示するスクリプトデータが不正です")
        st.warning("スクリプトデータが不完全です")
        return

    st.subheader("🍽️ 食べ物摂取過多動画脚本プレビュー")

    # YouTubeタイトル表示
    title = data.get("title", "未設定")
    st.metric("YouTubeタイトル", title)

    # 動画情報表示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("対象食品", data.get("food_name", "未設定"))
    with col2:
        duration = data.get("estimated_duration", "未計算")
        if duration == "未計算":
            try:
                duration = estimate_video_duration(data["all_segments"])
            except Exception as e:
                logger.warning(f"動画時間の推定に失敗: {e}")
                duration = "推定不可"
        st.metric("推定時間", duration)
    with col3:
        st.metric("総セリフ数", len(data.get("all_segments", [])))

    # シーン・アイテム情報表示
    display_scene_and_items_info(data)

    # セクション別表示
    sections = data.get("sections", [])
    if not sections:
        st.warning("セクション情報が見つかりません")
        return

    st.markdown("### 📋 セクション構成")

    for i, section in enumerate(sections):
        section_name = section.get("section_name", f"セクション{i+1}")
        scene_background = section.get("scene_background", "未設定")
        segments = section.get("segments", [])

        # セリフを結合処理
        merged_segments = merge_short_segments(segments)

        with st.expander(
            f"**{i+1}. {section_name}** ({len(merged_segments)}セリフ) - 🎬 {scene_background}",
            expanded=i == 0,  # 最初のセクションのみ展開
        ):
            st.info(f"🎬 シーン: {scene_background}")

            if not merged_segments:
                st.warning("このセクションにはセリフがありません")
                continue

            for j, segment in enumerate(merged_segments):
                try:
                    text = segment.get("text", "")
                    text_length = len(text)
                    length_color = "🟢" if text_length <= 30 else "🔴"

                    speaker = segment.get("speaker", "unknown")
                    expression = segment.get("expression", "normal")

                    # 表示名を取得（エラーハンドリング付き）
                    try:
                        speaker_name = Characters.get_display_name(speaker)
                    except Exception:
                        speaker_name = speaker

                    try:
                        expression_name = Expressions.get_display_name(expression)
                    except Exception:
                        expression_name = expression

                    # セリフ情報の表示
                    is_merged = segment.get("is_merged", False)
                    if is_merged:
                        st.markdown(
                            f"**{j+1}. {speaker_name}** {expression_name} 🔗({text_length}文字・結合)"
                        )
                    else:
                        st.markdown(
                            f"**{j+1}. {speaker_name}** {expression_name} {length_color}({text_length}文字)"
                        )

                    # セリフテキスト表示
                    st.write(f"💬 {text}")

                    # 背景情報表示
                    background = segment.get("background")
                    if background:
                        st.caption(f"🖼️ 背景: {background}")

                    # アイテム情報表示
                    character_items = segment.get("character_items", {})
                    if character_items:
                        items_parts = []
                        for char, item in character_items.items():
                            if item and item != "none":
                                try:
                                    char_display = Characters.get_display_name(char)
                                except Exception:
                                    char_display = char
                                items_parts.append(f"{char_display}: {item}")

                        if items_parts:
                            items_text = ", ".join(items_parts)
                            st.caption(f"🎯 アイテム: {items_text}")

                    # セリフ間の区切り線（最後以外）
                    if j < len(merged_segments) - 1:
                        st.markdown("---")

                except Exception as e:
                    logger.error(
                        f"セリフ表示エラー (セクション{i+1}, セリフ{j+1}): {e}"
                    )
                    st.error(f"セリフ{j+1}の表示でエラーが発生しました")

    logger.info("脚本プレビュー表示完了")


def display_prompt_file_status():
    """プロンプトファイルの状態を表示"""
    with st.expander("📄 プロンプトファイル設定", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**システムプロンプト**")
            if SYSTEM_PROMPT_FILE.exists():
                st.success(f"✅ {SYSTEM_PROMPT_FILE}")
                file_size = SYSTEM_PROMPT_FILE.stat().st_size
                st.caption(f"ファイルサイズ: {file_size} bytes")
                logger.debug(f"システムプロンプトファイル存在確認: {file_size} bytes")
            else:
                st.error(f"❌ ファイルが見つかりません: {SYSTEM_PROMPT_FILE}")
                logger.warning(
                    f"システムプロンプトファイルが見つかりません: {SYSTEM_PROMPT_FILE}"
                )

        with col2:
            st.write("**ユーザープロンプト**")
            if USER_PROMPT_FILE.exists():
                st.success(f"✅ {USER_PROMPT_FILE}")
                file_size = USER_PROMPT_FILE.stat().st_size
                st.caption(f"ファイルサイズ: {file_size} bytes")
                logger.debug(f"ユーザープロンプトファイル存在確認: {file_size} bytes")
            else:
                st.error(f"❌ ファイルが見つかりません: {USER_PROMPT_FILE}")
                logger.warning(
                    f"ユーザープロンプトファイルが見つかりません: {USER_PROMPT_FILE}"
                )

        st.info("💡 プロンプトファイルを編集することで、AIの動作をカスタマイズできます")


def display_debug_section():
    """デバッグ情報セクションを表示"""
    if (
        hasattr(st.session_state, "last_generated_json")
        or hasattr(st.session_state, "last_llm_output")
        or hasattr(st.session_state, "last_search_results")
    ):
        st.subheader("🔧 デバッグ情報")

        debug_mode = st.checkbox("デバッグモードを有効にする", value=False)

        if debug_mode:
            logger.debug("デバッグモードが有効化されました")

            display_prompt_file_status()

            if hasattr(st.session_state, "last_search_results"):
                display_search_results_debug(st.session_state.last_search_results)

            if (
                hasattr(st.session_state, "last_generated_json")
                and st.session_state.last_generated_json
            ):
                display_json_debug(
                    st.session_state.last_generated_json,
                    "生成されたPydanticオブジェクト",
                )

            if hasattr(st.session_state, "last_llm_output"):
                display_raw_llm_output(st.session_state.last_llm_output, "LLMの生出力")
