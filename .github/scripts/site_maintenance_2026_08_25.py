from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError
import re
import os

ROOT = Path('.')
TODAY = '2026-08-25'
BASE = 'https://www.fotograf-spalder.com'

INDEXABLE = {
    'index.html': ('/', 'Profesjonell fotograf i Ringsaker og Brumunddal. Spesialisert på kjæledyr, familie og portrett. Se bilder, priser og book fotografering hos Fotograf Spalder.'),
    'portfolio.html': ('/portfolio.html', 'Se porteføljen til Fotograf Spalder med kjæledyr, familie, portrett, bryllup, konfirmasjon og naturbilder fra Ringsaker og Innlandet.'),
    'priser.html': ('/priser.html', 'Se priser for fotografering og digitale bilder hos Fotograf Spalder i Ringsaker og Brumunddal, med tydelig informasjon om hva som er inkludert.'),
    'booking.html': ('/booking.html', 'Send en enkel bookingforespørsel til Fotograf Spalder for kjæledyr, familie, portrett, bryllup, konfirmasjon og andre fotooppdrag i Innlandet.'),
    'om.html': ('/om.html', 'Bli kjent med Fotograf Spalder i Ringsaker, arbeidsmåten, bakgrunnen og fotografier som er publisert i lokale medier.'),
    'kjaeledyrsfotograf-ringsaker.html': ('/kjaeledyrsfotograf-ringsaker.html', 'Kjæledyrsfotograf i Ringsaker og Brumunddal for hund, katt og andre dyr. Se priser, eksempler og hvordan fotograferingen foregår.'),
    'familie-portrettfotograf-ringsaker.html': ('/familie-portrettfotograf-ringsaker.html', 'Familie- og portrettfotograf i Ringsaker, Brumunddal og Innlandet. Se pakker, bildepriser, portefølje og send en bookingforespørsel.'),
    'bryllupsfotograf-ringsaker.html': ('/bryllupsfotograf-ringsaker.html', 'Bryllupsfotograf i Ringsaker, Brumunddal, Hamar og Innlandet. Se bryllupsbilder, priser, betalingsløp og hvordan dekningen kan tilpasses.'),
    'Konfirmasjon.html': ('/Konfirmasjon.html', 'Konfirmasjonsfotograf i Ringsaker, Brumunddal og Mjøsområdet. Portretter, familiebilder og stemningsbilder med tydelige priser og privat galleri.'),
    'sommerfotografering.html': ('/sommerfotografering.html', 'Sesongfotografering i Ringsaker og ved Mjøsa med naturlige portretter, familie-, kjæledyr- og naturbilder hos Fotograf Spalder.'),
    'personvern.html': ('/personvern.html', 'Les hvordan Fotograf Spalder behandler personopplysninger, bookingdata, informasjonskapsler og samtykke til analyse på nettstedet.'),
}

NOINDEX = {'takk.html'}


def upsert_named_meta(text: str, name: str, content: str) -> str:
    pattern = re.compile(rf'<meta\s+name=["\']{re.escape(name)}["\'][^>]*>', re.I)
    tag = f'<meta name="{name}" content="{content}">' 
    if pattern.search(text):
        return pattern.sub(tag, text, count=1)
    marker = re.search(r'<meta\s+name=["\']viewport["\'][^>]*>', text, re.I)
    if marker:
        return text[:marker.end()] + '\n  ' + tag + text[marker.end():]
    return text.replace('<head>', '<head>\n  ' + tag, 1)


def upsert_property_meta(text: str, prop: str, content: str) -> str:
    pattern = re.compile(rf'<meta\s+property=["\']{re.escape(prop)}["\'][^>]*>', re.I)
    tag = f'<meta property="{prop}" content="{content}">' 
    if pattern.search(text):
        return pattern.sub(tag, text, count=1)
    marker = re.search(r'<meta\s+property=["\']og:type["\'][^>]*>', text, re.I)
    if marker:
        return text[:marker.end()] + '\n  ' + tag + text[marker.end():]
    return text.replace('</title>', '</title>\n  ' + tag, 1)


def upsert_canonical(text: str, url: str) -> str:
    pattern = re.compile(r'<link\s+rel=["\']canonical["\'][^>]*>', re.I)
    tag = f'<link rel="canonical" href="{url}">' 
    if pattern.search(text):
        return pattern.sub(tag, text, count=1)
    return text.replace('</title>', '</title>\n  ' + tag, 1)


def normalize_seo() -> set[str]:
    changed: set[str] = set()
    for filename, (path, description) in INDEXABLE.items():
        file = ROOT / filename
        if not file.exists():
            raise SystemExit(f'Mangler SEO-side: {filename}')
        text = file.read_text(encoding='utf-8')
        original = text
        canonical = BASE + path
        text = upsert_named_meta(text, 'description', description)
        text = upsert_named_meta(text, 'robots', 'index, follow')
        text = upsert_canonical(text, canonical)
        text = upsert_property_meta(text, 'og:url', canonical)
        text = upsert_property_meta(text, 'og:type', 'website')
        if '<html lang="no"' not in text and "<html lang='no'" not in text:
            text = re.sub(r'<html(?:\s[^>]*)?>', '<html lang="no">', text, count=1, flags=re.I)
        if text != original:
            file.write_text(text, encoding='utf-8')
            changed.add(filename)

    for filename in NOINDEX:
        file = ROOT / filename
        if not file.exists():
            continue
        text = file.read_text(encoding='utf-8')
        original = text
        text = upsert_named_meta(text, 'robots', 'noindex, nofollow')
        if text != original:
            file.write_text(text, encoding='utf-8')
            changed.add(filename)

    sitemap_path = ROOT / 'sitemap.xml'
    sitemap = sitemap_path.read_text(encoding='utf-8')
    original_sitemap = sitemap
    for filename, (path, _description) in INDEXABLE.items():
        loc = BASE + path
        if loc not in sitemap:
            block = f'\n  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
            sitemap = sitemap.replace('</urlset>', block + '\n</urlset>')
        pattern = re.compile(rf'(<loc>{re.escape(loc)}</loc>\s*<lastmod>)[^<]+(</lastmod>)')
        sitemap = pattern.sub(rf'\g<1>{TODAY}\g<2>', sitemap, count=1)
    sitemap = re.sub(r'\s*<url>\s*<loc>https://www\.fotograf-spalder\.com/takk\.html</loc>.*?</url>', '', sitemap, flags=re.S)
    if sitemap != original_sitemap:
        sitemap_path.write_text(sitemap, encoding='utf-8')
        changed.add('sitemap.xml')
    return changed


def optimize_jpeg(path: Path) -> tuple[int, int] | None:
    before = path.stat().st_size
    if before <= 1_200_000:
        return None
    try:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source)
            icc = source.info.get('icc_profile')
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            if max(image.size) > 2400:
                image.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
            tmp = path.with_name(path.name + '.optimizing')
            quality_used = None
            for quality in (86, 82, 78):
                save_args = dict(format='JPEG', quality=quality, optimize=True, progressive=True, subsampling=1)
                if icc:
                    save_args['icc_profile'] = icc
                image.save(tmp, **save_args)
                quality_used = quality
                if tmp.stat().st_size <= 1_200_000:
                    break
            after = tmp.stat().st_size
            if after < before * 0.95:
                os.replace(tmp, path)
                print(f'Optimalisert {path}: {before/1024/1024:.1f} MB -> {after/1024/1024:.2f} MB (q={quality_used})')
                return before, after
            tmp.unlink(missing_ok=True)
    except (UnidentifiedImageError, OSError) as exc:
        print(f'Hopper over {path}: {exc}')
    return None


def optimize_images() -> tuple[int, int, int]:
    count = 0
    before_total = 0
    after_total = 0
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in {'.jpg', '.jpeg'}:
            continue
        if '.git' in path.parts or '.github' in path.parts:
            continue
        result = optimize_jpeg(path)
        if result:
            before, after = result
            count += 1
            before_total += before
            after_total += after
    return count, before_total, after_total


def local_image_references() -> set[Path]:
    refs: set[Path] = set()
    patterns = [
        re.compile(r'(?:src|href)=["\']([^"\']+\.(?:jpe?g|png|webp))(?:\?[^"\']*)?["\']', re.I),
        re.compile(r'url\(["\']?([^"\')]+\.(?:jpe?g|png|webp))(?:\?[^"\')]+)?["\']?\)', re.I),
    ]
    for html in ROOT.glob('*.html'):
        text = html.read_text(encoding='utf-8')
        for pattern in patterns:
            for match in pattern.findall(text):
                if match.startswith(('http://', 'https://', 'data:')):
                    continue
                refs.add(ROOT / match.lstrip('/'))
    return refs


def validate() -> None:
    for filename, (path, _description) in INDEXABLE.items():
        text = (ROOT / filename).read_text(encoding='utf-8')
        canonical = BASE + path
        required = [
            f'<link rel="canonical" href="{canonical}">',
            f'<meta property="og:url" content="{canonical}">',
            '<meta name="robots" content="index, follow">',
            '<meta name="description" content=',
            '<title>',
        ]
        missing = [token for token in required if token not in text]
        if missing:
            raise SystemExit(f'{filename}: mangler SEO-elementer: {missing}')

    thanks = (ROOT / 'takk.html').read_text(encoding='utf-8')
    if '<meta name="robots" content="noindex, nofollow">' not in thanks:
        raise SystemExit('takk.html skal være noindex, nofollow')

    if (ROOT / '.github/workflows/august-update.yml').exists():
        raise SystemExit('Utdatert august-workflow finnes fortsatt')

    sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
    if BASE + '/takk.html' in sitemap:
        raise SystemExit('takk.html skal ikke ligge i sitemap')
    for _filename, (path, _description) in INDEXABLE.items():
        if BASE + path not in sitemap:
            raise SystemExit(f'Mangler i sitemap: {BASE + path}')

    oversized = []
    for ref in local_image_references():
        if not ref.exists():
            raise SystemExit(f'HTML peker til manglende bilde: {ref}')
        if ref.suffix.lower() in {'.jpg', '.jpeg'} and ref.stat().st_size > 1_800_000:
            oversized.append((str(ref), ref.stat().st_size))
    if oversized:
        details = ', '.join(f'{p} ({s/1024/1024:.1f} MB)' for p, s in oversized)
        raise SystemExit('Fortsatt for store JPEG-er i aktiv nettside: ' + details)

    for html in ROOT.glob('*.html'):
        text = html.read_text(encoding='utf-8')
        if 'www.googletagmanager.com/gtag/js' in text:
            raise SystemExit(f'{html}: laster Google Analytics direkte før samtykke')


def retire_obsolete_automation() -> None:
    obsolete = [
        '.github/workflows/august-update.yml',
        '.github/workflows/privacy-consent.yml',
        '.github/scripts/august_update.py',
        '.github/scripts/kitten_portfolio_update.py',
        '.github/scripts/mobile_layout_fix.py',
        '.github/scripts/payment_flow_update.py',
        '.github/scripts/privacy_consent_update.py',
    ]
    for item in obsolete:
        path = ROOT / item
        if path.exists():
            path.unlink()
            print(f'Fjernet utdatert engangsautomatisering: {item}')


def main() -> None:
    retire_obsolete_automation()
    changed = normalize_seo()
    count, before, after = optimize_images()
    validate()
    print(f'SEO-filer oppdatert: {len(changed)}')
    if count:
        print(f'JPEG-er optimalisert: {count}; {before/1024/1024:.1f} MB -> {after/1024/1024:.1f} MB')
    else:
        print('Ingen JPEG-er trengte ny optimalisering.')


if __name__ == '__main__':
    main()
