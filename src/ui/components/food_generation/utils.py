"""Utility functions for food generation components"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

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


def save_json_to_outputs(data: Dict, food_name: str) -> Optional[str]:
    """JSONデータをoutputsフォルダに保存する"""
    try:
        # outputsフォルダのパスを作成
        outputs_dir = Path("outputs/json")

        # ファイル名を生成（食べ物名_日付時刻.json）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 食べ物名をファイル名に使用できるよう処理
        safe_food_name = "".join(
            c for c in food_name if c.isalnum() or c in "-_"
        ).rstrip()
        filename = f"{safe_food_name}_{timestamp}.json"
        file_path = outputs_dir / filename

        # JSONファイルとして保存
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"JSONファイルを保存: {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"JSONファイル保存エラー: {e}")
        return None


def add_conversation_to_session(conversation_data: Dict):
    """会話データをセッションに追加"""
    if "conversation_lines" not in st.session_state:
        st.session_state.conversation_lines = []

    # Food形式の脚本データから全セグメントを取得
    segments = conversation_data.get("all_segments", [])

    for segment in segments:
        st.session_state.conversation_lines.append(
            {
                "speaker": segment["speaker"],
                "text": segment["text"],
                "expression": segment["expression"],
                "background": segment.get("background", ""),
                "visible_characters": segment["visible_characters"],
                "character_items": segment.get("character_items", {}),
            }
        )

    logger.info(f"会話リストに{len(segments)}個のセリフを追加")
    st.success(f"🎉 {len(segments)}個のセリフを会話リストに追加しました！")
    st.info("ホームページの会話入力セクションで確認できます。")
