"""LLMファクトリーモジュール"""

import os
from typing import Dict, Any, Optional
from botocore.config import Config
from langchain_aws import ChatBedrock
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_bedrock_llm(
    model_id: str,
    temperature: float = 0.7,
    max_tokens: int = 8192,
    region_name: Optional[str] = None,
    request_timeout: int = 600,
) -> ChatBedrock:
    """AWS Bedrock LLMインスタンスを生成する

    Args:
        model_id: BedrockモデルID
        temperature: 温度パラメータ (0.0 ~ 1.0)
        max_tokens: 最大トークン数
        region_name: AWSリージョン名（Noneの場合は環境変数から取得）
        request_timeout: リクエストタイムアウト（秒）

    Returns:
        ChatBedrock: LLMインスタンス

    Raises:
        ValueError: AWS認証情報またはリージョンが設定されていない場合
    """
    # AWS認証情報の確認
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not aws_access_key or not aws_secret_key:
        raise ValueError(
            "AWS認証情報が設定されていません。\n"
            "AWS_ACCESS_KEY_ID と AWS_SECRET_ACCESS_KEY を .env ファイルに設定してください。"
        )

    # リージョンの取得
    if region_name is None:
        region_name = os.getenv("AWS_DEFAULT_REGION")

    if not region_name:
        raise ValueError(
            "AWSリージョンが設定されていません。\n"
            "AWS_DEFAULT_REGION を .env ファイルに設定してください（例: us-east-1）"
        )

    # boto3 Configを使用してタイムアウトを設定
    config = Config(
        read_timeout=request_timeout,
        connect_timeout=10,
        retries={"max_attempts": 3, "mode": "standard"},
    )

    return ChatBedrock(
        model_id=model_id,
        model_kwargs={"temperature": temperature, "max_tokens": max_tokens},
        region_name=region_name,
        config=config,
    )


def create_llm_from_model_config(
    model_config: Dict[str, Any], temperature: Optional[float] = None
) -> ChatBedrock:
    """モデル設定からLLMインスタンスを生成する

    Args:
        model_config: モデル設定辞書（id, provider, max_tokens, default_temperatureを含む）
        temperature: 温度パラメータ（Noneの場合はmodel_configのdefault_temperatureを使用）

    Returns:
        ChatBedrock: LLMインスタンス

    Raises:
        ValueError: サポートされていないプロバイダーの場合
    """
    provider = model_config.get("provider", "bedrock")

    if provider != "bedrock":
        raise ValueError(
            f"サポートされていないプロバイダー: {provider}. Bedrockのみサポートしています。"
        )

    model_id = model_config["id"]
    max_tokens = model_config.get("max_tokens", 8192)

    if temperature is None:
        temperature = model_config.get("default_temperature", 0.7)

    return create_bedrock_llm(
        model_id=model_id, temperature=temperature, max_tokens=max_tokens
    )

