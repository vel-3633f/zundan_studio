"""セクションコンテキスト構築ユーティリティ"""

from typing import Dict, List, Any
from app.models.script_models import ScriptMode
from app.core.script_generators.section_context import SectionContext


def build_context_text(context: SectionContext, mode: ScriptMode) -> str:
    """コンテキスト情報をテキスト化する"""
    context_text = f"""
## ストーリー全体の流れ
{context.story_summary}

## セクション情報
- セクション名: {context.section_definition.section_name}
- 目的: {context.section_definition.purpose}
- 内容: {context.section_definition.content_summary}
- セリフ数範囲: {context.section_definition.min_lines}-{context.section_definition.max_lines}
"""

    if mode in [ScriptMode.COMEDY, ScriptMode.THOUGHT_EXPERIMENT] and context.character_moods:
        mood_descriptions = _get_mood_descriptions(context.character_moods)
        context_text += f"""
## キャラクター機嫌レベル
- ずんだもん: {context.character_moods['zundamon']}/100 → {mood_descriptions['zundamon']}
- めたん: {context.character_moods['metan']}/100 → {mood_descriptions['metan']}
- つむぎ: {context.character_moods['tsumugi']}/100 → {mood_descriptions['tsumugi']}
"""
        if context.is_final_section and context.forced_ending_type:
            context_text += f"""
## 強制終了の実装
このセクションは最終セクションです。
強制終了タイプ「{context.forced_ending_type}」で唐突に終わらせてください。
話が盛り上がっている最中に終了し、誰も成長せず、何も解決しません。
"""

    if context.previous_sections:
        context_text += "\n## 前のセクションまでの展開\n"
        for prev in context.previous_sections:
            context_text += f"""
### {prev['section_name']}（{prev['segment_count']}セリフ）
- 最後の話者: {prev['last_speaker']}
- 最後のセリフ: {prev['last_text']}
- 要約: {prev['summary']}
"""

    return context_text


def _get_mood_descriptions(moods: Dict[str, int]) -> Dict[str, str]:
    """機嫌レベルから説明文を生成する"""
    descriptions = {}
    for char, mood in moods.items():
        if mood >= 70:
            if char == "zundamon":
                descriptions[char] = "傲慢で攻撃的、自信満々"
            elif char == "metan":
                descriptions[char] = "冷静で論理的、的確なツッコミ"
            else:  # tsumugi
                descriptions[char] = "陽気に煽る、積極的に話をややこしくする"
        elif mood >= 30:
            if char == "zundamon":
                descriptions[char] = "標準的な傲慢さ"
            elif char == "metan":
                descriptions[char] = "普通のツッコミ、適度なイライラ"
            else:  # tsumugi
                descriptions[char] = "普通の煽り、適度に話をかき回す"
        else:
            if char == "zundamon":
                descriptions[char] = "言い訳がましい、被害者面"
            elif char == "metan":
                descriptions[char] = "感情的、容赦ないキレ方、塩対応"
            else:  # tsumugi
                descriptions[char] = "無関心、塩対応、やる気なし"
    return descriptions

