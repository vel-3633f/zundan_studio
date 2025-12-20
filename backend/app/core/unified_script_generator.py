from typing import Union, Dict, Any, Optional, Callable, Tuple

from app.models.script_models import (
    ScriptMode,
    FoodTitle,
    FoodOutline,
    FoodScript,
    ComedyTitle,
    ComedyOutline,
    ComedyScript,
)
from app.core.food_script_generator import FoodScriptGenerator
from app.core.comedy_script_generator import ComedyScriptGenerator
from app.core.generate_food_over import (
    search_food_information,
    format_search_results_for_prompt,
    create_llm_instance,
)
from app.config.models import get_model_config, get_default_model_config
from app.utils_legacy.logger import get_logger

logger = get_logger(__name__)


class UnifiedScriptGenerator:
    """統合台本生成エンジン（モード別分岐処理）"""

    def __init__(self, mode: ScriptMode):
        """
        Args:
            mode: 生成モード（FOOD or COMEDY）
        """
        self.mode = mode
        if mode == ScriptMode.FOOD:
            self.generator = FoodScriptGenerator()
        else:
            self.generator = ComedyScriptGenerator()


    def generate_title(
        self,
        input_text: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Tuple[Union[FoodTitle, ComedyTitle], str, Dict[str, Any]]:
        """モード別タイトル生成

        Args:
            input_text: 食べ物名（FOODモード）またはテーマ（COMEDYモード）
            model: 使用するモデルID
            temperature: 生成温度
            progress_callback: 進捗通知用コールバック関数

        Returns:
            Tuple[タイトル, 参照情報, モデル設定]
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

            # お笑いモードの場合はtemperatureを高めに調整
            if self.mode == ScriptMode.COMEDY and temperature < 0.8:
                temperature = 0.8
                logger.info(f"お笑いモードのためtemperatureを{temperature}に調整")

            llm = create_llm_instance(model, temperature, model_config)

            # 食べ物モードの場合は検索実行
            reference_info = ""
            search_results = {}
            if self.mode == ScriptMode.FOOD:
                if progress_callback:
                    progress_callback("🔍 食べ物情報を検索中...")
                search_results = search_food_information(input_text)
                reference_info = format_search_results_for_prompt(search_results)

            # タイトル生成
            if self.mode == ScriptMode.FOOD:
                title = self.generator.generate_title(
                    input_text, search_results, llm, progress_callback
                )
            else:
                title = self.generator.generate_title(
                    input_text, llm, progress_callback
                )


            return (
                title,
                reference_info,
                {
                    "model": model,
                    "temperature": temperature,
                    "model_config": model_config,
                    "search_results": search_results,
                },
            )

        except Exception as e:
            error_msg = f"タイトル生成エラー ({self.mode.value}): {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def generate_outline(
        self,
        title_data: Union[FoodTitle, ComedyTitle],
        reference_info: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Tuple[Union[FoodOutline, ComedyOutline], Dict[str, Any]]:
        """モード別アウトライン生成

        Args:
            title_data: 生成されたタイトル
            reference_info: 参照情報（FOODモードのみ）
            model: 使用するモデルID
            temperature: 生成温度
            progress_callback: 進捗通知用コールバック関数

        Returns:
            Tuple[アウトライン, モデル設定]
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

            # お笑いモードの場合はtemperatureを高めに調整
            if self.mode == ScriptMode.COMEDY and temperature < 0.8:
                temperature = 0.8

            llm = create_llm_instance(model, temperature, model_config)

            # アウトライン生成
            outline = (
                self.generator.generate_outline(
                    title_data, reference_info, llm, progress_callback
                )
                if self.mode == ScriptMode.FOOD
                else self.generator.generate_outline(title_data, llm, progress_callback)
            )


            return outline, {
                "model": model,
                "temperature": temperature,
                "model_config": model_config,
            }

        except Exception as e:
            error_msg = f"アウトライン生成エラー ({self.mode.value}): {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def generate_script(
        self,
        outline_data: Union[FoodOutline, ComedyOutline],
        reference_info: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> Union[FoodScript, ComedyScript]:
        """モード別台本生成

        Args:
            outline_data: 生成されたアウトライン
            reference_info: 参照情報（FOODモードのみ）
            model: 使用するモデルID
            temperature: 生成温度
            progress_callback: 進捗通知用コールバック関数(message, progress)

        Returns:
            生成された台本
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

            # お笑いモードの場合はtemperatureを高めに調整
            if self.mode == ScriptMode.COMEDY and temperature < 0.8:
                temperature = 0.8

            llm = create_llm_instance(model, temperature, model_config)

            # 台本生成
            if self.mode == ScriptMode.FOOD:
                script = self.generator.generate_script(
                    outline_data, reference_info, llm, progress_callback
                )
            else:
                script = self.generator.generate_script(
                    outline_data, llm, progress_callback
                )


            return script

        except Exception as e:
            error_msg = f"台本生成エラー ({self.mode.value}): {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def generate_full_script(
        self,
        input_text: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> Union[FoodScript, ComedyScript]:
        """3段階一括生成（Title → Outline → Script）

        Args:
            input_text: 食べ物名（FOODモード）またはテーマ（COMEDYモード）
            model: 使用するモデルID
            temperature: 生成温度
            progress_callback: 進捗通知用コールバック関数(message, progress)

        Returns:
            生成された台本
        """

        try:
            # Step 1: タイトル生成
            if progress_callback:
                progress_callback("📝 タイトルを生成中...", 0.0)

            title, reference_info, model_settings = self.generate_title(
                input_text,
                model,
                temperature,
                lambda msg: progress_callback(msg, 0.0) if progress_callback else None,
            )

            # Step 2: アウトライン生成
            if progress_callback:
                progress_callback("📋 アウトラインを生成中...", 0.2)

            outline, _ = self.generate_outline(
                title,
                reference_info,
                model_settings["model"],
                model_settings["temperature"],
                lambda msg: progress_callback(msg, 0.2) if progress_callback else None,
            )

            # Step 3: 台本生成
            if progress_callback:
                progress_callback("🎬 台本を生成中...", 0.4)

            script = self.generate_script(
                outline,
                reference_info,
                model_settings["model"],
                model_settings["temperature"],
                lambda msg, prog: (
                    progress_callback(msg, 0.4 + (prog * 0.6))
                    if progress_callback
                    else None
                ),
            )


            return script

        except Exception as e:
            error_msg = f"完全台本生成エラー ({self.mode.value}): {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
