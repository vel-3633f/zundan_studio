"""Imagen 4を使用したアイテム画像自動生成"""

import os
from typing import List, Dict, Optional
from pathlib import Path

from app.config import Paths
from app.core.asset_generators.asset_generator_base import AssetImageGenerator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ItemImageGenerator(AssetImageGenerator):
    """Imagen 4を使用したアイテム画像自動生成クラス"""

    def __init__(self, llm_model: Optional[str] = None):
        """初期化

        Args:
            llm_model: プロンプト生成用のBedrockモデルID（省略時はデフォルトモデルを使用）
        """
        items_dir = os.path.join(Paths.get_assets_dir(), "items")
        prompt_file = (
            Path(__file__).parent.parent / "prompts" / "assets" / "item_prompt_creator.md"
        )
        super().__init__(
            output_dir=items_dir, prompt_file=prompt_file, llm_model=llm_model
        )
        # アイテム画像生成は imagen-4.0-generate-001 を使用
        self.model = "imagen-4.0-generate-001"

    def get_user_prompt_template(self) -> str:
        """ユーザープロンプトのテンプレートを取得

        Returns:
            str: プロンプトテンプレート
        """
        return "アイテム名: {item}"

    def get_prompt_variable_name(self) -> str:
        """プロンプト変数名を取得

        Returns:
            str: 変数名
        """
        return "item"

    def validate_item_name(self, item_name: str) -> bool:
        """アイテム名が3単語形式か検証

        Args:
            item_name: アイテム名

        Returns:
            bool: 有効な場合True
        """
        parts = item_name.split("_")
        if len(parts) != 3:
            return False
        return all(part.islower() and part.isalpha() for part in parts)

    def check_item_exists(self, item_name: str) -> bool:
        """アイテム画像が存在するかチェック

        Args:
            item_name: アイテム名（拡張子なし）

        Returns:
            bool: 存在する場合True
        """
        return self.check_image_exists(item_name, extensions=[".png"])

    def generate_item_prompt(self, item_name: str) -> str:
        """アイテム名から画像生成プロンプトを作成

        Args:
            item_name: アイテム名（例: "steaming_hot_ramen"）

        Returns:
            str: 画像生成用プロンプト
        """
        return self.generate_prompt(item_name)

    def generate_item_image(
        self, item_name: str, validate_name: bool = True
    ) -> str:
        """アイテム画像を生成して保存

        Args:
            item_name: アイテム名
            validate_name: 3単語形式の検証を行うか（デフォルト: True）

        Returns:
            str: 保存された画像のパス

        Raises:
            ValueError: アイテム名が無効な場合
            Exception: 画像生成に失敗した場合
        """
        # 3単語形式の検証
        if validate_name and not self.validate_item_name(item_name):
            logger.warning(
                f"Item name '{item_name}' does not follow 3-word convention"
            )
            # 警告のみで処理は続行

        logger.info(f"Generating item image: {item_name}")

        # アイテム画像は正方形に近い形で生成
        return self.generate_image(
            item_name,
            aspect_ratio="1:1",  # 正方形
            image_size="2K",
        )

    def generate_missing_items(
        self, item_names: List[str], validate_names: bool = True
    ) -> Dict[str, str]:
        """未存在のアイテムを一括生成

        Args:
            item_names: 生成対象のアイテム名リスト
            validate_names: 3単語形式の検証を行うか

        Returns:
            Dict[str, str]: {アイテム名: 保存パス} の辞書
        """
        generated = {}
        skipped = []
        failed = []

        for item_name in item_names:
            # 既存チェック
            if self.check_item_exists(item_name):
                logger.info(f"Item already exists: {item_name}")
                skipped.append(item_name)
                continue

            # 3単語形式の検証（オプション）
            if validate_names and not self.validate_item_name(item_name):
                logger.warning(
                    f"Item name '{item_name}' does not follow 3-word convention, but continuing..."
                )

            # 生成
            try:
                path = self.generate_item_image(
                    item_name, validate_name=validate_names
                )
                generated[item_name] = path
            except Exception as e:
                logger.error(f"Failed to generate '{item_name}': {e}")
                failed.append(item_name)

        # サマリーログ
        logger.info(
            f"Item generation summary: "
            f"Generated={len(generated)}, "
            f"Skipped={len(skipped)}, "
            f"Failed={len(failed)}"
        )

        return generated

    def get_existing_items(self) -> List[str]:
        """既存のアイテム画像名のリストを取得

        Returns:
            List[str]: アイテム名のリスト（拡張子なし）
        """
        return self.get_existing_images(extensions=[".png"])

    def get_items_by_category(self) -> Dict[str, List[str]]:
        """カテゴリー別にアイテムを取得

        Returns:
            Dict[str, List[str]]: {カテゴリー名: アイテム名リスト}
        """
        categories = {}

        if not os.path.exists(self.output_dir):
            return categories

        # ルートディレクトリのアイテム
        root_items = []
        for filename in os.listdir(self.output_dir):
            path = os.path.join(self.output_dir, filename)
            if os.path.isfile(path) and filename.endswith(".png"):
                item_name = os.path.splitext(filename)[0]
                root_items.append(item_name)

        if root_items:
            categories["uncategorized"] = sorted(root_items)

        # サブディレクトリのアイテム
        for category_name in os.listdir(self.output_dir):
            category_path = os.path.join(self.output_dir, category_name)
            if os.path.isdir(category_path):
                items = []
                for filename in os.listdir(category_path):
                    if filename.endswith(".png"):
                        item_name = os.path.splitext(filename)[0]
                        items.append(item_name)

                if items:
                    categories[category_name] = sorted(items)

        return categories
