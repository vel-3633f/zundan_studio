"""ロギングユーティリティモジュール"""

import os
import logging
from typing import Optional


# ログレベルの環境変数からの取得（デフォルト: INFO）
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# サードパーティロガーの抑制リスト
SUPPRESSED_LOGGERS = ["moviepy", "PIL", "matplotlib"]


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    モジュール専用ロガーを設定する

    Args:
        name: ロガー名（通常は __name__ を使用）
        level: ログレベル（指定しない場合は環境変数LOG_LEVELを使用）

    Returns:
        設定されたロガー
    """
    logger = logging.getLogger(name)

    # ログレベルを設定
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # ハンドラーが既に追加されていない場合のみ追加
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

    # サードパーティロガーの抑制
    _suppress_third_party_logs()

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得する（setup_loggerのエイリアス）

    Args:
        name: ロガー名（通常は __name__ を使用）

    Returns:
        設定されたロガー
    """
    return setup_logger(name)


def _suppress_third_party_logs():
    """サードパーティライブラリのログを抑制"""
    for logger_name in SUPPRESSED_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

