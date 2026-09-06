"""Data mutation tests verify propagation, isolation and fail-closed generation."""
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import build_site as b
import check_commercial
from site_audit import Page


class BusinessDataTests(unittest.TestCase):
    def setUp(self):
        self.data = b.load_data()

    def rendered(self):
        return b.build(check=True, data=self.data)[1]

    def test_baseline_has_identical_html(self):
        stale, _ = b.build(check=True)
        self.assertEqual(stale, [])
        self.assertEqual(check_commercial.check(), [])

    def test_all_package_prices_propagate_to_price_page_and_booking(self):
        for key in self.data['services']:
            with self.subTest(service=key):
                self.data = b.load_data()
                service = self.data['services'][key]
                service['price'] += 111
                pages = self.rendered()
                prices = Page(pages['priser.html'])
                heading = next(n for n in prices.tags('h2') if n.normalized().lstrip('⭐ ') == service['name'])
                self.assertIn(b.price(service) + ' kr', heading.parent.normalized())
                options = Page(pages['booking.html']).tags('option')
                option = next(n for n in options if n.normalized().startswith(service['name'] + (' – ' if service['max_price'] is None else ', ')))
                self.assertIn(b.price(service, lower=True) + ' kr', option.normalized())

    def test_pet_standard_price_and_name_reach_landing_and_jsonld(self):
        self.data['services']['pet-standard'].update(price=3101, name='Kjæledyr Ny Standard')
        pages = self.rendered()
        for name in ('priser.html', 'booking.html', 'kjaeledyrsfotograf-ringsaker.html'):
            self.assertIn('3101 kr', pages[name])
            self.assertIn('Kjæledyr Ny Standard', pages[name])
        schemas = [json.loads(n.text()) for n in Page(pages['kjaeledyrsfotograf-ringsaker.html']).tags('script') if n.attrs.get('type') == 'application/ld+json']
        offers = schemas[0]['hasOfferCatalog']['itemListElement']
        self.assertEqual(offers[1]['price'], '3101')
        self.assertEqual(offers[1]['name'], 'Kjæledyr Ny Standard')
        self.assertIn('fra 3000 kr', pages['booking.html'], 'Confirmation/baptism keep their independent price')

    def test_pet_included_count_and_grammar(self):
        self.data['services']['pet-standard']['included_images'] = 1
        pages = self.rendered()
        for name in ('priser.html', 'kjaeledyrsfotograf-ringsaker.html'):
            page = Page(pages[name])
            heading = next(n for n in page.nodes if n.tag in ('h2', 'h3') and n.normalized().lstrip('⭐ ') == 'Kjæledyr Standard')
            self.assertIn('1 digitalt bilde', heading.parent.normalized())
        self.assertIn('Kjæledyr Standard – 3000 kr – 1 bilde inkludert', pages['booking.html'])

    def test_extra_500_is_independent_of_digital_500(self):
        self.data['digital']['high_resolution']['price'] = 511
        pages = self.rendered()
        for name in ('priser.html', 'booking.html', 'Konfirmasjon.html', 'familie-portrettfotograf-ringsaker.html', 'bryllupsfotograf-ringsaker.html', 'kjaeledyrsfotograf-ringsaker.html'):
            self.assertIn('511 kr', pages[name])
        self.assertIn('Ekstra 30 minutter: +500 kr', pages['priser.html'])
        self.assertIn('Ekspressredigering innen 48 timer: +500 kr', pages['priser.html'])
        self.assertIn('6 500 kr', pages['priser.html'])

    def test_complete_gallery_price_and_exception(self):
        self.data['digital']['complete']['price'] = 6601
        pages = self.rendered()
        for name in ('priser.html', 'booking.html', 'Konfirmasjon.html', 'familie-portrettfotograf-ringsaker.html', 'bryllupsfotograf-ringsaker.html', 'kjaeledyrsfotograf-ringsaker.html'):
            self.assertIn('6 601 kr', pages[name])
        self.assertIn('ikke større bryllupsgallerier', pages['bryllupsfotograf-ringsaker.html'])
        self.assertIn('avtales komplett galleri separat', pages['booking.html'])

    def test_payment_percentage_reaches_all_five_pages(self):
        self.data['rules'].update(deposit_percent=25, balance_percent=75)
        pages = self.rendered()
        for name in ('priser.html', 'booking.html', 'takk.html', 'familie-portrettfotograf-ringsaker.html', 'bryllupsfotograf-ringsaker.html'):
            self.assertIn('25 %', pages[name])
            self.assertIn('75 %', pages[name])
            self.assertNotIn('30 %', pages[name])
            self.assertNotIn('70 %', pages[name])

    def test_delivery_range(self):
        self.data['rules'].update(delivery_min_weeks=2, delivery_max_weeks=4)
        pages = self.rendered()
        for name in ('booking.html', 'Konfirmasjon.html', 'sommerfotografering.html'):
            self.assertIn('2–4 uker', pages[name])
            self.assertNotIn('1–3 uker', pages[name])

    def test_aggregate_ranges_are_derived(self):
        self.data['services']['pet-mini']['price'] = 1900
        self.data['services']['total']['price'] = 8100
        pages = self.rendered()
        self.assertIn('"1900-4000"', pages['index.html'])
        self.assertIn('"highPrice":"8100"', pages['familie-portrettfotograf-ringsaker.html'])

    def test_package_content_has_one_canonical_value(self):
        self.data['services']['pet-standard']['content'][0] = 'Avtalt fotografering av kjæledyr'
        pages = self.rendered()
        self.assertIn('Avtalt fotografering av kjæledyr', pages['priser.html'])
        self.assertIn('Avtalt fotografering av kjæledyr', pages['kjaeledyrsfotograf-ringsaker.html'])

    def test_invalid_data_fails(self):
        for mutate in (
            lambda d: d['rules'].update(balance_percent=69),
            lambda d: d['services']['pet-standard'].update(price=-1),
            lambda d: d['services']['pet-standard'].update(included_images=True),
            lambda d: d['rules'].update(delivery_min_weeks=9),
            lambda d: d['digital']['complete'].update(separately_quoted=''),
            lambda d: d['booking_groups'][0]['services'].append('pet-standard'),
        ):
            data = copy.deepcopy(self.data)
            mutate(data)
            with self.assertRaises(ValueError):
                b.validate(data)

    def test_unknown_token_and_cycles_fail(self):
        with self.assertRaises(ValueError):
            b.render('{{ services.missing.price }}', self.data)
        self.data['rules']['cycle'] = '{{ rules.cycle }}'
        with self.assertRaises(ValueError):
            b.render('{{ rules.cycle }}', self.data)

    def test_html_and_json_escaping(self):
        self.data['services']['pet-standard']['name'] = '<script>"test"</script>'
        pages = self.rendered()
        self.assertNotIn('<script>"test"</script>', pages['booking.html'])
        self.assertIn('&lt;script&gt;', pages['booking.html'])
        for n in Page(pages['kjaeledyrsfotograf-ringsaker.html']).tags('script'):
            if n.attrs.get('type') == 'application/ld+json':
                json.loads(n.text())
        self.data['rules']['nested'] = '<b>{{ rules.deposit_percent }}</b>'
        self.assertEqual('&lt;b&gt;30&lt;/b&gt;', b.render('{{ rules.nested }}', self.data))

    def test_build_check_does_not_write_and_build_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'templates/pages').mkdir(parents=True)
            (root / 'index.html').write_text('old')
            (root / 'templates/pages/index.html.tmpl').write_text('{{ services.pet-standard.price }}')
            self.assertEqual(['index.html'], b.build(root, check=True, data=self.data)[0])
            self.assertEqual('old', (root / 'index.html').read_text())
            self.assertEqual(['index.html'], b.build(root, data=self.data)[0])
            self.assertEqual([], b.build(root, data=self.data)[0])

    def test_invalid_last_template_cannot_partially_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'templates/pages').mkdir(parents=True)
            for name, token in [('a', '{{ services.pet-standard.price }}'), ('z', '{{ missing }}')]:
                (root / (name + '.html')).write_text('old')
                (root / 'templates/pages' / (name + '.html.tmpl')).write_text(token)
            with self.assertRaises(ValueError):
                b.build(root, data=self.data)
            self.assertEqual('old', (root / 'a.html').read_text())


if __name__ == '__main__':
    unittest.main()

