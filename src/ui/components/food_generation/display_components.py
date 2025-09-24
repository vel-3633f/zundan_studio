import pandas as pd
import streamlit as st
import json
from src.models.food_over import FoodOverconsumptionScript
from config.app import SYSTEM_PROMPT_FILE, USER_PROMPT_FILE
from src.utils.logger import get_logger
from .data_models import Characters

logger = get_logger(__name__)


def display_json_debug(data, title="JSON Debug"):
    """JSONデータをデバッグ用に表示"""
    with st.expander(f"🔍 {title}", expanded=False):
        json_data = data.model_dump() if hasattr(data, "model_dump") else data
        st.json(json_data)


def display_search_results_debug(search_results):
    """検索結果をデバッグ用に表示"""
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


def display_scene_and_items_info(data):
    """シーンとアイテム情報を表示"""
    st.markdown("### 🎨 シーン・アイテム情報")

    sections = data.get("sections", [])
    if not sections:
        st.info("シーン・アイテム情報が見つかりませんでした")
        return

    section_scenes = {}
    character_items_all = {}

    for section in sections:
        section_name = section.get("section_name", "Unknown")
        section_scenes[section_name] = section.get("scene_background", "")

        for segment in section.get("segments", []):
            if segment.get("character_items"):
                for char, item in segment["character_items"].items():
                    if char not in character_items_all:
                        character_items_all[char] = set()
                    character_items_all[char].add(item)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎬 セクション別シーン")
        for section_name, scene in section_scenes.items():
            st.write(f"**{section_name}**: {scene}")

    with col2:
        st.subheader("🎯 キャラクター別アイテム")
        for char, items in character_items_all.items():
            char_display = Characters.get_display_name(char)
            st.write(f"**{char_display}**:")
            for item in sorted(items):
                st.write(f"  • {item}")


def display_prompt_file_status():
    """プロンプトファイルの状態を表示"""
    with st.expander("📄 プロンプトファイル設定", expanded=False):
        files = [
            ("システムプロンプト", SYSTEM_PROMPT_FILE),
            ("ユーザープロンプト", USER_PROMPT_FILE),
        ]

        for name, file_path in files:
            if file_path.exists():
                st.success(f"✅ {name}: {file_path.stat().st_size} bytes")
            else:
                st.error(f"❌ {name}: ファイルが見つかりません")


def display_header(data):
    """ヘッダー部分の表示"""
    st.title(f"🎬 {data['title']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("食品名", data["food_name"])
    with col2:
        st.metric("推定時間", data["estimated_duration"])
    with col3:
        st.metric("総セクション数", len(data["sections"]))


def get_character_emoji(character):
    """キャラクターに対応する絵文字を返す"""
    emoji_map = {"zundamon": "🟢", "metan": "🔵", "tsumugi": "🟡", "narrator": "📢"}
    return emoji_map.get(character, "👤")


def get_expression_emoji(expression):
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


def display_segment(segment, segment_index):
    """個別セグメントの表示"""
    character_emoji = get_character_emoji(segment["speaker"])
    expression_emoji = get_expression_emoji(segment["expression"])

    with st.container():
        col1, col2 = st.columns([1, 10])

        with col1:
            st.write(f"{character_emoji}")

        with col2:
            st.markdown(f"**{segment['speaker']}** {expression_emoji}")
            st.markdown(f"💬 {segment['text']}")

            if segment.get("character_items"):
                items = list(segment["character_items"].values())
                st.caption(f"📦 アイテム: {', '.join(items)}")

            if segment.get("visible_characters"):
                st.caption(f"👥 登場: {', '.join(segment['visible_characters'])}")

        st.divider()


def display_section_overview(sections):
    """セクション概要の表示"""
    st.subheader("📋 セクション概要")

    section_data = [
        {
            "セクション": f"{i+1}. {section['section_name']}",
            "セグメント数": len(section["segments"]),
            "背景": section["scene_background"],
        }
        for i, section in enumerate(sections)
    ]

    df = pd.DataFrame(section_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_character_stats(all_segments):
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
            st.write(f"{get_character_emoji(char)} {char}: {count}")

    with col2:
        st.write("**表情分布**")
        for expr, count in sorted(
            expression_counts.items(), key=lambda x: x[1], reverse=True
        ):
            st.write(f"{get_expression_emoji(expr)} {expr}: {count}")


def search_segments(all_segments, query):
    """セグメント検索機能"""
    if not query:
        return all_segments

    query = query.lower()
    return [
        segment
        for segment in all_segments
        if any(
            query in str(segment.get(field, "")).lower()
            for field in ["text", "speaker", "expression"]
        )
    ]


def display_food_script_preview(script_data: FoodOverconsumptionScript):
    data = script_data
    display_header(data)

    with st.sidebar:
        st.header("🎛️ コントロール")

        section_names = [
            f"{i+1}. {s['section_name']}" for i, s in enumerate(data["sections"])
        ]
        selected_section = st.selectbox("セクション選択", ["全て"] + section_names)

        all_characters = list(
            set(seg["speaker"] for seg in data.get("all_segments", []))
        )
        selected_characters = st.multiselect(
            "キャラクター", all_characters, default=all_characters
        )

        search_query = st.text_input("🔍 テキスト検索")

        st.subheader("📁 データアップロード")
        uploaded_file = st.file_uploader("JSONファイルをアップロード", type=["json"])

        if uploaded_file:
            try:
                st.session_state.scenario_data = json.load(uploaded_file)
                st.success("データが更新されました！")
                st.rerun()
            except Exception as e:
                st.error(f"ファイル読み込みエラー: {e}")

    tab1, tab2, tab3 = st.tabs(["📖 シナリオ表示", "📊 統計情報", "📋 概要"])

    with tab1:
        segments_to_show = data.get("all_segments", [])

        if selected_section != "全て":
            section_index = int(selected_section.split(".")[0]) - 1
            segments_to_show = data["sections"][section_index]["segments"]

        if selected_characters:
            segments_to_show = [
                s for s in segments_to_show if s["speaker"] in selected_characters
            ]

        segments_to_show = search_segments(segments_to_show, search_query)

        st.subheader(f"📝 セグメント表示 ({len(segments_to_show)}件)")

        if segments_to_show:
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
