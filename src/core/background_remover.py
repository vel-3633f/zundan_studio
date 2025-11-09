"""
背景除去処理モジュール

rembgライブラリを使用して画像から背景を除去します。
isnet-animeモデルを使用してアニメ・イラストに特化した高精度な背景除去を行います。
"""

import logging
from PIL import Image
from rembg import remove
from io import BytesIO

logger = logging.getLogger(__name__)


class BackgroundRemover:
    """背景除去処理クラス"""

    @staticmethod
    def remove_background(input_image: Image.Image) -> Image.Image:
        """
        画像から背景を除去する

        Args:
            input_image: 入力画像（PIL Image）

        Returns:
            背景が除去された画像（PNG、アルファチャンネル付き）

        Raises:
            Exception: 背景除去処理が失敗した場合
        """
        try:
            logger.info("背景除去処理を開始します")

            # PIL ImageをバイトストリームにエンコードしてRGBに変換
            if input_image.mode != "RGB":
                input_image = input_image.convert("RGB")

            # 画像をバイトストリームに変換
            input_bytes = BytesIO()
            input_image.save(input_bytes, format="PNG")
            input_bytes = input_bytes.getvalue()

            # rembgで背景除去（isnet-animeモデルを使用）
            output_bytes = remove(input_bytes, session=None, model_name="isnet-anime")

            # バイトストリームをPIL Imageに変換
            output_image = Image.open(BytesIO(output_bytes))

            logger.info("背景除去処理が完了しました")
            return output_image

        except Exception as e:
            logger.error(f"背景除去処理に失敗しました: {e}")
            raise Exception(f"背景除去処理に失敗しました: {e}")
