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
                "text": "今日の動画はここまでなのだ！",
                "background": "blue_sky",
                "expression": "happy",
                "visible_characters": ["zundamon"],
            },
            {
                "speaker": "zundamon",
                "text": "この動画が役に立ったら、チャンネル登録と高評価をお願いするのだ！",
                "background": "blue_sky",
                "expression": "excited",
                "visible_characters": ["zundamon"],
            },
            {
                "speaker": "zundamon",
                "text": "じゃないと、ずんだもんがお腹空きすぎて倒れちゃうのだ～！",
                "background": "blue_sky",
                "expression": "sick",
                "visible_characters": ["zundamon"],
            },
            {
                "speaker": "zundamon",
                "text": "それじゃあまた次の動画で会おうなのだ！バイバイなのだ〜！",
                "background": "blue_sky",
                "expression": "happy",
                "visible_characters": ["zundamon"],
            },
        ]

    @staticmethod
    def get_default_conversation() -> List[Dict[str, str]]:
        """デフォルト会話を取得"""
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
