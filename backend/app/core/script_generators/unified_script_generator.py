from typing import Dict, Any, Optional, Callable, Tuple

from app.models.script_models import (
    ScriptMode,
    ComedyTitle,
    ComedyOutline,
    ComedyScript,
    ThoughtExperimentTitle,
    ThoughtExperimentOutline,
    ThoughtExperimentScript,
    YouTubeMetadata,
)
from app.core.script_generators.comedy import ComedyScriptGenerator
from app.core.script_generators.thought_experiment import ThoughtExperimentScriptGenerator
from app.core.script_generators.generate_food_over import create_llm_instance
from app.config.models import get_model_config, get_default_model_config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UnifiedScriptGenerator:
    """統合台本生成エンジン（ComedyとThoughtExperiment対応）"""

    def __init__(self, mode: ScriptMode = ScriptMode.COMEDY):
        """
        Args:
            mode: 生成モード（COMEDY or THOUGHT_EXPERIMENT）
        """
        if mode not in [ScriptMode.COMEDY, ScriptMode.THOUGHT_EXPERIMENT]:
            raise ValueError(f"このシステムはComedyモードとThoughtExperimentモードのみ対応しています（指定: {mode.value}）")
        
        self.mode = mode
        if mode == ScriptMode.COMEDY:
            self.generator = ComedyScriptGenerator()
        elif mode == ScriptMode.THOUGHT_EXPERIMENT:
            self.generator = ThoughtExperimentScriptGenerator()

    def generate_title(
        self,
        input_text: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Tuple[Any, str, Dict[str, Any]]:
        """タイトル生成

        Args:
            input_text: テーマ
            model: 使用するモデルID
            temperature: 生成温度
            progress_callback: 進捗通知用コールバック関数

        Returns:
            Tuple[タイトル, 参照情報（空文字）, モデル設定]
        """

        try:
            # モデル設定
            if model is None:
                model_config = get_default_model_config()
                model = model_config["id"]
            else:
                model_config = get_model_config(model)

            if temperature is None:
                temperature = model_config["default_temperature"]

            # モードに応じてtemperatureを調整
            if self.mode == ScriptMode.COMEDY:
                if temperature < 0.8:
                    temperature = 0.8
                    logger.info(f"お笑いモードのためtemperatureを{temperature}に調整")
            elif self.mode == ScriptMode.THOUGHT_EXPERIMENT:
                if temperature < 0.7:
                    temperature = 0.7
                    logger.info(f"思考実験モードのためtemperatureを{temperature}に調整")

            llm = create_llm_instance(model, temperature, model_config)

            # タイトル生成
            title = self.generator.generate_title(input_text, llm, progress_callback)

            return (
                title,
                "",  # 参照情報は不要
                {
                    "model": model,
                    "temperature": temperature,
                    "model_config": model_config,
                },
            )

        except Exception as e:
            logger.error(f"タイトル生成エラー ({self.mode.value}): {str(e)}", exc_info=True)
            raise

    def generate_outline(
        self,
        title_data: Any,
        reference_info: str = "",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Tuple[Any, Optional[YouTubeMetadata], Dict[str, Any]]:
        """アウトライン生成

        Args:
            title_data: 生成されたタイトル
            reference_info: 参照情報（使用されない）
            model: 使用するモデルID
            temperature: 生成温度
            progress_callback: 進捗通知用コールバック関数

        Returns:
            Tuple[アウトライン, YouTubeメタデータ, モデル設定]
        """

        try:
            # モデル設定
            if model is None:
                model_config = get_default_model_config()
                model = model_config["id"]
            else:
                model_config = get_model_config(model)

            if temperature is None:
                temperature = model_config["default_temperature"]

            # モードに応じてtemperatureを調整
            if self.mode == ScriptMode.COMEDY:
                if temperature < 0.8:
                    temperature = 0.8
                    logger.info(f"お笑いモードのためtemperatureを{temperature}に調整")
            elif self.mode == ScriptMode.THOUGHT_EXPERIMENT:
                if temperature < 0.7:
                    temperature = 0.7
                    logger.info(f"思考実験モードのためtemperatureを{temperature}に調整")

            llm = create_llm_instance(model, temperature, model_config)

            # アウトライン生成（メタデータも同時生成）
            outline, youtube_metadata = self.generator.generate_outline(
                title_data, llm, progress_callback
            )

            return (
                outline,
                youtube_metadata,
                {
                    "model": model,
                    "temperature": temperature,
                    "model_config": model_config,
                },
            )

        except Exception as e:
            logger.error(f"アウトライン生成エラー ({self.mode.value}): {str(e)}", exc_info=True)
            raise

    def generate_script(
        self,
        outline_data: Any,
        reference_info: str = "",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> Tuple[Any, Dict[str, Any]]:
        """台本生成

        Args:
            outline_data: 生成されたアウトライン
            reference_info: 参照情報（使用されない）
            model: 使用するモデルID
            temperature: 生成温度
            progress_callback: 進捗通知用コールバック関数

        Returns:
            Tuple[台本, モデル設定]
        """

        try:
            # モデル設定
            if model is None:
                model_config = get_default_model_config()
                model = model_config["id"]
            else:
                model_config = get_model_config(model)

            if temperature is None:
                temperature = model_config["default_temperature"]

            # モードに応じてtemperatureを調整
            if self.mode == ScriptMode.COMEDY:
                if temperature < 0.8:
                    temperature = 0.8
                    logger.info(f"お笑いモードのためtemperatureを{temperature}に調整")
            elif self.mode == ScriptMode.THOUGHT_EXPERIMENT:
                if temperature < 0.7:
                    temperature = 0.7
                    logger.info(f"思考実験モードのためtemperatureを{temperature}に調整")

            llm = create_llm_instance(model, temperature, model_config)

            # 台本生成
            script = self.generator.generate_script(outline_data, llm, progress_callback)

            return (
                script,
                {
                    "model": model,
                    "temperature": temperature,
                    "model_config": model_config,
                },
            )

        except Exception as e:
            logger.error(f"台本生成エラー ({self.mode.value}): {str(e)}", exc_info=True)
            raise
