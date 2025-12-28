"""セクションコンテキスト定義"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from app.models.script_models import ScriptMode, SectionDefinition


@dataclass
class SectionContext:
    """セクション生成時のコンテキスト情報"""

    mode: ScriptMode
    section_definition: SectionDefinition
    story_summary: str
    reference_information: str
    previous_sections: List[Dict[str, Any]]
    # お笑いモード専用
    character_moods: Optional[Dict[str, int]] = None
    forced_ending_type: Optional[str] = None
    is_final_section: bool = False

