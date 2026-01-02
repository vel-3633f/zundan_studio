"""お笑い漫談台本生成API（Comedy専用）"""

from fastapi import APIRouter
from app.models.script_models import ComedyTitleBatch
from .scripts_models import (
    TitleRequest,
    TitleResponse,
    OutlineRequest,
    OutlineResponse,
    ScriptRequest,
    ScriptResponse,
    FullScriptRequest,
    FullScriptResponse,
    ThemeBatchResponse,
    ThemeTitleRequest,
)
from .scripts_handlers import (
    handle_generate_title,
    handle_generate_outline,
    handle_generate_script,
    handle_generate_full_script,
    handle_generate_comedy_titles_batch,
    handle_generate_theme_batch,
    handle_generate_theme_titles,
    handle_save_script_to_file,
    handle_get_available_models,
)

router = APIRouter()


@router.post("/title", response_model=TitleResponse)
async def generate_title(request: TitleRequest):
    """
    タイトル生成（Comedy専用）

    - **input_text**: 漫談のテーマ
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    return await handle_generate_title(request)


@router.post("/outline", response_model=OutlineResponse)
async def generate_outline(request: OutlineRequest):
    """
    アウトライン生成（Comedy専用）

    - **title_data**: 生成されたタイトル
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    return await handle_generate_outline(request)


@router.post("/script", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    """
    台本生成（Comedy専用）

    - **outline_data**: 生成されたアウトライン
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    return await handle_generate_script(request)


@router.post("/full", response_model=FullScriptResponse)
async def generate_full_script(request: FullScriptRequest):
    """
    完全台本生成（3段階一括）（Comedy専用）

    - **input_text**: 漫談のテーマ
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    return await handle_generate_full_script(request)


@router.post("/comedy/titles/batch")
async def generate_comedy_titles_batch():
    """
    お笑いモード: ランダムタイトル量産（20-30個）

    テーマ入力不要で、AIが自動的にバカバカしいタイトルを20-30個生成します。
    """
    return await handle_generate_comedy_titles_batch()


@router.post("/comedy/themes/batch", response_model=ThemeBatchResponse)
async def generate_theme_batch():
    """
    お笑いモード: テーマ候補生成（15-20個）

    テーマ候補（単語・フレーズ）を15-20個生成します。
    """
    return await handle_generate_theme_batch()


@router.post("/comedy/titles/from-theme", response_model=ComedyTitleBatch)
async def generate_titles_from_theme(request: ThemeTitleRequest):
    """
    お笑いモード: テーマベースタイトル生成

    指定されたテーマからタイトルを20個生成します。

    - **theme**: テーマ（単語・フレーズ）
    - **model**: 使用するLLMモデル（省略可）
    - **temperature**: 生成温度（省略可）
    """
    return await handle_generate_theme_titles(request)


@router.post("/save")
async def save_script_to_file(request: dict):
    """
    生成された台本をJSONファイルとして保存
    
    Args:
        request: {"script": 台本データ, "filename": ファイル名（オプション）}
    
    Returns:
        保存されたファイルのパス
    """
    return await handle_save_script_to_file(request)


@router.get("/models")
async def get_available_models():
    """
    利用可能なAIモデルの一覧を取得
    
    Returns:
        - models: 利用可能なモデルのリスト
        - default_model_id: デフォルトモデルID
        - recommended_model_id: 推奨モデルID
    """
    return await handle_get_available_models()


@router.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "service": "comedy_script_generator"}
