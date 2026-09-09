"""Reject hardcoded commercial numbers in authoring templates, not generated HTML."""
from pathlib import Path
import re

from build_site import ROOT, TOKEN, build, load_data


def check(root=ROOT):
    errors = []
    for path in sorted((root / 'templates/pages').glob('*.tmpl')):
        source = path.read_text(encoding='utf-8')
        source = re.sub(r'<style\b[^>]*>.*?</style>', '', source, flags=re.S | re.I)
        # Keep JSON-LD in scope, omit executable code with unrelated numeric constants.
        source = re.sub(r'<script(?![^>]*application/ld\+json)[^>]*>.*?</script>', '', source, flags=re.S | re.I)
        source = TOKEN.sub('DATA', source)
        patterns = {
            'literal price': r'\b\d[\d \u00a0]*(?:[–-]\d[\d ]*)?\s*kr\b',
            'literal payment percentage': r'\b(?:30|70)\s*%',
            'literal included images': r'\b\d+\s+(?:digitale?\s+|digitalt\s+)?bilder?\s+(?:inkludert|i høy kvalitet)',
            'literal delivery range': r'\b\d+[–-]\d+\s+uker',
            'literal JSON-LD price': r'"(?:price|lowPrice|highPrice)"\s*:\s*"?\d',
        }
        for label, pattern in patterns.items():
            for match in re.finditer(pattern, source, re.I):
                errors.append(f'{path.name}: {label}: {match[0]}')
    # Also verifies all references exist, schema is valid and output is current.
    stale, _ = build(root, check=True)
    errors.extend('Stale generated page: ' + name for name in stale)
    return errors


if __name__ == '__main__':
    errors = check()
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Commercial source and generated HTML verified; no literal prices in templates.')
