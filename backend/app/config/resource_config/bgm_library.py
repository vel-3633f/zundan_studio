from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path
import logging
import os
import unicodedata

from app.config.app import Paths

logger = logging.getLogger(__name__)


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
        default_volume=0.20,
        mood="curious",
        description="好奇心を刺激する、探求的な雰囲気のBGM",
    ),
    "honwaka": BGMTrack(
        id="honwaka",
        name="ほんわかぷっぷー",
        file_path="assets/bgm/ほんわかぷっぷー.mp3",
        default_volume=0.20,
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
        default_volume=0.20,
        mood="dramatic",
        description="ドラマチックなシーン、重要な転機に適したBGM",
    ),
    "mayonaka_omocha": BGMTrack(
        id="mayonaka_omocha",
        name="真夜中のおもちゃ箱",
        file_path="assets/bgm/真夜中のおもちゃ箱.mp3",
        default_volume=0.20,
        mood="mysterious",
        description="ミステリアスで少し不思議な雰囲気のBGM",
    ),
    "maou_piano25": BGMTrack(
        id="maou_piano25",
        name="日常ピアノ25",
        file_path="assets/bgm/maou_日常_piano25.mp3",
        default_volume=0.20,
        mood="peaceful",
        description="穏やかな日常シーン、落ち着いた雰囲気のピアノBGM",
    ),
    "2_23_am": BGMTrack(
        id="2_23_am",
        name="2:23 AM",
        file_path="assets/bgm/2_23_AM_2.mp3",
        default_volume=0.20,
        mood="ambient",
        description="深夜の静かな雰囲気、アンビエントな背景音楽",
    ),
    "summer_triangle": BGMTrack(
        id="summer_triangle",
        name="SUMMER TRIANGLE",
        file_path="assets/bgm/SUMMER_TRIANGLE.mp3",
        default_volume=0.20,
        mood="uplifting",
        description="爽やかで前向きな雰囲気、夏の明るいイメージのBGM",
    ),
    "oikakekko_kyahha": BGMTrack(
        id="oikakekko_kyahha",
        name="おいかけっこきゃっは",
        file_path="assets/bgm/追いかけっこキャッハー.mp3",
        default_volume=0.05,
        mood="playful",
        description="遊び心のある楽しい雰囲気のBGM",
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
        logger.warning(f"BGMトラックが見つかりません: {bgm_id}")
        return None

    assets_dir = Paths.get_assets_dir()
    # track.file_path は "assets/bgm/..." なので、"bgm/..." 部分を抽出
    bgm_relative_path = track.file_path.replace("assets/", "", 1)
    full_path = os.path.join(assets_dir, bgm_relative_path)

    full_path_nfd = unicodedata.normalize("NFD", full_path)

    exists_nfc = os.path.exists(full_path)
    exists_nfd = os.path.exists(full_path_nfd)

    if exists_nfd and not exists_nfc:
        logger.info(f"BGMファイルパス解決（NFD正規化）: {bgm_id} -> {full_path_nfd}")
        return full_path_nfd

    logger.info(f"BGMファイルパス解決: {bgm_id} -> {full_path} (exists: {exists_nfc})")
    return full_path


SECTION_BGM_MAP: Dict[str, str] = {
    "hook": "mayonaka_omocha",
    "daily": "honwaka",
    "background": "maou_piano25",
    "crisis": "mayonaka_omocha",
    "deterioration": "nandesho",
    "honeymoon": "hirusagari",
    "recovery": "noraneko",
    "learning": "2_23_am",
}


def get_section_bgm(section_type: str) -> Dict[str, any]:
    """セクションタイプに応じた固定BGM設定を取得

    Args:
        section_type: セクションのタイプ (hook, daily, background, etc.)

    Returns:
        Dict[str, any]: BGM設定 (bgm_id と volume)、存在しない場合はデフォルト
    """
    # 全てのセクションでoikakekko_kyahhaを使用（音量0.05）
    bgm_id = "oikakekko_kyahha"
    track = get_bgm_track(bgm_id)

    if track:
        return {"bgm_id": bgm_id, "volume": 0.05}
    else:
        # フォールバック: 元のロジックを使用
        bgm_id = SECTION_BGM_MAP.get(section_type, "none")
        track = get_bgm_track(bgm_id)
        if track:
            return {"bgm_id": bgm_id, "volume": track.default_volume}
        else:
            return {"bgm_id": "none", "volume": 0.0}


def validate_bgm_id(bgm_id: str) -> str:
    """BGM IDを検証し、無効な場合はnoneを返す

    Args:
        bgm_id: 検証するBGM ID

    Returns:
        str: 有効なBGM ID、無効な場合は"none"
    """
    if not bgm_id or not bgm_id.strip():
        return "none"

    bgm_id = bgm_id.strip()
    if bgm_id in BGM_LIBRARY:
        return bgm_id
    else:
        logger.warning(
            f"無効なBGM IDが指定されました: {bgm_id} -> noneにフォールバック"
        )
        return "none"


def format_bgm_choices_for_prompt() -> str:
    """プロンプト用にBGM選択肢を整形

    Returns:
        str: プロンプトに埋め込むBGM選択肢の説明文
    """
    lines = ["利用可能なBGM:"]

    for bgm_id, track in BGM_LIBRARY.items():
        lines.append(f"- {bgm_id}: {track.name} - {track.description}")

    return "\n".join(lines)
