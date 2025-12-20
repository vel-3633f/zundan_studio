"""AI models configuration"""

from typing import List, Dict, Any

# 利用可能なAIモデルの設定
AVAILABLE_MODELS: List[Dict[str, Any]] = [
    {
        "id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "name": "Claude Sonnet 4.5",
        "provider": "bedrock",
        "temperature_range": (0.0, 1.0),
        "default_temperature": 1.0,
        "max_tokens": 64000,
        "recommended": True,
    },
    {
        "id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "name": "Claude Haiku 4.5",
        "provider": "bedrock",
        "temperature_range": (0.0, 1.0),
        "default_temperature": 1.0,
        "max_tokens": 64000,
        "recommended": False,
    },
]

# デフォルトモデル設定
DEFAULT_MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


# モデル設定を取得する関数
def get_model_config(model_id: str) -> Dict[str, Any]:
    """指定されたモデルIDの設定を取得する"""
    for model in AVAILABLE_MODELS:
        if model["id"] == model_id:
            return model
    return get_default_model_config()


def get_default_model_config() -> Dict[str, Any]:
    """デフォルトモデルの設定を取得する"""
    return get_model_config(DEFAULT_MODEL_ID)


def get_recommended_model_id() -> str:
    """推奨モデルのIDを取得する"""
    for model in AVAILABLE_MODELS:
        if model.get("recommended", False):
            return model["id"]
    return DEFAULT_MODEL_ID
