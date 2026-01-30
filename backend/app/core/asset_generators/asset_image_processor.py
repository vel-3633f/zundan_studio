"""画像処理ユーティリティ"""
from PIL import Image, ImageDraw
def apply_rounded_corners(
    image: Image.Image,
    radius: int = 80,
    border_width: int = 20,
    border_color: tuple = (200, 200, 200),
) -> Image.Image:
    """画像に角丸と枠線を適用する"""
    width, height = image.size
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=radius,
        fill=255,
    )
    rounded_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    rounded_image.paste(image, (0, 0), mask)
    if border_width > 0:
        draw = ImageDraw.Draw(rounded_image)
        offset = border_width // 2
        draw.rounded_rectangle(
            [(offset, offset), (width - offset, height - offset)],
            radius=radius,
            outline=border_color + (255,),
            width=border_width,
        )
    return rounded_image