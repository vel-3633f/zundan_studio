"""Imagen 4を使用した背景画像自動生成"""

import os
from typing import List, Dict, Optional
from pathlib import Path

from config import Paths
from app.utils_legacy.logger import get_logger
from app.utils_legacy.llm_factory import create_bedrock_llm
from app.config.models import get_default_model_config
from langchain_core.prompts import ChatPromptTemplate

logger = get_logger(__name__)


class BackgroundImageGenerator:
    """Imagen 4を使用した背景画像自動生成クラス"""

    def __init__(self, llm_model: Optional[str] = None):
        """初期化

        Args:
            llm_model: プロンプト生成用のBedrockモデルID（省略時はデフォルトモデルを使用）
        """
        # モデル設定を取得
        if llm_model is None:
            model_config = get_default_model_config()
            llm_model = model_config["id"]
            logger.info(f"デフォルトモデルを使用: {llm_model}")
        self.client = None
        self.model = "imagen-4.0-ultra-generate-001"
        self.backgrounds_dir = Paths.get_backgrounds_dir()

        # AWS Bedrock LLMインスタンス生成
        aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.llm = create_bedrock_llm(
            model_id=llm_model,
            temperature=0.7,
            max_tokens=4096,
            region_name=aws_region,
        )
        self.prompt_file = (
            Path(__file__).parent.parent / "prompts" / "background_prompt_creator.md"
        )
        self._ensure_backgrounds_dir()

    def _ensure_backgrounds_dir(self):
        """背景ディレクトリが存在することを確認"""
        os.makedirs(self.backgrounds_dir, exist_ok=True)
        logger.info(f"Background directory: {self.backgrounds_dir}")

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

    def check_background_exists(self, bg_name: str) -> bool:
        """背景画像が存在するかチェック

        Args:
            bg_name: 背景名（拡張子なし）

        Returns:
            bool: 存在する場合True
        """
        extensions = [".png", ".jpg", ".jpeg", ".webp"]
        for ext in extensions:
            path = os.path.join(self.backgrounds_dir, f"{bg_name}{ext}")
            if os.path.exists(path):
                logger.debug(f"Background exists: {path}")
                return True
        return False

    def _create_prompt_with_llm(self, bg_name: str) -> str:
        """LLMを使って背景名から詳細な画像生成プロンプトを作成"""
        try:
            if not self.prompt_file.exists():
                raise FileNotFoundError(f"Prompt file not found: {self.prompt_file}")

            with open(self.prompt_file, "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()

            scene_description = bg_name.replace("_", " ")

            prompt_template = ChatPromptTemplate.from_messages(
                [("system", system_prompt), ("user", "背景情報: {scene}")]
            )

            chain = prompt_template | self.llm
            response = chain.invoke({"scene": scene_description})

            generated_prompt = response.content.strip()
            logger.info(
                f"Generated prompt for '{bg_name}': {generated_prompt[:100]}..."
            )

            return generated_prompt

        except Exception as e:
            logger.error(f"Failed to create prompt with LLM for '{bg_name}': {e}")
            raise

    def generate_background_prompt(self, bg_name: str) -> str:
        """背景名から画像生成プロンプトを作成

        Args:
            bg_name: 背景名（例: "hospital_room", "kitchen"）

        Returns:
            str: 画像生成用プロンプト
        """
        return self._create_prompt_with_llm(bg_name)

    def generate_background_image(self, bg_name: str) -> str:
        """背景画像を生成して保存

        Args:
            bg_name: 背景名

        Returns:
            str: 保存された画像のパス

        Raises:
            Exception: 画像生成に失敗した場合
        """
        # クライアント初期化
        self._initialize_client()

        # プロンプト生成
        prompt = self.generate_background_prompt(bg_name)

        logger.info(f"Generating background image: {bg_name}")
        logger.info(f"Prompt: {prompt}")

        try:
            from google.genai.types import GenerateImagesConfig

            # 画像生成
            image_result = self.client.models.generate_images(
                model=self.model,
                prompt=prompt,
                config=GenerateImagesConfig(
                    image_size="2K",
                    aspect_ratio="16:9",
                    number_of_images=1,
                    person_generation="dont_allow",
                ),
            )

            output_path = os.path.join(self.backgrounds_dir, f"{bg_name}.png")

            # 画像を取得して保存
            generated_image = image_result.generated_images[0]

            # PIL Imageとして取得
            if hasattr(generated_image, 'image'):
                img = generated_image.image
            else:
                raise ValueError(f"Cannot extract image from result: {type(generated_image)}")

            # 画像を保存（拡張子から自動判定）
            img.save(output_path)

            # 保存確認
            if not os.path.exists(output_path):
                raise IOError(f"Image file was not saved: {output_path}")

            file_size = os.path.getsize(output_path)
            logger.info(f"Successfully saved background: {output_path} ({file_size} bytes)")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate background '{bg_name}': {e}", exc_info=True)
            raise

    def generate_missing_backgrounds(
        self,
        background_names: List[str],
        fixed_backgrounds: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """未存在の背景を一括生成

        Args:
            background_names: 生成対象の背景名リスト
            fixed_backgrounds: 固定背景（生成スキップ対象）のリスト

        Returns:
            Dict[str, str]: {背景名: 保存パス} の辞書
        """
        if fixed_backgrounds is None:
            fixed_backgrounds = ["modern_study_room", "library"]

        generated = {}
        skipped = []
        failed = []

        for bg_name in background_names:
            # 固定背景はスキップ
            if bg_name in fixed_backgrounds:
                logger.info(f"Skipping fixed background: {bg_name}")
                skipped.append(bg_name)
                continue

            # 既存チェック
            if self.check_background_exists(bg_name):
                logger.info(f"Background already exists: {bg_name}")
                skipped.append(bg_name)
                continue

            # 生成
            try:
                path = self.generate_background_image(bg_name)
                generated[bg_name] = path
            except Exception as e:
                logger.error(f"Failed to generate '{bg_name}': {e}")
                failed.append(bg_name)

        # サマリーログ
        logger.info(
            f"Background generation summary: "
            f"Generated={len(generated)}, "
            f"Skipped={len(skipped)}, "
            f"Failed={len(failed)}"
        )

        return generated

    def get_existing_backgrounds(self) -> List[str]:
        """既存の背景画像名のリストを取得

        Returns:
            List[str]: 背景名のリスト（拡張子なし）
        """
        if not os.path.exists(self.backgrounds_dir):
            return []

        extensions = [".png", ".jpg", ".jpeg", ".webp"]
        backgrounds = []

        for filename in os.listdir(self.backgrounds_dir):
            path = os.path.join(self.backgrounds_dir, filename)
            if os.path.isfile(path):
                name, ext = os.path.splitext(filename)
                if ext.lower() in extensions:
                    backgrounds.append(name)

        return sorted(list(set(backgrounds)))
