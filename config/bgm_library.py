"""BGM管理モジュール

セクションごとに使用できるBGMを管理します。
"""

from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path


@dataclass
class BGMTrack:
    """BGMトラックの情報"""

    id: str
    name: str
    file_path: str
    default_volume: float
    mood: str
    description: str


# BGMライブラリ
BGM_LIBRARY: Dict[str, BGMTrack] = {
    "none": BGMTrack(
        id="none",
        name="BGMなし",
        file_path="",
        default_volume=0.0,
        mood="none",
        description="BGMを使用しない",
    ),
    "upbeat_1": BGMTrack(
        id="upbeat_1",
        name="明るく軽快",
        file_path="assets/bgm/upbeat_1.mp3",
        default_volume=0.25,
        mood="cheerful",
        description="明るく楽しいシーン、ポジティブな雰囲気に適したBGM",
    ),
    "calm_1": BGMTrack(
        id="calm_1",
        name="落ち着いた説明",
        file_path="assets/bgm/calm_1.mp3",
        default_volume=0.20,
        mood="calm",
        description="落ち着いた説明シーン、情報提供に適したBGM",
    ),
    "curious_1": BGMTrack(
        id="curious_1",
        name="興味深い・探求",
        file_path="assets/bgm/curious_1.mp3",
        default_volume=0.22,
        mood="curious",
        description="好奇心を刺激する、探求的な雰囲気のBGM",
    ),
    "relaxed_1": BGMTrack(
        id="relaxed_1",
        name="リラックス・穏やか",
        file_path="assets/bgm/relaxed_1.mp3",
        default_volume=0.18,
        mood="relaxed",
        description="穏やかで癒される、リラックスした雰囲気のBGM",
    ),
    "tense_1": BGMTrack(
        id="tense_1",
        name="緊迫・不安",
        file_path="assets/bgm/tense_1.mp3",
        default_volume=0.28,
        mood="tense",
        description="緊迫感のあるシーン、不安を感じさせる場面に適したBGM",
    ),
    "dramatic_1": BGMTrack(
        id="dramatic_1",
        name="ドラマチック",
        file_path="assets/bgm/dramatic_1.mp3",
        default_volume=0.30,
        mood="dramatic",
        description="ドラマチックなシーン、重要な転機に適したBGM",
    ),
    "sad_1": BGMTrack(
        id="sad_1",
        name="悲しい・切ない",
        file_path="assets/bgm/sad_1.mp3",
        default_volume=0.22,
        mood="sad",
        description="悲しい、切ないシーンに適したBGM",
    ),
    "hopeful_1": BGMTrack(
        id="hopeful_1",
        name="希望・前向き",
        file_path="assets/bgm/hopeful_1.mp3",
        default_volume=0.25,
        mood="hopeful",
        description="希望に満ちた、前向きなシーンに適したBGM",
    ),
}


def get_bgm_track(bgm_id: str) -> Optional[BGMTrack]:
    """BGMトラック情報を取得

    Args:
        bgm_id: BGMのID

    Returns:
        BGMTrack: BGMトラック情報、存在しない場合はNone
    """
    return BGM_LIBRARY.get(bgm_id)


def get_bgm_file_path(bgm_id: str) -> Optional[str]:
    """BGMファイルの絶対パスを取得

    Args:
        bgm_id: BGMのID

    Returns:
        str: BGMファイルの絶対パス、存在しない場合やnoneの場合はNone
    """
    if bgm_id == "none":
        return None

    track = get_bgm_track(bgm_id)
    if not track or not track.file_path:
        return None

    # プロジェクトルートからの絶対パスを構築
    project_root = Path(__file__).parent.parent.parent
    return str(project_root / track.file_path)


def get_all_bgm_ids() -> list[str]:
    """利用可能な全BGM IDのリストを取得

    Returns:
        list[str]: BGM IDのリスト
    """
    return list(BGM_LIBRARY.keys())


# セクションごとの固定BGM設定
SECTION_BGM_MAP: Dict[str, Dict[str, any]] = {
    "hook": {"bgm_id": "dramatic_1", "volume": 0.30},  # 冒頭フック - ドラマチック
    "daily": {"bgm_id": "calm_1", "volume": 0.20},  # 日常導入 - 落ち着いた
    "background": {"bgm_id": "curious_1", "volume": 0.22},  # 背景説明 - 興味深い
    "crisis": {"bgm_id": "tense_1", "volume": 0.28},  # 危機の発生 - 緊迫感
    "deterioration": {"bgm_id": "sad_1", "volume": 0.22},  # 悪化 - 悲しい
    "honeymoon": {"bgm_id": "hopeful_1", "volume": 0.25},  # ハネムーン期 - 希望
    "recovery": {"bgm_id": "upbeat_1", "volume": 0.25},  # 回復 - 明るく軽快
    "learning": {"bgm_id": "relaxed_1", "volume": 0.18},  # 教訓 - リラックス
}


def get_section_bgm(section_type: str) -> Dict[str, any]:
    """セクションタイプに応じた固定BGM設定を取得

    Args:
        section_type: セクションのタイプ (hook, daily, background, etc.)

    Returns:
        Dict[str, any]: BGM設定 (bgm_id と volume)、存在しない場合はデフォルト
    """
    return SECTION_BGM_MAP.get(section_type, {"bgm_id": "none", "volume": 0.0})


def format_bgm_choices_for_prompt() -> str:
    """プロンプト用にBGM選択肢を整形

    Returns:
        str: プロンプトに埋め込むBGM選択肢の説明文
    """
    lines = ["利用可能なBGM:"]

    for bgm_id, track in BGM_LIBRARY.items():
        lines.append(f"- {bgm_id}: {track.name} - {track.description}")

    return "\n".join(lines)
