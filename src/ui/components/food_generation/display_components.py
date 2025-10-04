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


def display_scene_and_items_info(data: FoodOverconsumptionScript):
    """シーン情報を表示"""
    st.markdown("### 🎨 シーン情報")

    if not data.sections:
        st.info("シーン情報が見つかりませんでした")
        return

    section_scenes = {}

    for section in data.sections:
        section_scenes[section.section_name] = section.scene_background

    st.subheader("🎬 セクション別シーン")
    for section_name, scene in section_scenes.items():
        st.write(f"**{section_name}**: {scene}")


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


def display_header(data: FoodOverconsumptionScript):
    """ヘッダー部分の表示"""
    st.title(f"🎬 {data.title}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("食品名", data.food_name)
    with col2:
        st.metric("推定時間", data.estimated_duration)
    with col3:
        st.metric("総セクション数", len(data.sections))


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
    character_emoji = get_character_emoji(segment.speaker)
    expression_emoji = get_expression_emoji(segment.expression)

    with st.container():
        col1, col2 = st.columns([1, 10])

        with col1:
            st.write(f"{character_emoji}")

        with col2:
            st.markdown(f"**{segment.speaker}** {expression_emoji}")
            st.markdown(f"💬 {segment.text}")

            if segment.visible_characters:
                st.caption(f"👥 登場: {', '.join(segment.visible_characters)}")


def display_section_overview(sections):
    """セクション概要の表示"""
    st.subheader("📋 セクション概要")

    section_data = [
        {
            "セクション": f"{i+1}. {section.section_name}",
            "セグメント数": len(section.segments),
            "背景": section.scene_background,
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
        speaker = segment.speaker
        expression = segment.expression
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
            query in str(getattr(segment, field, "")).lower()
            for field in ["text", "speaker", "expression"]
        )
    ]
