"""Compare Astro dist with the checked-in Phase 3a HTML authority."""
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.github/scripts'))
from site_audit import audit  # noqa: E402

PAGE_FIELDS = (
    'title', 'metadata', 'canonical', 'json_ld', 'booking_options',
    'forms', 'scripts', 'nav', 'footer', 'css_variables', 'media_queries',
    'css_rules', 'style_bytes', 'inline_scripts', 'patches',
)


def signature(reference):
    return tuple(reference[key] for key in ('page', 'kind', 'ref', 'target', 'fragment'))


def compare(root=ROOT, output=None):
    output = output or root / 'dist'
    errors = []
    with tempfile.TemporaryDirectory() as directory:
        authority = Path(directory)
        for source in root.glob('*.html'):
            shutil.copyfile(source, authority / source.name)
        for name in ('CNAME', 'robots.txt', 'sitemap.xml'):
            shutil.copyfile(root / 'public' / name, authority / name)
        expected = audit(authority)
    actual = audit(output)
    if set(expected['pages']) != set(actual['pages']):
        errors.append('Route inventory differs: ' + repr(sorted(set(expected['pages']) ^ set(actual['pages']))))
    for name in sorted(set(expected['pages']) & set(actual['pages'])):
        for field in PAGE_FIELDS:
            if expected['pages'][name][field] != actual['pages'][name][field]:
                errors.append(f'{name}: {field} differs')
        expected_commercial = [entry['text'] for entry in expected['pages'][name]['commercial']]
        actual_commercial = [entry['text'] for entry in actual['pages'][name]['commercial']]
        if expected_commercial != actual_commercial:
            errors.append(f'{name}: commercial copy differs')
        expected_images = [{key: value for key, value in image.items() if key != 'line'} for image in expected['pages'][name]['images']]
        actual_images = [{key: value for key, value in image.items() if key != 'line'} for image in actual['pages'][name]['images']]
        if expected_images != actual_images:
            errors.append(f'{name}: included images differ')
    if sorted(map(signature, expected['references'])) != sorted(map(signature, actual['references'])):
        errors.append('Local asset references differ')
    for name in ('CNAME', 'robots.txt', 'sitemap.xml'):
        expected_text = (root / 'public' / name).read_text(encoding='utf-8')
        actual_text = (output / name).read_text(encoding='utf-8')
        if expected_text != actual_text:
            errors.append(name + ' differs')
    return errors


if __name__ == '__main__':
    failures = compare()
    if failures:
        raise SystemExit('\n'.join(failures))
    print('Astro dist is semantically identical to the Phase 3a authority across 12 routes.')
