from pathlib import Path
import re

ROOT = Path('.')
BASE = 'https://www.fotograf-spalder.com'
INDEXABLE = {
    'index.html': '/',
    'portfolio.html': '/portfolio.html',
    'priser.html': '/priser.html',
    'booking.html': '/booking.html',
    'om.html': '/om.html',
    'kjaeledyrsfotograf-ringsaker.html': '/kjaeledyrsfotograf-ringsaker.html',
    'familie-portrettfotograf-ringsaker.html': '/familie-portrettfotograf-ringsaker.html',
    'bryllupsfotograf-ringsaker.html': '/bryllupsfotograf-ringsaker.html',
    'Konfirmasjon.html': '/Konfirmasjon.html',
    'sommerfotografering.html': '/sommerfotografering.html',
    'personvern.html': '/personvern.html',
}


def local_image_refs():
    refs = set()
    patterns = [
        re.compile(r'(?:src|href)=["\']([^"\']+\.(?:jpe?g|png|webp))(?:\?[^"\']*)?["\']', re.I),
        re.compile(r'url\(["\']?([^"\')]+\.(?:jpe?g|png|webp))(?:\?[^"\')]+)?["\']?\)', re.I),
    ]
    for html in ROOT.glob('*.html'):
        text = html.read_text(encoding='utf-8')
        for pattern in patterns:
            for ref in pattern.findall(text):
                if not ref.startswith(('http://', 'https://', 'data:')):
                    refs.add(ROOT / ref.lstrip('/'))
    return refs


def main():
    errors = []
    sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')

    for filename, path in INDEXABLE.items():
        file = ROOT / filename
        if not file.exists():
            errors.append(f'Mangler side: {filename}')
            continue
        text = file.read_text(encoding='utf-8')
        canonical = BASE + path
        checks = {
            'title': '<title>' in text and '</title>' in text,
            'description': '<meta name="description" content=' in text,
            'robots': '<meta name="robots" content="index, follow">' in text,
            'canonical': f'<link rel="canonical" href="{canonical}">' in text,
            'og:url': f'<meta property="og:url" content="{canonical}">' in text,
        }
        for name, ok in checks.items():
            if not ok:
                errors.append(f'{filename}: mangler/feil {name}')
        if canonical not in sitemap:
            errors.append(f'{filename}: mangler i sitemap')

    thanks = (ROOT / 'takk.html').read_text(encoding='utf-8')
    if '<meta name="robots" content="noindex, nofollow">' not in thanks:
        errors.append('takk.html må være noindex, nofollow')
    if BASE + '/takk.html' in sitemap:
        errors.append('takk.html skal ikke være i sitemap')

    robots = (ROOT / 'robots.txt').read_text(encoding='utf-8')
    if f'Sitemap: {BASE}/sitemap.xml' not in robots:
        errors.append('robots.txt mangler sitemap')

    for html in ROOT.glob('*.html'):
        text = html.read_text(encoding='utf-8')
        if 'www.googletagmanager.com/gtag/js' in text:
            errors.append(f'{html}: Google Analytics lastes direkte før samtykke')

    for ref in local_image_refs():
        if not ref.exists():
            errors.append(f'Manglende bildefil: {ref}')
        elif ref.suffix.lower() in {'.jpg', '.jpeg'} and ref.stat().st_size > 1_800_000:
            errors.append(f'For stor aktiv JPEG: {ref} ({ref.stat().st_size/1024/1024:.1f} MB)')

    if (ROOT / '.github/workflows/august-update.yml').exists():
        errors.append('Utdatert august-update.yml finnes fortsatt')

    if errors:
        raise SystemExit('\n'.join(errors))
    print('Teknisk kvalitetskontroll bestått.')


if __name__ == '__main__':
    main()
