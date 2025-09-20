"""AI models configuration"""

from typing import List, Dict, Any

# 利用可能なAIモデルの設定
AVAILABLE_MODELS: List[Dict[str, Any]] = [
    {
        "id": "gpt-4.1-mini",
        "name": "GPT-4.1-mini",
        "temperature_range": (0.0, 1.0),
        "default_temperature": 0.8,
        "recommended": True,
    },
    {
        "id": "gpt-4.1",
        "name": "GPT-4.1",
        "temperature_range": (0.0, 1.0),
        "default_temperature": 0.8,
        "recommended": True,
    },
    {
        "id": "gpt-5",
        "name": "GPT-5",
        "temperature_range": (0.0, 1.0),
        "default_temperature": 0.8,
        "recommended": True,
    },
    {
        "id": "gpt-5-mini",
        "name": "GPT-5-mini",
        "temperature_range": (0.0, 1.0),
        "default_temperature": 0.8,
        "recommended": True,
    },
]

# デフォルトモデル設定
DEFAULT_MODEL_ID = "gpt-5-mini"


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
