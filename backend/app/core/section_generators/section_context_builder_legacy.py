"""レガシーセクションコンテキスト構築ユーティリティ"""

from typing import Dict, List, Any
from app.core.section_generators.base import SectionContext


def build_context_text(context: SectionContext) -> str:
    """コンテキスト情報をテキスト化する（8セクション構造対応）"""
    context_text = f"""
## 全体のアウトライン
- YouTubeタイトル: {context.outline.title}
- 食べ物: {context.outline.food_name}

### セクション別コンテンツ
1. 冒頭フック: {context.outline.hook_content}
2. 食品解説: {context.outline.background_content}
3. 日常導入: {context.outline.daily_content}
4. 楽観期: {context.outline.honeymoon_content}
5. 異変期: {', '.join(context.outline.deterioration_content)}
6. 危機: {context.outline.crisis_content}
7. 真相解明: {context.outline.learning_content}
8. 回復: {context.outline.recovery_content}
"""

    if context.previous_sections:
        context_text += "\n## 前のセクションまでの流れ\n"
        for prev in context.previous_sections:
            context_text += f"""
### {prev['section_name']}（{prev['segment_count']}セリフ）
- 最後の話者: {prev['last_speaker']}
- 最後のセリフ: {prev['last_text']}
- 要約: {prev['summary']}
"""

    return context_text


def replace_outline_variables(
    prompt_text: str, context: SectionContext
) -> str:
    """プロンプト内のアウトライン変数を実際の値で置換する（8セクション構造対応）"""
    replacements = {
        "{{food_name}}": context.food_name,
        "{{outline_title}}": context.outline.title,
        "{{outline_hook_content}}": context.outline.hook_content,
        "{{outline_background_content}}": context.outline.background_content,
        "{{outline_daily_content}}": context.outline.daily_content,
        "{{outline_honeymoon_content}}": context.outline.honeymoon_content,
        "{{outline_deterioration_content}}": "\n".join(
            f"- {symptom}" for symptom in context.outline.deterioration_content
        ),
        "{{outline_crisis_content}}": context.outline.crisis_content,
        "{{outline_learning_content}}": context.outline.learning_content,
        "{{outline_recovery_content}}": context.outline.recovery_content,
    }

    result = prompt_text
    for var, value in replacements.items():
        result = result.replace(var, value)

    return result

