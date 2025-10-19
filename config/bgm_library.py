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
    "nandesho": BGMTrack(
        id="nandesho",
        name="なんでしょう？",
        file_path="assets/bgm/なんでしょう？.mp3",
        default_volume=0.22,
        mood="curious",
        description="好奇心を刺激する、探求的な雰囲気のBGM",
    ),
    "honwaka": BGMTrack(
        id="honwaka",
        name="ほんわかぷっぷー",
        file_path="assets/bgm/ほんわかぷっぷー.mp3",
        default_volume=0.25,
        mood="cheerful",
        description="明るく楽しいシーン、ポジティブな雰囲気に適したBGM",
    ),
    "hirusagari": BGMTrack(
        id="hirusagari",
        name="昼下がり気分",
        file_path="assets/bgm/昼下がり気分.mp3",
        default_volume=0.20,
        mood="calm",
        description="落ち着いた説明シーン、穏やかな雰囲気に適したBGM",
    ),
    "noraneko": BGMTrack(
        id="noraneko",
        name="野良猫は宇宙を目指した",
        file_path="assets/bgm/野良猫は宇宙を目指した_2.mp3",
        default_volume=0.28,
        mood="dramatic",
        description="ドラマチックなシーン、重要な転機に適したBGM",
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
    "learning": {"bgm_id": "noraneko", "volume": 0.18},  # 教訓 - リラックス
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
