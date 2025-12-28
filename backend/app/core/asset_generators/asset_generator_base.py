"""画像生成の基底クラス"""

import os
from typing import List, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from PIL import Image
from app.utils.logger import get_logger
from app.utils.llm_factory import create_bedrock_llm
from app.config.models import get_default_model_config
from langchain_core.prompts import ChatPromptTemplate
from .asset_image_processor import apply_rounded_corners

logger = get_logger(__name__)


class AssetImageGenerator(ABC):
    """画像生成の基底クラス"""

    def __init__(
        self,
        output_dir: str,
        prompt_file: Path,
        llm_model: Optional[str] = None,
    ):
        """初期化

        Args:
            output_dir: 画像の出力ディレクトリ
            prompt_file: プロンプト生成用のマークダウンファイル
            llm_model: プロンプト生成用のBedrockモデルID（省略時はデフォルトモデルを使用）
        """
        # モデル設定を取得
        if llm_model is None:
            model_config = get_default_model_config()
            llm_model = model_config["id"]
            logger.info(f"デフォルトモデルを使用: {llm_model}")
        self.client = None
        self.model = "imagen-4.0-ultra-generate-001"
        self.output_dir = output_dir

        aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.llm = create_bedrock_llm(
            model_id=llm_model,
            temperature=0.7,
            max_tokens=4096,
            region_name=aws_region,
        )
        self.prompt_file = prompt_file
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """出力ディレクトリが存在することを確認"""
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")

    def _initialize_client(self):
        """Google Gen AIクライアントを初期化"""
        if self.client is not None:
            return

        try:
            from google import genai

            self.client = genai.Client()
            logger.info("Google Gen AI client initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import google-genai: {e}")
            raise ImportError(
                "google-genai package is not installed. "
                "Please install it with: pip install google-genai"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Google Gen AI client: {e}")
            raise

    def check_image_exists(
        self, image_name: str, extensions: Optional[List[str]] = None
    ) -> bool:
        """画像が存在するかチェック

        Args:
            image_name: 画像名（拡張子なし）
            extensions: チェックする拡張子のリスト（デフォルト: [".png", ".jpg", ".jpeg", ".webp"]）

        Returns:
            bool: 存在する場合True
        """
        if extensions is None:
            extensions = [".png", ".jpg", ".jpeg", ".webp"]

        for ext in extensions:
            path = os.path.join(self.output_dir, f"{image_name}{ext}")
            if os.path.exists(path):
                return True
        return False

    def _create_prompt_with_llm(self, image_name: str) -> str:
        """LLMを使って画像名から詳細な画像生成プロンプトを作成

        Args:
            image_name: 画像名

        Returns:
            str: 生成されたプロンプト
        """
        try:
            if not self.prompt_file.exists():
                raise FileNotFoundError(f"Prompt file not found: {self.prompt_file}")

            with open(self.prompt_file, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()

            description = image_name.replace("_", " ")

            prompt_template = ChatPromptTemplate.from_messages(
                [("system", system_prompt), ("user", self.get_user_prompt_template())]
            )

            chain = prompt_template | self.llm
            response = chain.invoke({self.get_prompt_variable_name(): description})

            generated_prompt = response.content.strip()
            logger.info(
                f"Generated prompt for '{image_name}': {generated_prompt[:100]}..."
            )

            return generated_prompt

        except Exception as e:
            logger.error(f"Failed to create prompt with LLM for '{image_name}': {e}")
            raise

    @abstractmethod
    def get_user_prompt_template(self) -> str:
        """ユーザープロンプトのテンプレートを取得（サブクラスで実装）

        Returns:
            str: プロンプトテンプレート（例: "背景情報: {scene}"）
        """
        pass

    @abstractmethod
    def get_prompt_variable_name(self) -> str:
        """プロンプト変数名を取得（サブクラスで実装）

        Returns:
            str: 変数名（例: "scene", "item"）
        """
        pass

    def generate_prompt(self, image_name: str) -> str:
        """画像名から画像生成プロンプトを作成

        Args:
            image_name: 画像名

        Returns:
            str: 画像生成用プロンプト
        """
        return self._create_prompt_with_llm(image_name)

    def generate_image(self, image_name: str, **config_overrides) -> str:
        """画像を生成して保存

        Args:
            image_name: 画像名
            **config_overrides: GenerateImagesConfigのオーバーライド設定

        Returns:
            str: 保存された画像のパス

        Raises:
            Exception: 画像生成に失敗した場合
        """
        # クライアント初期化
        self._initialize_client()

        # プロンプト生成
        prompt = self.generate_prompt(image_name)

        logger.info(f"Generating image: {image_name}")
        logger.info(f"Prompt: {prompt}")

        try:
            from google.genai.types import GenerateImagesConfig

            # デフォルト設定
            default_config = {
                "image_size": "2K",
                "aspect_ratio": "16:9",
                "number_of_images": 1,
                "person_generation": "dont_allow",
            }

            # オーバーライド設定をマージ
            config = {**default_config, **config_overrides}

            # 画像生成
            image_result = self.client.models.generate_images(
                model=self.model,
                prompt=prompt,
                config=GenerateImagesConfig(**config),
            )

            output_path = os.path.join(self.output_dir, f"{image_name}.png")

            # 画像を取得して保存
            generated_image = image_result.generated_images[0]

            # PIL Imageとして取得
            # Google Gen AIのImageオブジェクトからPIL Imageに変換
            from io import BytesIO

            if hasattr(generated_image, "image"):
                # Imageオブジェクトのバイトデータを取得してPIL Imageに変換
                image_bytes = generated_image.image.image_bytes
                img = Image.open(BytesIO(image_bytes))
            else:
                raise ValueError(
                    f"Cannot extract image from result: {type(generated_image)}"
                )

            # 角丸と枠線を適用
            img = apply_rounded_corners(img)

            # 画像を保存（PNG形式でアルファチャンネルを保持）
            img.save(output_path, format="PNG")

            # 保存確認
            if not os.path.exists(output_path):
                raise IOError(f"Image file was not saved: {output_path}")

            file_size = os.path.getsize(output_path)
            logger.info(f"Successfully saved image: {output_path} ({file_size} bytes)")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate image '{image_name}': {e}", exc_info=True)
            raise

    def get_existing_images(self, extensions: Optional[List[str]] = None) -> List[str]:
        """既存の画像名のリストを取得

        Args:
            extensions: チェックする拡張子のリスト

        Returns:
            List[str]: 画像名のリスト（拡張子なし）
        """
        if extensions is None:
            extensions = [".png", ".jpg", ".jpeg", ".webp"]

        if not os.path.exists(self.output_dir):
            return []

        images = []

        for filename in os.listdir(self.output_dir):
            path = os.path.join(self.output_dir, filename)
            if os.path.isfile(path):
                name, ext = os.path.splitext(filename)
                if ext.lower() in extensions:
                    images.append(name)

        return sorted(list(set(images)))
