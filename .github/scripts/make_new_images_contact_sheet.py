from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path.cwd()
OUTPUT = ROOT / "new-images-contact-sheet.jpg"
SOURCE_NAMES = [
    "IMG_0362.jpg", "IMG_0379.jpg", "IMG_0457.jpg", "IMG_0556.jpg",
    "IMG_0616.jpg", "IMG_0629.jpg", "IMG_0664.jpg", "IMG_0678.jpg",
    "IMG_0684.jpg", "IMG_0688.jpg", "IMG_0703.jpg", "IMG_0720.jpg",
    "IMG_0728.jpg", "IMG_0737.jpg", "IMG_0748.jpg", "IMG_0764.jpg",
    "IMG_0782.jpg", "IMG_0842.jpg", "IMG_0858.jpg", "IMG_0906.jpg",
    "IMG_0945.jpg", "IMG_0958.jpg", "IMG_1006.jpg", "IMG_1118.jpg",
    "IMG_1157.jpg", "IMG_1165.jpg", "IMG_1246.jpg", "IMG_1265.jpg",
]

COLS = 4
TILE_W = 420
IMAGE_H = 330
LABEL_H = 54
PAD = 14


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def main() -> None:
    sources = [ROOT / name for name in SOURCE_NAMES]
    missing = [path.name for path in sources if not path.exists()]
    if missing:
        raise SystemExit(f"Mangler bildefiler: {missing}")

    rows = (len(sources) + COLS - 1) // COLS
    canvas_w = PAD + COLS * (TILE_W + PAD)
    canvas_h = PAD + rows * (IMAGE_H + LABEL_H + PAD)
    canvas = Image.new("RGB", (canvas_w, canvas_h), (15, 23, 42))
    draw = ImageDraw.Draw(canvas)
    font = load_font(25)

    for index, path in enumerate(sources):
        row, col = divmod(index, COLS)
        x = PAD + col * (TILE_W + PAD)
        y = PAD + row * (IMAGE_H + LABEL_H + PAD)
        with Image.open(path) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
        tile = ImageOps.contain(image, (TILE_W, IMAGE_H), method=Image.Resampling.LANCZOS)
        tile_bg = Image.new("RGB", (TILE_W, IMAGE_H), (30, 41, 59))
        offset = ((TILE_W - tile.width) // 2, (IMAGE_H - tile.height) // 2)
        tile_bg.paste(tile, offset)
        canvas.paste(tile_bg, (x, y))
        draw.rectangle((x, y + IMAGE_H, x + TILE_W, y + IMAGE_H + LABEL_H), fill=(3, 7, 18))
        draw.text((x + 12, y + IMAGE_H + 12), path.name, font=font, fill=(248, 250, 252))

    canvas.save(OUTPUT, "JPEG", quality=90, optimize=True, progressive=True)
    print(f"Lagde {OUTPUT} med {len(sources)} bilder")


if __name__ == "__main__":
    main()
