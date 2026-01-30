"""persona.mdとtheme.mdを読み込むユーティリティ"""

from pathlib import Path
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

# プロジェクトルートからの相対パス
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
PERSONA_FILE = PROJECT_ROOT / "doc" / "persona.md"
THEME_FILE = PROJECT_ROOT / "doc" / "theme.md"

# キャッシュ
_persona_cache: Optional[str] = None
_theme_cache: Optional[str] = None


def load_persona_info() -> str:
    """doc/persona.mdを読み込んでプロンプト用に整形
    
    Returns:
        str: persona.mdの内容（ファイルが存在しない場合は空文字列）
    """
    global _persona_cache
    
    if _persona_cache is not None:
        return _persona_cache
    
    try:
        if not PERSONA_FILE.exists():
            logger.warning(f"persona.mdが見つかりません: {PERSONA_FILE}")
            _persona_cache = ""
            return ""
        
        with open(PERSONA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            _persona_cache = content
            logger.info(f"persona.mdを読み込みました: {len(content)}文字")
            return content
            
    except Exception as e:
        logger.error(f"persona.md読み込みエラー: {str(e)}")
        _persona_cache = ""
        return ""


def load_theme_info() -> str:
    """doc/theme.mdを読み込んでプロンプト用に整形
    
    Returns:
        str: theme.mdの内容（ファイルが存在しない場合は空文字列）
    """
    global _theme_cache
    
    if _theme_cache is not None:
        return _theme_cache
    
    try:
        if not THEME_FILE.exists():
            logger.warning(f"theme.mdが見つかりません: {THEME_FILE}")
            _theme_cache = ""
            return ""
        
        with open(THEME_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            _theme_cache = content
            logger.info(f"theme.mdを読み込みました: {len(content)}文字")
            return content
            
    except Exception as e:
        logger.error(f"theme.md読み込みエラー: {str(e)}")
        _theme_cache = ""
        return ""
