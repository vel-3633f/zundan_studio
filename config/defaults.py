"""
デフォルトデータ + UI設定
"""

from typing import Dict, List, Tuple, Any


class DefaultConversations:
    """デフォルト会話データ"""

    @staticmethod
    def get_sample_conversation() -> List[Dict[str, str]]:
        """サンプル会話を取得"""
        return [
            {
                "speaker": "zundamon",
                "text": "こんにちはなのだ！今日もいい天気なのだ！",
                "background": "blue_sky",
                "expression": "happy",
                "visible_characters": ["zundamon", "metan"],
            },
            {
                "speaker": "metan",
                "text": "こんにちは〜！本当にいい天気だっぺ〜",
                "background": "blue_sky",
                "expression": "normal",
                "visible_characters": ["zundamon", "metan"],
            },
            {
                "speaker": "tsumugi",
                "text": "春日部つむぎです。よろしくお願いします！",
                "background": "sakura",
                "expression": "normal",
                "visible_characters": ["zundamon", "tsumugi"],
            },
        ]

    @staticmethod
    def get_reset_conversation() -> List[Dict[str, str]]:
        """リセット用会話を取得"""
        return [
            {
                "speaker": "zundamon",
                "text": "こんにちはなのだ！",
                "background": "default",
                "expression": "normal",
                "visible_characters": ["zundamon", "metan"],
            },
            {
                "speaker": "metan",
                "text": "こんにちは〜だっぺ！",
                "background": "blue_sky",
                "expression": "normal",
                "visible_characters": ["zundamon", "metan"],
            },
        ]


class UIConfig:
    """UI設定"""

    # スライダー設定
    speed_range: Tuple[float, float, float, float] = (
        0.5,
        2.0,
        1.0,
        0.1,
    )  # min, max, default, step
    pitch_range: Tuple[float, float, float, float] = (-0.15, 0.15, 0.0, 0.01)
    intonation_range: Tuple[float, float, float, float] = (0.0, 2.0, 1.0, 0.1)

    # テキストエリア設定
    text_area_height: int = 80

    # カラム設定
    input_columns: List[int] = [
        1,
        3,
        1,
        1,
        2,
    ]  # 話者、テキスト、背景、表情、表示キャラ
    button_columns: List[int] = [1, 1, 1]
    generate_columns: List[int] = [1, 2, 1]


# グローバル設定インスタンス
UI_CONFIG = UIConfig()
