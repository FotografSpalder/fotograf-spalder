"""Dependency-free, case-sensitive audit of the static site. No network requests."""
import argparse
from collections import Counter, defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import subprocess
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

BASE = 'https://www.fotograf-spalder.com'
ROOT = Path(__file__).resolve().parents[2]
IMAGE = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.svg', '.gif', '.ico'}
COMMERCIAL = re.compile(r'\bkr\b|\bNOK\b|\b(?:30|70)\s*%|forskudd|restbeløp|leveringstid|\b\d+[–-]\d+ uker|avbestill|forsinkelse|dårlig vær|inkludert|komplett digital|tilleggskjøp|reise:', re.I)


class Node:
    def __init__(self, tag='', attrs=(), line=0, parent=None):
        self.tag, self.attrs, self.line, self.parent = tag, dict(attrs), line, parent
        self.children = []

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)

    def normalized(self):
        return ' '.join(self.text().split())

    def inside(self, tag):
        p = self.parent
        while p:
            if p.tag == tag:
                return True
            p = p.parent
        return False


class Page(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack, self.nodes = [self.root], []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.getpos()[0], self.stack[-1])
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def tags(self, tag):
        return [n for n in self.nodes if n.tag == tag]


def local_path(page, ref):
    u = urlsplit(ref.strip())
    if u.scheme and u.scheme not in ('http', 'https'):
        return None
    if u.netloc and u.netloc.lower() not in ('www.fotograf-spalder.com', 'fotograf-spalder.com'):
        return None
    p = unquote(u.path)
    path = posixpath.normpath(p.lstrip('/') if p.startswith('/') else posixpath.join(posixpath.dirname(page), p)) if p else page
    if path == '.' or p.endswith('/'):
        path = posixpath.join(path if path != '.' else '', 'index.html')
    return path, unquote(u.fragment)


def css_refs(text):
    return re.findall(r'url\(\s*[\"\']?([^\"\')\s]+)', text, re.I)


def audit(root=ROOT):
    files = {p.relative_to(root).as_posix(): p for p in root.rglob('*') if p.is_file() and not {'.git', '__pycache__'}.intersection(p.relative_to(root).parts)}
    pages = {name: Page(p.read_text(encoding='utf-8')) for name, p in sorted(files.items()) if name.endswith('.html')}
    findings, inventory, refs = [], {}, []

    def issue(code, page, detail):
        findings.append({'code': code, 'page': page, 'detail': detail})

    def reference(page, ref, kind, line=0):
        target = local_path(page, ref)
        if target is None:
            return
        path, fragment = target
        refs.append({'page': page, 'line': line, 'kind': kind, 'ref': ref, 'target': path, 'fragment': fragment})
        # Directory enumeration and dict lookup are case-sensitive even on Windows.
        if path not in files:
            issue('missing-target', page, path)
        elif fragment and path in pages:
            ids = {n.attrs.get('id') for n in pages[path].nodes}
            ids.update(n.attrs.get('name') for n in pages[path].tags('a'))
            if fragment not in ids:
                issue('missing-fragment', page, path + '#' + fragment)

    if not pages:
        issue('html', '.', 'No HTML files')
    expected_sitemap = set()
    for name, page in pages.items():
        raw = files[name].read_text(encoding='utf-8')
        meta = {n.attrs.get('name', n.attrs.get('property', '')).lower(): n.attrs.get('content', '') for n in page.tags('meta')}
        titles = [n.normalized() for n in page.tags('title')]
        canonicals = [n.attrs.get('href') for n in page.tags('link') if n.attrs.get('rel', '').lower() == 'canonical']
        expected = BASE + ('/' if name == 'index.html' else '/' + name)
        noindex = 'noindex' in meta.get('robots', '').lower()
        if len(titles) != 1 or not titles[0]:
            issue('title', name, 'Expected one non-empty title')
        if not meta.get('description', '').strip():
            issue('description', name, 'Missing description')
        if canonicals != [expected]:
            issue('canonical', name, 'Expected ' + expected)
        if not noindex:
            expected_sitemap.add(expected)
            if meta.get('og:url') != expected:
                issue('og-url', name, 'Expected ' + expected)
        if name == 'takk.html' and not noindex:
            issue('noindex', name, 'Thank-you page must remain noindex')
        if not any(n.attrs.get('src') == 'samtykke.js' for n in page.tags('script')):
            issue('consent-script', name, 'Missing shared consent script')
        ids = Counter(n.attrs['id'] for n in page.nodes if 'id' in n.attrs)
        for value, count in ids.items():
            if count > 1:
                issue('duplicate-id', name, value)
        images = []
        for n in page.nodes:
            a = n.attrs
            if n.tag == 'img':
                if 'alt' not in a:
                    issue('alt', name, a.get('src', '(no src)'))
                if not all(re.fullmatch(r'[1-9]\d*', a.get(k, '')) for k in ('width', 'height')):
                    issue('dimensions', name, a.get('src', '(no src)'))
                images.append({'line': n.line, **a, 'picture': n.inside('picture')})
            if n.tag in ('a', 'area', 'link') and a.get('href'):
                reference(name, a['href'], n.tag, n.line)
            if n.tag in ('img', 'script', 'source', 'iframe', 'video', 'audio', 'input') and a.get('src'):
                reference(name, a['src'], n.tag, n.line)
            if a.get('poster'):
                reference(name, a['poster'], 'poster', n.line)
            if a.get('srcset') and not a['srcset'].startswith('data:'):
                for entry in a['srcset'].split(','):
                    if entry.strip():
                        reference(name, entry.strip().split()[0], 'srcset', n.line)
            for ref in css_refs(a.get('style', '')):
                reference(name, ref, 'inline-css', n.line)
            if n.tag == 'meta' and a.get('property') in ('og:image', 'og:image:secure_url'):
                reference(name, a.get('content', ''), 'og-image', n.line)
        schemas = []
        for n in page.tags('script'):
            if n.attrs.get('type') == 'application/ld+json':
                try:
                    schemas.append(json.loads(n.text()))
                except json.JSONDecodeError as exc:
                    issue('json-ld', name, str(exc))
            elif re.search(r'googletagmanager\.com|google-analytics\.com', n.attrs.get('src', '') + n.text(), re.I):
                issue('analytics-direct', name, 'Analytics code outside consent module')
        styles = '\n'.join(n.text() for n in page.tags('style'))
        for ref in css_refs(styles):
            reference(name, ref, 'css')
        commercial = [{'line': n.line, 'text': n.normalized()} for n in page.nodes if n.tag in ('p', 'li', 'option', 'h1', 'h2', 'h3', 'div', 'span') and COMMERCIAL.search(n.normalized()) and not any(isinstance(c, Node) and c.tag in ('p', 'li', 'option', 'h1', 'h2', 'h3', 'div') for c in n.children)]
        inventory[name] = {
            'title': titles, 'metadata': meta, 'canonical': canonicals, 'json_ld': schemas,
            'style_bytes': len(styles.encode()),
            'inline_scripts': len([n for n in page.tags('script') if not n.attrs.get('src') and n.attrs.get('type') != 'application/ld+json']),
            'scripts': [n.attrs['src'] for n in page.tags('script') if 'src' in n.attrs],
            'patches': sorted(set(re.findall(r'\b[A-Z][A-Z_]*(?:FIX|MEDIA|IMAGE)[A-Z_]*\b', styles))),
            'nav': [[{'text': n.normalized(), 'href': n.attrs.get('href')} for n in page.tags('a') if n.inside('nav')]],
            'footer': [n.normalized() for n in page.tags('footer')],
            'images': images, 'commercial': commercial,
            'booking_options': [n.normalized() for n in page.tags('option')],
            'forms': [{'tag': n.tag, **n.attrs} for n in page.nodes if n.tag in ('form', 'input', 'select', 'textarea', 'button') and (n.inside('form') or n.tag == 'form')],
            'css_variables': dict(re.findall(r'(--[\w-]+)\s*:\s*([^;}]+)', styles)),
            'media_queries': re.findall(r'@media\s*([^\{]+)', styles),
            # Candidates only: equal selectors in different media contexts are not necessarily redundant.
            'css_rules': [{'selector': ' '.join(selector.split()), 'declarations': ' '.join(body.split())}
                          for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', re.sub(r'/\*.*?\*/', '', styles, flags=re.S))
                          if not selector.strip().startswith('@')],
        }
    for name, path in files.items():
        if name.endswith('.css'):
            for ref in css_refs(path.read_text(encoding='utf-8')):
                reference(name, ref, 'css')
        if name.endswith('.js') and name != 'samtykke.js' and re.search(r'googletagmanager\.com|google-analytics\.com', path.read_text(encoding='utf-8')):
            issue('analytics-direct', name, 'Analytics code outside consent module')
    try:
        sitemap = [n.text for n in ET.parse(root / 'sitemap.xml').findall('.//{*}loc')]
        for url in set(sitemap) ^ expected_sitemap:
            issue('sitemap', 'sitemap.xml', 'Unexpected or missing URL: ' + str(url))
        if len(sitemap) != len(set(sitemap)):
            issue('sitemap', 'sitemap.xml', 'Duplicate URLs')
    except (OSError, ET.ParseError) as exc:
        issue('sitemap', 'sitemap.xml', str(exc))
    robots = (root / 'robots.txt').read_text(encoding='utf-8') if (root / 'robots.txt').exists() else ''
    if not re.search(r'^Sitemap:\s*' + re.escape(BASE + '/sitemap.xml') + r'\s*$', robots, re.M):
        issue('robots', 'robots.txt', 'Missing sitemap declaration')
    if not (root / 'CNAME').exists() or (root / 'CNAME').read_text().strip() != 'www.fotograf-spalder.com':
        issue('domain', 'CNAME', 'Domain changed or missing')
    for name in sorted({r['target'] for r in refs}):
        if name in files and Path(name).suffix.lower() in IMAGE and files[name].stat().st_size > 1_800_000:
            issue('large-image', name, 'Active image exceeds 1,800,000 bytes')
    # Check the tracked tree too: Windows cannot represent both Meg.jpg and meg.jpg.
    try:
        tree = subprocess.check_output(['git', '-c', 'safe.directory=' + root.resolve().as_posix(), 'ls-tree', '-rlz', 'HEAD'], cwd=root).decode()
        tracked = []
        groups = defaultdict(list)
        for entry in tree.split('\0'):
            if not entry:
                continue
            fields, name = entry.split('\t', 1)
            _, kind, sha, size = fields.split()
            if kind == 'blob':
                tracked.append({'path': name, 'bytes': int(size), 'sha': sha})
                groups[name.casefold()].append(name)
        collisions = [names for names in groups.values() if len(names) > 1]
    except (subprocess.CalledProcessError, OSError):
        tracked, collisions = [], []
    return {'pages': inventory, 'references': refs, 'findings': findings, 'tracked_files': tracked, 'case_collisions': collisions,
            'files': sorted(files), 'image_files': sorted(n for n in files if Path(n).suffix.lower() in IMAGE)}


def protected_snapshot(result):
    return {name: {k: ([v['text'] for v in data[k]] if k == 'commercial' else data[k]) for k in ('title', 'metadata', 'canonical', 'json_ld', 'commercial', 'booking_options', 'forms')} for name, data in result['pages'].items()}


def finding_key(f):
    return json.dumps(f, ensure_ascii=False, sort_keys=True)


def check(result, baseline):
    actual = Counter(finding_key(f) for f in result['findings'])
    known = Counter(finding_key(f) for f in baseline['known_findings'])
    errors = [f'New regression ({count}): {key}' for key, count in (actual - known).items()]
    for key in (known - actual):
        errors.append('Resolved debt: remove this exact baseline entry after review: ' + key)
    expected = baseline['protected']
    current = protected_snapshot(result)
    for name in sorted(set(expected) | set(current)):
        if expected.get(name) != current.get(name):
            errors.append(name + ': protected content/SEO/booking changed; review before updating baseline')
    if result['case_collisions'] != baseline.get('case_collisions', []):
        errors.append('Tracked case collisions changed; review baseline')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--strict', action='store_true', help='Fail on existing debt as well as regressions')
    args = parser.parse_args()
    result = audit(args.root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    baseline = json.loads((args.root / '.github/site-baseline.json').read_text(encoding='utf-8'))
    errors = check(result, baseline)
    if args.strict:
        errors.extend(finding_key(f) for f in result['findings'])
        errors.extend('Case collision: ' + repr(c) for c in result['case_collisions'])
    print(f"Audited {len(result['pages'])} pages, {len(result['references'])} local references; {len(result['findings'])} recorded debt findings.")
    if errors:
        raise SystemExit('\n'.join(errors))
    print('No new regressions. Existing debt is explicitly recorded, not fixed.')


if __name__ == '__main__':
    main()
