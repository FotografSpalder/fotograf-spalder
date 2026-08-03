from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path.cwd()
DATE = "2026-08-04"
SOURCE_NAMES = [
    "IMG_0362.jpg", "IMG_0379.jpg", "IMG_0457.jpg", "IMG_0556.jpg",
    "IMG_0616.jpg", "IMG_0629.jpg", "IMG_0664.jpg", "IMG_0678.jpg",
    "IMG_0684.jpg", "IMG_0688.jpg", "IMG_0703.jpg", "IMG_0720.jpg",
    "IMG_0728.jpg", "IMG_0737.jpg", "IMG_0748.jpg", "IMG_0764.jpg",
    "IMG_0782.jpg", "IMG_0842.jpg", "IMG_0858.jpg", "IMG_0906.jpg",
    "IMG_0945.jpg", "IMG_0958.jpg", "IMG_1006.jpg", "IMG_1118.jpg",
    "IMG_1157.jpg", "IMG_1165.jpg", "IMG_1246.jpg", "IMG_1265.jpg",
]
N_SELECT = 12
OUT_DIR = ROOT / "images" / "portfolio" / "natur"
SHARE_DIR = ROOT / "images" / "deling"


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write_text(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8", newline="\n")


def replace_required(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Fant ikke forventet tekst for {label}: {old[:100]!r}")
    return text.replace(old, new, 1)


def add_css_once(text: str, css: str, marker: str) -> str:
    if marker in text:
        return text
    if "</style>" not in text:
        raise RuntimeError("Fant ikke </style> i HTML-filen")
    return text.replace("</style>", f"\n{marker}\n{css}\n</style>", 1)


def normalized_image(path: Path) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.exif_transpose(source).convert("RGB")


def ahash(image: Image.Image, size: int = 16) -> np.ndarray:
    small = image.convert("L").resize((size, size), Image.Resampling.LANCZOS)
    arr = np.asarray(small, dtype=np.float32)
    return arr > arr.mean()


def metrics(path: Path) -> dict:
    image = normalized_image(path)
    width, height = image.size
    sample = image.copy()
    sample.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
    gray_img = sample.convert("L")
    gray = np.asarray(gray_img, dtype=np.float32)
    edges = np.asarray(gray_img.filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    sharpness = float(edges.var())
    entropy = float(gray_img.entropy())
    mean = float(gray.mean())
    exposure = max(0.0, 1.0 - abs(mean - 128.0) / 128.0)
    clipping = float((gray < 5).mean() + (gray > 250).mean())
    megapixels = (width * height) / 1_000_000
    resolution_bonus = min(math.log1p(megapixels), 3.0)
    score = math.log1p(sharpness) * 2.8 + entropy * 1.8 + exposure * 3.0 + resolution_bonus - clipping * 14.0
    return {
        "source": path.name,
        "width": width,
        "height": height,
        "score": round(score, 4),
        "sharpness": round(sharpness, 4),
        "entropy": round(entropy, 4),
        "mean_luminance": round(mean, 4),
        "clipping": round(clipping, 6),
        "hash": ahash(sample),
    }


def select_diverse(items: list[dict], limit: int) -> list[dict]:
    ordered = sorted(items, key=lambda item: item["score"], reverse=True)
    selected: list[dict] = []
    for threshold in (42, 34, 26, 18, 0):
        for item in ordered:
            if item in selected:
                continue
            if not selected or all(np.count_nonzero(item["hash"] != other["hash"]) >= threshold for other in selected):
                selected.append(item)
                if len(selected) == limit:
                    return selected
    return selected[:limit]


def resize_for_web(image: Image.Image, max_side: int = 1800) -> Image.Image:
    result = image.copy()
    result.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return result


def save_variants(item: dict, rank: int) -> dict:
    image = resize_for_web(normalized_image(ROOT / item["source"]))
    stem = f"natur-og-dyreliv-ringsaker-{rank:02d}"
    webp_path = OUT_DIR / f"{stem}.webp"
    jpg_path = OUT_DIR / f"{stem}.jpg"
    image.save(webp_path, "WEBP", quality=82, method=6)
    image.save(jpg_path, "JPEG", quality=86, optimize=True, progressive=True, subsampling="4:2:0")
    return {
        "rank": rank,
        "source": item["source"],
        "webp": webp_path.relative_to(ROOT).as_posix(),
        "jpg": jpg_path.relative_to(ROOT).as_posix(),
        "width": image.width,
        "height": image.height,
        "score": item["score"],
    }


def make_share_image(source: Path, destination: Path) -> None:
    image = normalized_image(source)
    image = ImageOps.fit(image, (1200, 630), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    image.save(destination, "JPEG", quality=87, optimize=True, progressive=True)


def make_collage(selected: list[dict], destination: Path) -> None:
    canvas = Image.new("RGB", (1200, 630), (15, 23, 42))
    cells = [(0, 0, 600, 315), (600, 0, 1200, 315), (0, 315, 600, 630), (600, 315, 1200, 630)]
    for item, box in zip(selected[:4], cells):
        image = normalized_image(ROOT / item["source"])
        tile = ImageOps.fit(image, (box[2] - box[0], box[3] - box[1]), method=Image.Resampling.LANCZOS)
        canvas.paste(tile, box[:2])
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, 532, 1200, 630), fill=(11, 17, 32, 190))
    draw.text((38, 558), "Fotograf Spalder – portefølje", fill=(248, 250, 252, 255))
    canvas.save(destination, "JPEG", quality=87, optimize=True, progressive=True)


def picture_markup(entry: dict, alt: str, eager: bool = False) -> str:
    loading = "eager" if eager else "lazy"
    priority = ' fetchpriority="high"' if eager else ""
    return (
        '<div class="gallery-item"><picture>'
        f'<source srcset="{entry["webp"]}" type="image/webp">'
        f'<img src="{entry["jpg"]}" loading="{loading}" decoding="async"{priority} '
        f'width="{entry["width"]}" height="{entry["height"]}" alt="{alt}">'
        '</picture></div>'
    )


def update_portfolio(entries: list[dict]) -> None:
    path = "portfolio.html"
    text = read_text(path)
    text = text.replace('content="https://www.fotograf-spalder.com/hund2.jpg"', 'content="https://www.fotograf-spalder.com/images/deling/portfolio-fotograf-ringsaker.jpg"', 1)
    text = text.replace("Se bilder fra kjæledyrfoto, familie, portrett, bryllup og cosplay i Ringsaker og Innlandet.", "Se bilder fra kjæledyr, familie, portrett, bryllup, cosplay, natur og dyreliv i Ringsaker og Innlandet.", 1)
    text = text.replace("Kjæledyr, familie, portrett, bryllup og cosplayfoto fra Ringsaker, Brumunddal og Innlandet.", "Kjæledyr, familie, portrett, bryllup, cosplay, natur og dyreliv fra Ringsaker, Brumunddal og Innlandet.", 1)
    text = add_css_once(text, ".gallery picture { display: block; width: 100%; }\n.gallery img { aspect-ratio: auto; }", "/* AUGUST_GALLERY_MEDIA */")
    if "onclick=\"showTab(event, 'natur')\"" not in text:
        text = replace_required(text, '    <div class="tab" onclick="showTab(event, \'cosplay\')">Cosplay</div>', '    <div class="tab" onclick="showTab(event, \'cosplay\')">Cosplay</div>\n    <div class="tab" onclick="showTab(event, \'natur\')">Natur og dyreliv</div>', "naturfane i porteføljen")
    gallery = "\n".join(picture_markup(entry, f"Natur- og dyreliv fotografert i Ringsaker av Fotograf Spalder, bilde {entry['rank']}") for entry in entries)
    section = f'''\n  <!-- AUGUST_NATURE_START -->
  <div id="natur" class="section">
    <div class="gallery">
      {gallery}
    </div>
  </div>
  <!-- AUGUST_NATURE_END -->\n'''
    if "<!-- AUGUST_NATURE_START -->" in text:
        text = re.sub(r"\n\s*<!-- AUGUST_NATURE_START -->.*?<!-- AUGUST_NATURE_END -->\s*\n", section, text, flags=re.S)
    else:
        text = replace_required(text, '  <div style="text-align:center; margin-top:2rem;">', section + '\n  <div style="text-align:center; margin-top:2rem;">', "naturseksjon i porteføljen")
    write_text(path, text)


def update_index(entries: list[dict]) -> None:
    path = "index.html"
    text = read_text(path)
    text = text.replace('content="https://www.fotograf-spalder.com/header.jpg"', 'content="https://www.fotograf-spalder.com/images/deling/portfolio-fotograf-ringsaker.jpg"', 1)
    text = text.replace("Aktuelt denne sommeren", "Aktuelt i august", 1)
    text = text.replace("Sommerfotografering i Ringsaker</h2>", "Sensommerfotografering i Ringsaker</h2>", 1)
    text = text.replace("Sommeren gir grønt landskap, varme kvelder og naturlige omgivelser som passer godt til familie-, portrett- og kjæledyrsfotografering. Se forslag til fotografering, steder og praktisk informasjon.", "August gir modent grønt, åkre, roligere kvelder og et mykere sensommerlys. Det passer svært godt til familie-, portrett- og kjæledyrsfotografering – og nå kan du også sikre deg tid før høstfargene kommer.", 1)
    text = text.replace("Se sommerfotografering", "Se sensommerfotografering", 1)
    text = text.replace("<strong>Sommerfoto</strong>", "<strong>Sensommerfoto</strong>", 1)
    text = text.replace("Sommerfotografering for familie, portrett og kjæledyr", "Sensommerfotografering for familie, portrett og kjæledyr", 1)
    text = text.replace('"price": "1500-4000"', '"price": "1800-4000"', 1)
    text = text.replace('"price": "1200-1800"', '"price": "1500-2500"', 1)
    text = text.replace('"price": "6000+"', '"price": "10000+"', 1)
    text = add_css_once(text, ".gallery picture { display: block; width: 100%; height: 100%; }\n.gallery picture img { width: 100%; height: 100%; object-fit: cover; }", "/* AUGUST_GALLERY_MEDIA */")
    items = [
        '<div class="gallery-item"><img src="hund2.jpg" loading="lazy" decoding="async" alt="Hund fotografert utendørs i Ringsaker av Fotograf Spalder"></div>',
        '<div class="gallery-item"><img src="konfirmant.jpg" loading="lazy" decoding="async" alt="Konfirmasjonsfoto i Ringsaker av Fotograf Spalder"></div>',
        '<div class="gallery-item"><img src="familie1.jpg" loading="lazy" decoding="async" alt="Familiefoto i Ringsaker av Fotograf Spalder"></div>',
        '<div class="gallery-item"><img src="bryllup.jpg" loading="lazy" decoding="async" alt="Bryllupsfotografering i Ringsaker av Fotograf Spalder"></div>',
        picture_markup(entries[0], "Natur- og dyreliv fotografert i Ringsaker av Fotograf Spalder"),
        picture_markup(entries[1], "Dyrefotografi fra Innlandet av Fotograf Spalder"),
    ]
    new_gallery = "\n          ".join(items)
    pattern = re.compile(r'(<section id="galleri">.*?<div class="section-head">.*?<h2>Galleri</h2>\s*<p class="lead">)(.*?)(</p>\s*</div>\s*<div class="gallery">)(.*?)(</div>\s*</div>\s*</section>)', re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("Fant ikke galleriseksjonen på forsiden")
    text = pattern.sub(lambda m: m.group(1) + "Et oppdatert utvalg av kjæledyr, mennesker, bryllup, natur og dyreliv." + m.group(3) + "\n          " + new_gallery + "\n        " + m.group(5), text, count=1)
    write_text(path, text)


def update_summer_page() -> None:
    path = "sommerfotografering.html"
    text = read_text(path)
    replacements = [
        ("<title>Sommerfotografering i Ringsaker og Brumunddal | Fotograf Spalder</title>", "<title>Sensommerfotografering i Ringsaker og Brumunddal | Fotograf Spalder</title>"),
        ('content="Book sommerfotografering i Ringsaker og Brumunddal. Naturlige bilder av kjæledyr, familie, par og portrett i sommerlys hos Fotograf Spalder."', 'content="Book sensommerfotografering i Ringsaker og Brumunddal. Naturlige bilder av kjæledyr, familie, par og portrett i det myke augustlyset."'),
        ('content="Sommerfotografering i Ringsaker og Brumunddal | Fotograf Spalder"', 'content="Sensommerfotografering i Ringsaker og Brumunddal | Fotograf Spalder"'),
        ('content="Naturlige sommerbilder av kjæledyr, familie, par og portrett i Ringsaker og Innlandet."', 'content="Naturlige sensommerbilder av kjæledyr, familie, par og portrett i Ringsaker og Innlandet."'),
        ('content="https://www.fotograf-spalder.com/header.jpg"', 'content="https://www.fotograf-spalder.com/images/deling/sensommerfotografering-ringsaker.jpg"'),
        ("url('header.jpg') center/cover", "url('images/deling/sensommerfotografering-ringsaker.jpg') center/cover"),
        ('content:"Sommerfotografering i Innlandet"', 'content:"Sensommerfotografering i Innlandet"'),
        ("Sommerfotografering i Ringsaker og Brumunddal</div>", "Sensommerfotografering i Ringsaker og Brumunddal</div>"),
        ("Naturlige sommerbilder som varer lenger enn sesongen", "Naturlige sensommerbilder i det myke augustlyset"),
        ("Sommeren gir mykt lys, grønne omgivelser og god tid til å skape naturlige bilder av kjæledyr, familier, par og enkeltpersoner. Jeg tar oppdrag i Ringsaker, Brumunddal, Moelv, Hamar og resten av Innlandet.", "August gir mykere kveldslys, modne grøntoner og mer ro i landskapet. Det passer godt til naturlige bilder av kjæledyr, familier, par og enkeltpersoner i Ringsaker, Brumunddal, Moelv, Hamar og resten av Innlandet."),
        ("Book sommerfotografering", "Book sensommerfotografering"),
        ("Praktisk før sommerfotograferingen", "Praktisk før sensommerfotograferingen"),
        ("Book sommerfotografering i Innlandet", "Book sensommerfotografering i Innlandet"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    august_section = '''
  <!-- AUGUST_SEASON_START -->
  <section>
    <div class="container">
      <div class="info-box">
        <h2>August nå – høstfarger snart</h2>
        <p>De første ukene i august gir fortsatt sommerlige omgivelser, mens kveldene gradvis blir mørkere og lyset mykere. Mot slutten av måneden begynner overgangen til høst. Det gjør august egnet både for sensommerbilder og for å reservere fotografering når høstfargene kommer.</p>
      </div>
    </div>
  </section>
  <!-- AUGUST_SEASON_END -->
'''
    if "<!-- AUGUST_SEASON_START -->" not in text:
        text = replace_required(text, "\n  <section>\n    <div class=\"container\">\n      <div class=\"cta\">", august_section + "\n  <section>\n    <div class=\"container\">\n      <div class=\"cta\">", "augustseksjon på sensommersiden")
    write_text(path, text)


def update_pet_page() -> None:
    path = "kjaeledyrsfotograf-ringsaker.html"
    text = read_text(path)
    text = text.replace("https://www.fotograf-spalder.com/Untitled-1.png", "https://www.fotograf-spalder.com/images/deling/kjaeledyrsfotograf-ringsaker.jpg")
    text = re.sub(r'<img src="([^"]+)" alt=', r'<img src="\1" loading="lazy" decoding="async" alt=', text)
    write_text(path, text)


def update_sitemap() -> None:
    urls = [
        ("https://www.fotograf-spalder.com/", "1.0", "weekly"),
        ("https://www.fotograf-spalder.com/portfolio.html", "0.9", "monthly"),
        ("https://www.fotograf-spalder.com/priser.html", "0.9", "monthly"),
        ("https://www.fotograf-spalder.com/booking.html", "1.0", "monthly"),
        ("https://www.fotograf-spalder.com/Konfirmasjon.html", "0.9", "monthly"),
        ("https://www.fotograf-spalder.com/kjaeledyrsfotograf-ringsaker.html", "1.0", "monthly"),
        ("https://www.fotograf-spalder.com/sommerfotografering.html", "0.9", "weekly"),
        ("https://www.fotograf-spalder.com/om.html", "0.7", "yearly"),
    ]
    blocks = []
    for loc, priority, freq in urls:
        blocks.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{DATE}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n  </url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n' + "\n\n".join(blocks) + "\n\n</urlset>\n"
    write_text("sitemap.xml", xml)


def main() -> None:
    sources = [ROOT / name for name in SOURCE_NAMES if (ROOT / name).exists()]
    if len(sources) != len(SOURCE_NAMES):
        missing = sorted(set(SOURCE_NAMES) - {path.name for path in sources})
        raise RuntimeError(f"Mangler forventede bildefiler: {missing}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SHARE_DIR.mkdir(parents=True, exist_ok=True)
    all_metrics = [metrics(path) for path in sources]
    selected = select_diverse(all_metrics, N_SELECT)
    if len(selected) < N_SELECT:
        raise RuntimeError(f"Klarte bare å velge {len(selected)} bilder")
    entries = [save_variants(item, rank) for rank, item in enumerate(selected, 1)]
    public_metrics = []
    for item in sorted(all_metrics, key=lambda value: value["score"], reverse=True):
        copy = {key: value for key, value in item.items() if key != "hash"}
        copy["selected"] = any(entry["source"] == copy["source"] for entry in entries)
        public_metrics.append(copy)
    (OUT_DIR / "gallery.json").write_text(json.dumps({"generated": DATE, "selected": entries, "all_images": public_metrics}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    make_share_image(ROOT / selected[0]["source"], SHARE_DIR / "sensommerfotografering-ringsaker.jpg")
    make_collage(selected, SHARE_DIR / "portfolio-fotograf-ringsaker.jpg")
    dog_source = ROOT / "IMG_8950.1.jpg"
    if not dog_source.exists():
        dog_source = ROOT / "hund2.jpg"
    make_share_image(dog_source, SHARE_DIR / "kjaeledyrsfotograf-ringsaker.jpg")
    contact = Image.new("RGB", (1200, 900), (15, 23, 42))
    draw = ImageDraw.Draw(contact)
    for index, item in enumerate(selected):
        row, col = divmod(index, 4)
        image = normalized_image(ROOT / item["source"])
        tile = ImageOps.fit(image, (280, 240), method=Image.Resampling.LANCZOS)
        x, y = 10 + col * 295, 10 + row * 295
        contact.paste(tile, (x, y))
        draw.rectangle((x, y + 240, x + 280, y + 278), fill=(11, 17, 32))
        draw.text((x + 8, y + 250), f"{index + 1:02d} · {item['source']}", fill=(248, 250, 252))
    contact.save(OUT_DIR / "utvalg-kontaktark.jpg", "JPEG", quality=86, optimize=True, progressive=True)
    update_portfolio(entries)
    update_index(entries)
    update_summer_page()
    update_pet_page()
    update_sitemap()
    print("Valgte bilder:")
    for entry in entries:
        print(f"  {entry['rank']:02d}: {entry['source']} -> {entry['webp']}")


if __name__ == "__main__":
    main()
