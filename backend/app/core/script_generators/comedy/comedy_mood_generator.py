"""機嫌レベル生成モジュール"""

import random
from typing import Dict

from app.models.script_models import CharacterMood
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ComedyMoodGenerator:
    """機嫌レベル生成クラス"""

    def generate_random_moods(self) -> CharacterMood:
        """ランダムな機嫌レベルを生成する"""
        moods = CharacterMood(
            zundamon=random.randint(0, 100),
            metan=random.randint(0, 100),
            tsumugi=random.randint(0, 100),
        )

        logger.info(
            f"ランダム機嫌レベル生成: "
            f"ずんだもん={moods.zundamon}, "
            f"めたん={moods.metan}, "
            f"つむぎ={moods.tsumugi}"
        )

        return moods

    def get_mood_description(self, character: str, mood: int) -> str:
        """機嫌レベルから説明文を生成する"""
        if mood >= 70:
            if character == "zundamon":
                return "傲慢で攻撃的、自信満々"
            elif character == "metan":
                return "冷静で論理的、的確なツッコミ"
            else:  # tsumugi
                return "陽気に煽る、積極的に話をややこしくする"
        elif mood >= 30:
            if character == "zundamon":
                return "標準的な傲慢さ"
            elif character == "metan":
                return "普通のツッコミ、適度なイライラ"
            else:  # tsumugi
                return "普通の煽り、適度に話をかき回す"
        else:
            if character == "zundamon":
                return "言い訳がましい、被害者面"
            elif character == "metan":
                return "感情的、容赦ないキレ方、塩対応"
            else:  # tsumugi
                return "無関心、塩対応、やる気なし"

