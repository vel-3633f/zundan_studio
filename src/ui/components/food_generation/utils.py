"""Utility functions for food generation components"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pykakasi

from src.utils.logger import get_logger

logger = get_logger(__name__)


def estimate_video_duration(segments: List[Dict]) -> str:
    """動画の推定時間を計算"""
    if not segments:
        return "約0分00秒"

    total_chars = sum(len(segment.get("text", "")) for segment in segments)
    total_seconds = total_chars * 0.4
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    duration = f"約{minutes}分{seconds:02d}秒"
    logger.debug(f"動画時間推定: {total_chars}文字 → {duration}")
    return duration


def _convert_japanese_to_romaji(food_name: str) -> str:
    """日本語の食べ物名をローマ字に変換する"""
    try:
        kks = pykakasi.kakasi()

        result = kks.convert(food_name)

        romaji_text = "".join([item["hepburn"] for item in result])

        clean_text = "".join(c for c in romaji_text if c.isalnum()).lower()

        return clean_text if clean_text else "unknown_food"

    except Exception as e:
        logger.warning(f"日本語→ローマ字変換エラー: {e}")
        result = "".join(c for c in food_name if c.isascii() and c.isalnum()).lower()
        return result if result else "unknown_food"


def save_json_to_outputs(data: Dict, food_name: str) -> Optional[str]:
    """JSONデータをoutputsフォルダに保存する"""
    try:
        outputs_dir = Path("outputs/json")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        romaji_food_name = _convert_japanese_to_romaji(food_name)
        filename = f"{romaji_food_name}_{timestamp}.json"
        file_path = outputs_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"JSONファイルを保存: {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"JSONファイル保存エラー: {e}")
        return None
