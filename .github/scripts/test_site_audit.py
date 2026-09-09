"""Mutation tests: demonstrate that the safety net rejects actual regressions."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import site_audit as a


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        # Sparse fixture with every actual HTML/CSS/JS file and placeholder assets.
        for item in a.ROOT.rglob('*'):
            rel = item.relative_to(a.ROOT)
            if not item.is_file() or '.git' in rel.parts or '.github' in rel.parts:
                continue
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if item.suffix in ('.html', '.js', '.css', '.xml', '.txt') or item.name == 'CNAME':
                target.write_bytes(item.read_bytes())
            else:
                target.write_bytes(b'fixture')
        self.git = patch.object(a.subprocess, 'check_output', side_effect=OSError)
        self.git.start()
        self.addCleanup(self.git.stop)
        base = a.audit(self.root)
        self.baseline = {'known_findings': base['findings'], 'protected': a.protected_snapshot(base), 'case_collisions': []}

    def edit(self, name, old, new):
        p = self.root / name
        text = p.read_text(encoding='utf-8')
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, 1), encoding='utf-8')

    def rejected(self, code=None):
        result = a.audit(self.root)
        self.assertTrue(a.check(result, self.baseline))
        if code:
            self.assertIn(code, [f['code'] for f in result['findings']])

    def test_unchanged(self):
        self.assertEqual([], a.check(a.audit(self.root), self.baseline))

    def test_missing_page(self):
        (self.root / 'booking.html').unlink()
        self.rejected('missing-target')

    def test_case_sensitive_link(self):
        self.edit('index.html', 'booking.html', 'Booking.html')
        self.rejected('missing-target')

    def test_missing_fragment(self):
        self.edit('index.html', 'booking.html', 'booking.html#not-a-real-id')
        self.rejected('missing-fragment')

    def test_srcset(self):
        self.edit('portfolio.html', '.webp', '-missing.webp')
        self.rejected('missing-target')

    def test_duplicate_id(self):
        self.edit('index.html', '</body>', '<div id="navLinks"></div></body>')
        self.rejected('duplicate-id')

    def test_bad_json_ld(self):
        self.edit('index.html', '"@context":', 'INVALID "@context":')
        self.rejected('json-ld')

    def test_analytics_inline(self):
        self.edit('index.html', '</body>', '<script src="https://www.googletagmanager.com/gtag/js?id=x"></script></body>')
        self.rejected('analytics-direct')

    def test_analytics_external(self):
        (self.root / 'bad.js').write_text("fetch('https://www.google-analytics.com/collect')")
        self.rejected('analytics-direct')

    def test_price_change(self):
        self.edit('booking.html', '3000 kr', '3100 kr')
        self.rejected()

    def test_required_field_removed(self):
        self.edit('booking.html', 'autocomplete="name" required', 'autocomplete="name"')
        self.rejected()

    def test_new_image_without_alt(self):
        self.edit('index.html', '</body>', '<img src="hund2.jpg" width="100" height="100"></body>')
        self.rejected('alt')

    def test_new_image_without_dimensions(self):
        self.edit('index.html', '</body>', '<img src="hund2.jpg" alt="Hund"></body>')
        self.rejected('dimensions')

    def test_large_webp(self):
        image = next(self.root.rglob('*.webp'))
        image.write_bytes(b'x' * 1_800_001)
        self.rejected('large-image')

    def test_noindex_in_sitemap(self):
        self.edit('sitemap.xml', '</urlset>', '<url><loc>https://www.fotograf-spalder.com/takk.html</loc></url></urlset>')
        self.rejected('sitemap')

    def test_robots(self):
        self.edit('robots.txt', 'sitemap.xml', 'missing.xml')
        self.rejected('robots')

    def test_canonical(self):
        self.edit('index.html', '<link rel="canonical"', '<link rel="wrong"')
        self.rejected('canonical')

    def test_title(self):
        self.edit('index.html', '<title>', '<not-title>')
        self.rejected('title')

    def test_domain(self):
        (self.root / 'CNAME').write_text('example.com')
        self.rejected('domain')


if __name__ == '__main__':
    unittest.main()
