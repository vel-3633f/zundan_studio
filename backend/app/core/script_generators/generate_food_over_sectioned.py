from typing import Dict, List, Any, Union, Optional, Callable
from pathlib import Path
from app.models.food_over import FoodOverconsumptionScript, VideoSection, StoryOutline
from app.core.script_generators.outline_generator import generate_outline
from app.core.section_generators.base import SectionGeneratorBase, SectionContext
from app.core.script_generators.generate_food_over import (
    search_food_information,
    format_search_results_for_prompt,
    create_llm_instance
)
from app.config.models import get_model_config, get_default_model_config
from app.config.content_config.closing_section import create_closing_section
from app.utils.logger import get_logger
logger = get_logger(__name__)
SECTION_CONFIGS = [
    {"key": "hook", "name": "冒頭フック・危機の予告", "min": 6, "max": 10, "background": "home_livingroom_morning"},
    {"key": "background", "name": "食品解説・背景情報", "min": 10, "max": 15, "background": "modern_study_room"},
    {"key": "daily", "name": "日常導入・理由付け", "min": 12, "max": 18, "background": "cafe_counter_morning"},
    {"key": "honeymoon", "name": "楽観期・ハネムーン期", "min": 15, "max": 25, "background": "restaurant_ikinaristeak_day"},
    {"key": "deterioration", "name": "異変期・段階的悪化", "min": 25, "max": 35, "background": "home_livingroom_morning"},
    {"key": "crisis", "name": "危機・転機となる決定的イベント", "min": 20, "max": 30, "background": "office_meeting_emergency"},
    {"key": "learning", "name": "真相解明・学習フェーズ", "min": 15, "max": 25, "background": "library"},
    {"key": "recovery", "name": "回復・新しい習慣", "min": 10, "max": 20, "background": "home_livingroom_morning"},
]
def generate_outline_only(
    food_name: str,
    model: str = None,
    temperature: float = None,
    progress_callback: Optional[Callable[[str], None]] = None
) -> Union[StoryOutline, Dict[str, Any]]:
    """アウトラインのみを生成する

    Args:
        food_name: 食べ物名
        model: 使用するモデルID
        temperature: 生成温度
        progress_callback: 進捗通知用コールバック関数

    Returns:
        StoryOutline: 生成されたアウトライン、またはエラー辞書
    """
    try:
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
        if progress_callback:
            progress_callback("🔍 食べ物情報を検索中...")
        search_results = search_food_information(food_name)
        reference_info = format_search_results_for_prompt(search_results)
        if progress_callback:
            progress_callback("📋 全体のアウトラインを作成中...")
        llm = create_llm_instance(model, temperature, model_config)
        outline = generate_outline(food_name, reference_info, llm)
        logger.info(f"アウトライン生成完了: {outline.title}")
        return {
            "outline": outline,
            "search_results": search_results,
            "reference_info": reference_info,
            "model": model,
            "temperature": temperature,
            "model_config": model_config
        }
    except Exception as e:
        error_msg = f"アウトライン生成エラー: {e}"
        logger.error(error_msg, exc_info=True)
        return {"error": "Outline Generation Error", "details": str(e)}
def generate_sections_from_approved_outline(
    outline: StoryOutline,
    food_name: str,
    reference_info: str,
    model: str,
    temperature: float,
    model_config: Dict[str, Any],
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Union[FoodOverconsumptionScript, Dict[str, Any]]:
    """承認されたアウトラインから各セクションを生成する

    Args:
        outline: 承認されたアウトライン
        food_name: 食べ物名
        reference_info: 参照情報
        model: 使用するモデルID
        temperature: 生成温度
        model_config: モデル設定
        progress_callback: 進捗通知用コールバック関数(message, progress)

    Returns:
        FoodOverconsumptionScript: 生成された台本、またはエラー辞書
    """
    try:
        logger.info(f"承認されたアウトラインから脚本生成開始: {outline.title}")
        llm = create_llm_instance(model, temperature, model_config)
        sections = []
        previous_sections_summary = []
        if progress_callback:
            progress_callback("🎬 各セクションの詳細を生成中...", 0.0)
        for i, config in enumerate(SECTION_CONFIGS):
            if progress_callback:
                progress_callback(
                    f"📝 セクション {i+1}/8: {config['name']} を生成中... "
                    f"({config['min']}-{config['max']}セリフ)",
                    (i / len(SECTION_CONFIGS))
                )
            generator = SectionGeneratorBase(
                section_key=config["key"],
                section_name=config["name"],
                min_lines=config["min"],
                max_lines=config["max"],
                fixed_background=config.get("background")
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
                if progress_callback:
                    progress_callback(
                        f"✅ {config['name']} 完了 ({len(section.segments)}セリフ)",
                        ((i + 1) / len(SECTION_CONFIGS))
                    )
                logger.info(
                    f"セクション {i+1}/8 完了: {config['name']} - "
                    f"{len(section.segments)}セリフ"
                )
            except Exception as e:
                logger.error(f"セクション生成エラー ({config['name']}): {str(e)}", exc_info=True)
                return {
                    "error": "Section Generation Error",
                    "section": config['name'],
                    "details": str(e)
                }
        if progress_callback:
            progress_callback("🔍 品質チェック中...", 0.9)
        all_segments = []
        for section in sections:
            all_segments.extend(section.segments)
        total_segments = len(all_segments)
        logger.info(f"全セグメント数（締めくくり前）: {total_segments}")
        if total_segments < 130:
            logger.warning(f"セリフ数が目標より少ない: {total_segments}/130")
        elif total_segments > 160:
            logger.warning(f"セリフ数が目標より多い: {total_segments}/160")
        else:
            logger.info(f"セリフ数が適正範囲: {total_segments}")
        if progress_callback:
            progress_callback("🎬 締めくくりセクションを追加中...", 0.95)
        closing_section = create_closing_section()
        sections.append(closing_section)
        all_segments.extend(closing_section.segments)
        total_segments_with_closing = len(all_segments)
        logger.info(
            f"締めくくりセクション追加完了: +{len(closing_section.segments)}セリフ "
            f"(合計: {total_segments_with_closing})"
        )
        estimated_duration_sec = total_segments_with_closing * 4
        estimated_duration = f"{estimated_duration_sec // 60}分{estimated_duration_sec % 60}秒"
        script = FoodOverconsumptionScript(
            title=outline.title,
            food_name=food_name,
            estimated_duration=estimated_duration,
            sections=sections,
            all_segments=all_segments
        )
        if progress_callback:
            progress_callback("🎉 台本生成完了！", 1.0)
        logger.info(f"台本生成成功: {total_segments_with_closing}セリフ, 推定時間: {estimated_duration}")
        return script
    except Exception as e:
        error_msg = f"予期せぬエラーが発生しました: {e}"
        logger.error(error_msg, exc_info=True)
        return {"error": "Unexpected Error", "details": str(e)}
def generate_food_overconsumption_script_sectioned(
    food_name: str,
    model: str = None,
    temperature: float = None,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Union[FoodOverconsumptionScript, Dict[str, Any]]:
    """セクション分割方式で食べ物摂取過多動画脚本を生成する（ワンステップ版・後方互換性のため残存）

    Args:
        food_name: 食べ物名
        model: 使用するモデルID
        temperature: 生成温度
        progress_callback: 進捗通知用コールバック関数

    Returns:
        FoodOverconsumptionScript: 生成された台本、またはエラー辞書
    """
    outline_result = generate_outline_only(food_name, model, temperature, progress_callback)
    if isinstance(outline_result, dict) and "error" in outline_result:
        return outline_result
    outline = outline_result["outline"]
    reference_info = outline_result["reference_info"]
    model = outline_result["model"]
    temperature = outline_result["temperature"]
    model_config = outline_result["model_config"]
    return generate_sections_from_approved_outline(
        outline, food_name, reference_info, model, temperature, model_config, progress_callback
    )