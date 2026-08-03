from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path.cwd()
OUT_DIR = ROOT / "images" / "portfolio" / "kjaeledyr" / "kattunger"

KITTENS = [
    ("IMG_0664.jpg", "hvit-kattunge-ringsaker-01", "Hvit kattunge fotografert i mykt lys i Ringsaker av Fotograf Spalder"),
    ("IMG_0678.jpg", "hvit-kattunge-ringsaker-02", "Hvit kattunge på mørkt pledd fotografert av Fotograf Spalder"),
    ("IMG_0684.jpg", "gra-kattunge-ringsaker-01", "Grå kattunge fotografert i Ringsaker av Fotograf Spalder"),
    ("IMG_0688.jpg", "brun-kattunge-ringsaker-01", "Brun kattunge fotografert på pledd av Fotograf Spalder"),
    ("IMG_0703.jpg", "hvit-kattunge-ringsaker-03", "Nærbilde av hvit kattunge fotografert av Fotograf Spalder"),
    ("IMG_0720.jpg", "kattungekull-ringsaker-01", "Kattungekull fotografert sammen i Ringsaker av Fotograf Spalder"),
    ("IMG_0728.jpg", "kattungekull-ringsaker-02", "Fem kattunger samlet til kjæledyrfotografering i Ringsaker"),
]

HERO_WEBP = "images/portfolio/natur/natur-og-dyreliv-ringsaker-01.webp"
HERO_JPG = "images/portfolio/natur/natur-og-dyreliv-ringsaker-01.jpg"


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write_text(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8", newline="\n")


def load_image(path: Path) -> Image.Image:
    with Image.open(path) as opened:
        return ImageOps.exif_transpose(opened).convert("RGB")


def save_web_variants(source: str, stem: str) -> dict[str, object]:
    source_path = ROOT / source
    if not source_path.exists():
        raise RuntimeError(f"Mangler kattungebilde: {source}")

    image = load_image(source_path)
    image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    webp_path = OUT_DIR / f"{stem}.webp"
    jpg_path = OUT_DIR / f"{stem}.jpg"

    image.save(webp_path, "WEBP", quality=84, method=6)
    image.save(jpg_path, "JPEG", quality=87, optimize=True, progressive=True, subsampling="4:2:0")

    return {
        "webp": webp_path.relative_to(ROOT).as_posix(),
        "jpg": jpg_path.relative_to(ROOT).as_posix(),
        "width": image.width,
        "height": image.height,
    }


def kitten_markup(entry: dict[str, object], alt: str) -> str:
    return (
        '      <div class="gallery-item kitten-item">\n'
        '        <picture>\n'
        f'          <source srcset="{entry["webp"]}" type="image/webp">\n'
        f'          <img src="{entry["jpg"]}" loading="lazy" decoding="async" '
        f'width="{entry["width"]}" height="{entry["height"]}" alt="{alt}" title="Kattungefotografering i Ringsaker">\n'
        '        </picture>\n'
        '      </div>'
    )


def update_portfolio(entries: list[tuple[dict[str, object], str]]) -> None:
    text = read_text("portfolio.html")

    css = """
/* KITTEN_GALLERY_STYLE_START */
.kitten-item picture {
  display: block;
  width: 100%;
  height: 100%;
}

.kitten-item img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #111827;
}
/* KITTEN_GALLERY_STYLE_END */
"""
    if "/* KITTEN_GALLERY_STYLE_START */" in text:
        text = re.sub(
            r"\n?/\* KITTEN_GALLERY_STYLE_START \*/.*?/\* KITTEN_GALLERY_STYLE_END \*/\n?",
            "\n" + css.strip() + "\n",
            text,
            flags=re.S,
        )
    else:
        text = text.replace("</style>", css + "\n</style>", 1)

    gallery_block = "\n".join(kitten_markup(entry, alt) for entry, alt in entries)
    marked_block = (
        "\n      <!-- KITTEN_GALLERY_START -->\n"
        + gallery_block
        + "\n      <!-- KITTEN_GALLERY_END -->"
    )

    if "<!-- KITTEN_GALLERY_START -->" in text:
        text = re.sub(
            r"\n\s*<!-- KITTEN_GALLERY_START -->.*?<!-- KITTEN_GALLERY_END -->",
            marked_block,
            text,
            flags=re.S,
        )
    else:
        anchor = '''      <div class="gallery-item">
        <img src="IMG_8950.1.jpg" loading="lazy" alt="Stemningsfullt kjæledyrfoto i Innlandet av Fotograf Spalder" title="Kjæledyrfoto Innlandet">
      </div>'''
        if anchor not in text:
            raise RuntimeError("Fant ikke siste eksisterende kjæledyrbilde i porteføljen")
        text = text.replace(anchor, anchor + marked_block, 1)

    write_text("portfolio.html", text)


def update_summer_hero() -> None:
    text = read_text("sommerfotografering.html")

    css = """
/* FULL_HERO_IMAGE_START */
.hero-image {
  min-height: 0;
  background: #111827;
  overflow: hidden;
}

.hero-image picture,
.hero-image img {
  display: block;
  width: 100%;
  height: auto;
}

.hero-image img {
  object-fit: contain;
}
/* FULL_HERO_IMAGE_END */
"""
    if "/* FULL_HERO_IMAGE_START */" in text:
        text = re.sub(
            r"\n?/\* FULL_HERO_IMAGE_START \*/.*?/\* FULL_HERO_IMAGE_END \*/\n?",
            "\n" + css.strip() + "\n",
            text,
            flags=re.S,
        )
    else:
        text = text.replace("</style>", css + "\n</style>", 1)

    old = '<div class="hero-card"><div class="hero-image" role="img" aria-label="Sensommerfotografering i Ringsaker og Innlandet"></div></div>'
    new = (
        '<div class="hero-card"><div class="hero-image">'
        f'<picture><source srcset="{HERO_WEBP}" type="image/webp">'
        f'<img src="{HERO_JPG}" width="1200" height="1800" loading="eager" decoding="async" fetchpriority="high" '
        'alt="Båtliv og landskap ved Mjøsa fotografert i full komposisjon av Fotograf Spalder">'
        '</picture></div></div>'
    )

    if old in text:
        text = text.replace(old, new, 1)
    elif HERO_WEBP not in text:
        raise RuntimeError("Fant ikke hero-feltet på sensommersiden")

    write_text("sommerfotografering.html", text)


def main() -> None:
    entries: list[tuple[dict[str, object], str]] = []
    for source, stem, alt in KITTENS:
        entries.append((save_web_variants(source, stem), alt))

    update_portfolio(entries)
    update_summer_hero()
    print("La inn sju kattungebilder og viste hele sensommerbildet uten beskjæring.")


if __name__ == "__main__":
    main()
