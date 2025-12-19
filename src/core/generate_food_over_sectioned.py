"""セクション分割方式での台本生成モジュール"""

import streamlit as st
from typing import Dict, List, Any, Union
from pathlib import Path

from src.models.food_over import FoodOverconsumptionScript, VideoSection, StoryOutline
from src.core.outline_generator import generate_outline
from src.core.section_generators.base import SectionGeneratorBase, SectionContext
from src.core.generate_food_over import (
    search_food_information,
    format_search_results_for_prompt,
    create_llm_instance
)
from config.models import get_model_config, get_default_model_config
from config.closing_section import create_closing_section
from src.utils.logger import get_logger

logger = get_logger(__name__)

# セクション設定
SECTION_CONFIGS = [
    {"key": "hook", "name": "冒頭フック・危機の予告", "min": 6, "max": 10, "fixed_background": None},
    {"key": "background", "name": "食品解説・背景情報", "min": 10, "max": 15, "fixed_background": "modern_study_room"},
    {"key": "daily", "name": "日常導入・理由付け", "min": 12, "max": 18, "fixed_background": None},
    {"key": "honeymoon", "name": "楽観期・ハネムーン期", "min": 15, "max": 25, "fixed_background": None},
    {"key": "deterioration", "name": "異変期・段階的悪化", "min": 25, "max": 35, "fixed_background": None},
    {"key": "crisis", "name": "危機・転機となる決定的イベント", "min": 20, "max": 30, "fixed_background": None},
    {"key": "learning", "name": "真相解明・学習フェーズ", "min": 15, "max": 25, "fixed_background": "library"},
    {"key": "recovery", "name": "回復・新しい習慣", "min": 10, "max": 20, "fixed_background": None},
]


def generate_outline_only(
    food_name: str,
    model: str = None,
    temperature: float = None
) -> Union[StoryOutline, Dict[str, Any]]:
    """アウトラインのみを生成する

    Args:
        food_name: 食べ物名
        model: 使用するモデルID
        temperature: 生成温度

    Returns:
        StoryOutline: 生成されたアウトライン、またはエラー辞書
    """
    try:
        # モデル設定
        if model is None:
            model_config = get_default_model_config()
            model = model_config["id"]
        else:
            model_config = get_model_config(model)

        if temperature is None:
            temperature = model_config["default_temperature"]

        provider = model_config.get("provider", "openai")

        logger.info(
            f"アウトライン生成開始: 食べ物={food_name}, "
            f"プロバイダー={provider}, モデル={model}, temperature={temperature}"
        )

        st.info("🔍 食べ物情報を検索中...")
        search_results = search_food_information(food_name)
        reference_info = format_search_results_for_prompt(search_results)
        st.session_state.last_search_results = search_results

        st.info("📋 全体のアウトラインを作成中...")
        llm = create_llm_instance(model, temperature, model_config)
        outline = generate_outline(food_name, reference_info, llm)

        # アウトラインと関連情報をsession_stateに保存
        st.session_state.current_outline = outline
        st.session_state.current_food_name = food_name
        st.session_state.current_reference_info = reference_info
        st.session_state.current_model = model
        st.session_state.current_temperature = temperature
        st.session_state.current_model_config = model_config

        st.success(f"✅ アウトライン生成完了: {outline.title}")
        logger.info(f"アウトライン生成完了: {outline.title}")

        return outline

    except Exception as e:
        error_msg = f"アウトライン生成エラー: {e}"
        logger.error(error_msg, exc_info=True)
        st.error(f"❌ アウトライン生成に失敗しました: {str(e)}")
        return {"error": "Outline Generation Error", "details": str(e)}


def generate_sections_from_approved_outline() -> Union[FoodOverconsumptionScript, Dict[str, Any]]:
    """承認されたアウトラインから各セクションを生成する

    Returns:
        FoodOverconsumptionScript: 生成された台本、またはエラー辞書
    """
    try:
        # session_stateからアウトラインと設定を取得
        outline = st.session_state.current_outline
        food_name = st.session_state.current_food_name
        reference_info = st.session_state.current_reference_info
        model = st.session_state.current_model
        temperature = st.session_state.current_temperature
        model_config = st.session_state.current_model_config

        logger.info(f"承認されたアウトラインから脚本生成開始: {outline.title}")

        llm = create_llm_instance(model, temperature, model_config)

        sections = []
        previous_sections_summary = []

        st.info("🎬 各セクションの詳細を生成中...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, config in enumerate(SECTION_CONFIGS):
            status_text.text(
                f"📝 セクション {i+1}/8: {config['name']} を生成中... "
                f"({config['min']}-{config['max']}セリフ)"
            )

            generator = SectionGeneratorBase(
                section_key=config["key"],
                section_name=config["name"],
                min_lines=config["min"],
                max_lines=config["max"],
                fixed_background=config.get("fixed_background")
            )

            context = SectionContext(
                outline=outline,
                food_name=food_name,
                reference_information=reference_info,
                previous_sections=previous_sections_summary
            )

            try:
                section = generator.generate(context, llm)
                sections.append(section)

                section_summary = {
                    "section_name": section.section_name,
                    "segment_count": len(section.segments),
                    "last_speaker": section.segments[-1].speaker if section.segments else "",
                    "last_text": section.segments[-1].text if section.segments else "",
                    "summary": generator.summarize_section(section)
                }
                previous_sections_summary.append(section_summary)

                progress_bar.progress((i + 1) / len(SECTION_CONFIGS))

                with st.expander(
                    f"✅ {config['name']} ({len(section.segments)}セリフ)",
                    expanded=False
                ):
                    for seg in section.segments[:3]:
                        st.write(f"**{seg.speaker}**: {seg.text}")
                    if len(section.segments) > 3:
                        st.write(f"... 他 {len(section.segments) - 3} セリフ")

                logger.info(
                    f"セクション {i+1}/8 完了: {config['name']} - "
                    f"{len(section.segments)}セリフ"
                )

            except Exception as e:
                logger.error(f"セクション生成エラー ({config['name']}): {str(e)}", exc_info=True)
                st.error(f"❌ セクション生成失敗: {config['name']}")
                return {
                    "error": "Section Generation Error",
                    "section": config['name'],
                    "details": str(e)
                }

        st.info("🔍 品質チェック中...")

        all_segments = []
        for section in sections:
            all_segments.extend(section.segments)

        total_segments = len(all_segments)
        logger.info(f"全セグメント数（締めくくり前）: {total_segments}")

        if total_segments < 130:
            st.warning(f"⚠️ セリフ数が少なめです（{total_segments}/130）")
            logger.warning(f"セリフ数が目標より少ない: {total_segments}/130")
        elif total_segments > 160:
            st.warning(f"⚠️ セリフ数が多めです（{total_segments}/160）")
            logger.warning(f"セリフ数が目標より多い: {total_segments}/160")
        else:
            st.success(f"✅ セリフ数OK: {total_segments}セリフ")
            logger.info(f"セリフ数が適正範囲: {total_segments}")

        with st.expander("📊 セクション別セリフ数", expanded=False):
            for i, section in enumerate(sections):
                config = SECTION_CONFIGS[i]
                segment_count = len(section.segments)
                status = "✅" if config["min"] <= segment_count <= config["max"] else "⚠️"
                st.write(
                    f"{status} {section.section_name}: {segment_count}セリフ "
                    f"(目標: {config['min']}-{config['max']})"
                )

        # 締めくくりセクションを追加
        st.info("🎬 締めくくりセクションを追加中...")
        closing_section = create_closing_section()
        sections.append(closing_section)
        all_segments.extend(closing_section.segments)

        total_segments_with_closing = len(all_segments)
        logger.info(
            f"締めくくりセクション追加完了: +{len(closing_section.segments)}セリフ "
            f"(合計: {total_segments_with_closing})"
        )
        st.success(f"✅ 締めくくり追加: +{len(closing_section.segments)}セリフ")

        estimated_duration_sec = total_segments_with_closing * 4
        estimated_duration = f"{estimated_duration_sec // 60}分{estimated_duration_sec % 60}秒"

        script = FoodOverconsumptionScript(
            title=outline.title,
            food_name=food_name,
            estimated_duration=estimated_duration,
            sections=sections,
            all_segments=all_segments
        )

        st.session_state.last_generated_json = script
        st.session_state.last_llm_output = f"セクション分割方式で生成成功: {total_segments_with_closing}セリフ"

        st.success("🎉 台本生成完了！")
        logger.info(f"台本生成成功: {total_segments_with_closing}セリフ, 推定時間: {estimated_duration}")

        return script

    except Exception as e:
        error_msg = f"予期せぬエラーが発生しました: {e}"
        logger.error(error_msg, exc_info=True)

        st.session_state.last_llm_output = f"予期せぬエラー: {str(e)}"
        st.session_state.last_generated_json = None

        return {"error": "Unexpected Error", "details": str(e)}


def generate_food_overconsumption_script_sectioned(
    food_name: str,
    model: str = None,
    temperature: float = None
) -> Union[FoodOverconsumptionScript, Dict[str, Any]]:
    """セクション分割方式で食べ物摂取過多動画脚本を生成する（ワンステップ版・後方互換性のため残存）

    Args:
        food_name: 食べ物名
        model: 使用するモデルID
        temperature: 生成温度

    Returns:
        FoodOverconsumptionScript: 生成された台本、またはエラー辞書
    """
    # アウトライン生成
    outline_result = generate_outline_only(food_name, model, temperature)

    if isinstance(outline_result, dict) and "error" in outline_result:
        return outline_result

    # そのまま承認してセクション生成
    return generate_sections_from_approved_outline()
