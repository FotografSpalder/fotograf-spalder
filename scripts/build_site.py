"""Render checked-in static HTML from small templates and commercial JSON data.

No dependencies, network access, runtime data fetching or framework required.
Run python scripts/build_site.py; use --check in CI to reject stale HTML.
"""
import argparse
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'\{\{\s*([\w.\-]+)(?:\s*\|\s*(\w+))?\s*\}\}')


def load_data(root=ROOT):
    data = json.loads((root / 'data/services.json').read_text(encoding='utf-8'))
    validate(data)
    return data


def validate(data):
    if data.get('schema_version') != 1 or data.get('currency') != 'NOK':
        raise ValueError('Unsupported schema or currency')
    def integer(value, label, minimum=0):
        if type(value) is not int or value < minimum:
            raise ValueError(f'{label} must be an integer >= {minimum}')
    services = data['services']
    if not services:
        raise ValueError('At least one service is required')
    for key, service in services.items():
        if not service['name'].strip() or service['category'] not in data['categories']:
            raise ValueError('Missing name or unknown category: ' + key)
        integer(service['price'], key + '.price')
        if type(service['from_price']) is not bool:
            raise ValueError(key + '.from_price must be boolean')
        if service.get('max_price') is not None:
            integer(service['max_price'], key + '.max_price', service['price'])
        if service['included_images'] is not None:
            integer(service['included_images'], key + '.included_images')
        if not service['content']:
            raise ValueError('Missing package contents: ' + key)
    rules = data['rules']
    for key in ('deposit_percent', 'balance_percent'):
        integer(rules[key], key)
    if rules['deposit_percent'] + rules['balance_percent'] != 100:
        raise ValueError('Deposit and balance must sum to 100')
    for key in ('delivery_min_weeks', 'delivery_max_weeks', 'cancellation_notice_hours', 'late_minutes'):
        integer(rules[key], key, 1)
    if rules['delivery_max_weeks'] < rules['delivery_min_weeks']:
        raise ValueError('Invalid delivery range')
    for value in data['extras'].values():
        integer(value['price'], 'Extra price')
    for key, field in [('time', 'minutes'), ('travel', 'included_mil'), ('express', 'hours')]:
        integer(data['extras'][key][field], key + '.' + field, 1)
    for key in ('mobile', 'high_resolution', 'full_resolution'):
        integer(data['digital'][key]['price'], key + '.price')
    complete = data['digital']['complete']
    integer(complete['price'], 'complete.price')
    if not complete['scope'] or not complete['separately_quoted']:
        raise ValueError('Complete gallery scope and exclusions are required')
    for group in data['booking_groups']:
        if any(key not in services for key in group['services']):
            raise ValueError('Unknown booking service')
    offered = [key for group in data['booking_groups'] for key in group['services']]
    if len(offered) != len(set(offered)) or set(offered) != set(services):
        raise ValueError('Each service must appear once in booking groups')


def lookup(data, path):
    value = data
    for part in path.split('.'):
        try:
            value = value[int(part)] if isinstance(value, list) else value[part]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError('Unknown data reference: ' + path) from exc
    return value


def grouped(value):
    return f'{value:,}'.replace(',', ' ')


def price(service, group=False, lower=False):
    number = grouped(service['price']) if group or service['price'] >= 10000 else str(service['price'])
    if service.get('max_price') is not None:
        maximum = service['max_price']
        number += '–' + (grouped(maximum) if group or maximum >= 10000 else str(maximum))
    return (('fra ' if lower else 'Fra ') if service['from_price'] else '') + number


def render(source, data, depth=0):
    if depth > 12:
        raise ValueError('Circular template/data reference')
    def substitute(match):
        path, fmt = match.groups()
        value = lookup(data, path)
        if isinstance(value, str) and TOKEN.search(value):
            # Stored content can reuse numeric fields without duplicating their values.
            value = render(html.escape(value, quote=False), data, depth + 1)
            if fmt in (None, 'raw'):
                return value
        if fmt == 'json_string':
            return json.dumps(str(value), ensure_ascii=False).replace('<', '\\u003c')
        if fmt == 'raw':
            if path != 'derived.booking_options':
                raise ValueError('Raw HTML is reserved for generated booking markup')
            return str(value)
        if fmt == 'grouped':
            value = grouped(value)
        elif fmt == 'images':
            value = f'{value} ' + ('digitalt bilde' if value == 1 else 'digitale bilder')
        elif fmt == 'booking_images':
            value = f'{value} ' + ('bilde' if value == 1 else 'bilder')
        elif fmt in ('price', 'price_grouped', 'price_lower', 'price_grouped_lower'):
            value = price(value, 'grouped' in fmt, 'lower' in fmt)
        elif fmt is not None:
            raise ValueError('Unknown filter: ' + fmt)
        if isinstance(value, (dict, list)):
            raise ValueError('Expected scalar token: ' + path)
        return html.escape(str(value), quote=False)
    rendered = TOKEN.sub(substitute, source)
    if '{{' in rendered:
        raise ValueError('Malformed or unresolved template expression')
    return rendered


def context(data):
    # Derived SEO ranges track the same service set already advertised on each page.
    data = json.loads(json.dumps(data))
    s = data['services']
    data['derived'] = {
        'pets_range': f"{min(s[k]['price'] for k in ('pet-mini', 'pet-standard', 'pet-premium'))}-{max(s[k]['price'] for k in ('pet-mini', 'pet-standard', 'pet-premium'))}",
        'portrait_family_range': f"{min(s[k]['price'] for k in ('portrait', 'family'))}-{max(s[k]['price'] for k in ('portrait', 'family'))}",
        'family_low': min(s[k]['price'] for k in ('portrait', 'family', 'basic', 'favorite', 'total')),
        'family_high': max(s[k]['price'] for k in ('portrait', 'family', 'basic', 'favorite', 'total')),
        'wedding_price': str(s['wedding']['price']) + ('+' if s['wedding']['from_price'] else ''),
        'booking_options': booking_options(data),
    }
    return data


def booking_options(data):
    groups = []
    for group in data['booking_groups']:
        lines = ['<optgroup label="' + html.escape(group['label'], quote=True) + '">']
        for key in group['services']:
            service = data['services'][key]
            label = service['name'] + (', ' if service['max_price'] is not None else ' – ') + price(service, lower=True) + ' kr'
            count = service['included_images']
            if count is not None:
                label += f' – {count} ' + ('bilde' if count == 1 else 'bilder') + ' inkludert'
            lines.append('          <option>' + html.escape(label, quote=False) + '</option>')
        lines.append('        </optgroup>')
        groups.append('\n'.join(lines))
    return '\n        '.join(groups)


def build(root=ROOT, check=False, data=None):
    data = load_data(root) if data is None else data
    validate(data)
    data = context(data)
    templates = sorted((root / 'templates/pages').glob('*.html.tmpl'))
    if not templates:
        raise ValueError('No templates found')
    expected = {p.name.removesuffix('.tmpl') for p in templates}
    actual = {p.name for p in root.glob('*.html')}
    if expected != actual:
        raise ValueError('Template/page inventory differs: ' + repr(expected ^ actual))
    stale = []
    rendered = {}
    for template in templates:
        target = root / template.name.removesuffix('.tmpl')
        content = render(template.read_text(encoding='utf-8'), data)
        rendered[target.name] = content
        if TOKEN.search(content):
            raise ValueError('Unresolved token in ' + target.name)
        if target.read_text(encoding='utf-8') != content:
            stale.append(target.name)
    # Render everything before writing anything, so invalid data cannot partially update the site.
    if not check:
        for name in stale:
            (root / name).write_text(rendered[name], encoding='utf-8', newline='\n')
    return stale, rendered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        stale, _ = build(args.root, args.check)
    except (KeyError, ValueError, TypeError) as exc:
        raise SystemExit('Build failed: ' + str(exc)) from exc
    if args.check and stale:
        raise SystemExit('Generated HTML is stale; run python scripts/build_site.py: ' + ', '.join(stale))
    print('Static build verified.' if args.check else f'Static build complete; {len(stale)} page(s) updated.')


if __name__ == '__main__':
    main()
