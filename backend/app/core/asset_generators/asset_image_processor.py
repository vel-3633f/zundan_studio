"""画像処理ユーティリティ"""

from PIL import Image, ImageDraw


def apply_rounded_corners(
    image: Image.Image,
    radius: int = 80,
    border_width: int = 20,
    border_color: tuple = (200, 200, 200),
) -> Image.Image:
    """画像に角丸と枠線を適用

    Args:
        image: 元画像（PIL Image）
        radius: 角の丸みの半径（ピクセル）
        border_width: 枠線の太さ（ピクセル）
        border_color: 枠線の色（RGB）

    Returns:
        Image.Image: 加工後の画像
    """
    # 元画像のサイズを取得
    width, height = image.size

    # アルファチャンネル付きの新しい画像を作成
    # RGBAモードに変換（元画像がRGBの場合）
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # 角丸マスク用の画像を作成（白黒）
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)

    # 角丸の矩形を描画（白で塗りつぶし）
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=radius,
        fill=255,
    )

    # 透明な背景の新しい画像を作成
    rounded_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # マスクを適用して角丸画像を作成
    rounded_image.paste(image, (0, 0), mask)

    # 枠線を描画
    if border_width > 0:
        draw = ImageDraw.Draw(rounded_image)
        # 枠線は内側に描画されるため、半分ずつ内外に配置
        offset = border_width // 2
        draw.rounded_rectangle(
            [(offset, offset), (width - offset, height - offset)],
            radius=radius,
            outline=border_color + (255,),  # RGBA形式に変換（不透明）
            width=border_width,
        )

    return rounded_image

