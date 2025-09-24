import pandas as pd
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


def load_scenario_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """JSONデータを読み込み、処理用の形式に変換"""
    return json_data


def display_header(data: Dict[str, Any]):
    """ヘッダー部分の表示"""
    st.title(f"🎬 {data['title']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("食品名", data["food_name"])
    with col2:
        st.metric("推定時間", data["estimated_duration"])
    with col3:
        st.metric("総セクション数", len(data["sections"]))


def get_character_emoji(character: str) -> str:
    """キャラクターに対応する絵文字を返す"""
    emoji_map = {"zundamon": "🟢", "metan": "🔵", "tsumugi": "🟡", "narrator": "📢"}
    return emoji_map.get(character, "👤")


def get_expression_emoji(expression: str) -> str:
    """表情に対応する絵文字を返す"""
    expression_map = {
        "happy": "😊",
        "excited": "🤩",
        "worried": "😰",
        "thinking": "🤔",
        "sad": "😢",
        "surprised": "😲",
        "serious": "😐",
        "normal": "😐",
    }
    return expression_map.get(expression, "😐")


def display_segment(segment: Dict[str, Any], segment_index: int):
    """個別セグメントの表示"""
    character_emoji = get_character_emoji(segment["speaker"])
    expression_emoji = get_expression_emoji(segment["expression"])

    with st.container():
        col1, col2 = st.columns([1, 10])

        with col1:
            st.write(f"{character_emoji}")

        with col2:
            # キャラクター名と表情
            st.markdown(f"**{segment['speaker']}** {expression_emoji}")

            # セリフ
            st.markdown(f"💬 {segment['text']}")

            # アイテム情報があれば表示
            if segment.get("character_items") and segment["character_items"]:
                items = list(segment["character_items"].values())
                st.caption(f"📦 アイテム: {', '.join(items)}")

            # 登場キャラクター
            if segment.get("visible_characters"):
                characters = ", ".join(segment["visible_characters"])
                st.caption(f"👥 登場: {characters}")

        st.divider()


def display_section_overview(sections: List[Dict[str, Any]]):
    """セクション概要の表示"""
    st.subheader("📋 セクション概要")

    section_data = []
    for i, section in enumerate(sections):
        section_data.append(
            {
                "セクション": f"{i+1}. {section['section_name']}",
                "セグメント数": len(section["segments"]),
                "背景": section["scene_background"],
            }
        )

    df = pd.DataFrame(section_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_character_stats(all_segments: List[Dict[str, Any]]):
    """キャラクター統計の表示"""
    st.subheader("👤 キャラクター統計")

    character_counts = {}
    expression_counts = {}

    for segment in all_segments:
        speaker = segment["speaker"]
        expression = segment["expression"]

        character_counts[speaker] = character_counts.get(speaker, 0) + 1
        expression_counts[expression] = expression_counts.get(expression, 0) + 1

    col1, col2 = st.columns(2)

    with col1:
        st.write("**セリフ数**")
        for char, count in sorted(
            character_counts.items(), key=lambda x: x[1], reverse=True
        ):
            emoji = get_character_emoji(char)
            st.write(f"{emoji} {char}: {count}")

    with col2:
        st.write("**表情分布**")
        for expr, count in sorted(
            expression_counts.items(), key=lambda x: x[1], reverse=True
        ):
            emoji = get_expression_emoji(expr)
            st.write(f"{emoji} {expr}: {count}")


def search_segments(
    all_segments: List[Dict[str, Any]], query: str
) -> List[Dict[str, Any]]:
    """セグメント検索機能"""
    if not query:
        return all_segments

    query = query.lower()
    filtered_segments = []

    for segment in all_segments:
        if (
            query in segment["text"].lower()
            or query in segment["speaker"].lower()
            or query in segment["expression"].lower()
        ):
            filtered_segments.append(segment)

    return filtered_segments


def display_food_script_preview(script_data: FoodOverconsumptionScript):

    data = script_data

    display_header(data)

    # サイドバー
    with st.sidebar:
        st.header("🎛️ コントロール")

        # セクション選択
        section_names = [
            f"{i+1}. {s['section_name']}" for i, s in enumerate(data["sections"])
        ]
        selected_section = st.selectbox("セクション選択", ["全て"] + section_names)

        # キャラクターフィルター
        all_characters = list(
            set(seg["speaker"] for seg in data.get("all_segments", []))
        )
        selected_characters = st.multiselect(
            "キャラクター", all_characters, default=all_characters
        )

        # 検索機能
        search_query = st.text_input("🔍 テキスト検索")

        # JSONアップロード機能
        st.subheader("📁 データアップロード")
        uploaded_file = st.file_uploader("JSONファイルをアップロード", type=["json"])

        if uploaded_file is not None:
            try:
                new_data = json.load(uploaded_file)
                st.session_state.scenario_data = new_data
                st.success("データが更新されました！")
                st.rerun()
            except Exception as e:
                st.error(f"ファイル読み込みエラー: {e}")

    # メインコンテンツ
    tab1, tab2, tab3 = st.tabs(["📖 シナリオ表示", "📊 統計情報", "📋 概要"])

    with tab1:
        # セグメント表示
        segments_to_show = data.get("all_segments", [])

        # フィルタリング
        if selected_section != "全て":
            section_index = int(selected_section.split(".")[0]) - 1
            segments_to_show = data["sections"][section_index]["segments"]

        if selected_characters:
            segments_to_show = [
                s for s in segments_to_show if s["speaker"] in selected_characters
            ]

        if search_query:
            segments_to_show = search_segments(segments_to_show, search_query)

        # 結果表示
        st.subheader(f"📝 セグメント表示 ({len(segments_to_show)}件)")

        if segments_to_show:
            # プログレスバー
            progress = st.progress(0)

            for i, segment in enumerate(segments_to_show):
                display_segment(segment, i)
                progress.progress((i + 1) / len(segments_to_show))
        else:
            st.info("条件に一致するセグメントがありません。")

    with tab2:
        if data.get("all_segments"):
            display_character_stats(data["all_segments"])
        else:
            st.info("統計情報を表示するには all_segments データが必要です。")

    with tab3:
        display_section_overview(data["sections"])

        # エクスポート機能
        st.subheader("📤 エクスポート")
        if st.button("テキストファイルとしてエクスポート"):
            text_content = f"# {data['title']}\n\n"
            for section in data["sections"]:
                text_content += f"## {section['section_name']}\n\n"
                for segment in section["segments"]:
                    text_content += f"**{segment['speaker']}**: {segment['text']}\n\n"

            st.download_button(
                label="ダウンロード",
                data=text_content,
                file_name=f"{data['food_name']}_scenario.txt",
                mime="text/plain",
            )
