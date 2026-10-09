import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = path.resolve(import.meta.dirname, '..');
const dataPath = path.join(root, 'data', 'services.json');
const output = path.join(root, '.test-dist');
const astro = path.join(root, 'node_modules', 'astro', 'bin', 'astro.mjs');

function sourceFiles(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const target = path.join(directory, entry.name);
    return entry.isDirectory() ? sourceFiles(target) : entry.name.endsWith('.astro') ? [target] : [];
  });
}

function build() {
  fs.rmSync(output, { recursive: true, force: true });
  return spawnSync(process.execPath, [astro, 'build', '--outDir', output], {
    cwd: root, encoding: 'utf8', env: { ...process.env, ASTRO_TELEMETRY_DISABLED: '1' },
  });
}
function page(name) { return fs.readFileSync(path.join(output, name), 'utf8'); }
function grouped(value) { return new Intl.NumberFormat('nb-NO', { maximumFractionDigits: 0 }).format(value).replace(/\u00a0/g, ' '); }
function price(service, lower = false) {
  const value = service.price >= 10000 ? grouped(service.price) : String(service.price);
  const maximum = service.max_price === null ? '' : `–${service.max_price >= 10000 ? grouped(service.max_price) : service.max_price}`;
  return `${service.from_price ? (lower ? 'fra ' : 'Fra ') : ''}${value}${maximum}`;
}

test('schema v2 contains structured copy and no generic data tokens', () => {
  const text = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(text);
  assert.equal(data.schema_version, 2);
  assert.equal(text.includes('{{'), false);
  assert.deepEqual(data.rules.booking_terms, ['cancellation','late-arrival','weather','deposit','deposit-refund','balance','gallery','delivery','included-images']);
});

test('Astro authoring sources do not hardcode commercial values', () => {
  const patterns = {
    'literal price': /\b\d[\d \u00a0]*(?:[–-]\d[\d ]*)?\s*kr\b/giu,
    'literal payment percentage': /\b(?:30|70)\s*%/giu,
    'literal included images': /\b\d+\s+(?:digitale?\s+|digitalt\s+)?bilder?\s+(?:inkludert|i høy kvalitet)/giu,
    'literal delivery range': /\b\d+[–-]\d+\s+uker/giu,
    'literal JSON-LD price': /"(?:price|lowPrice|highPrice)"\s*:\s*"?\d/giu,
  };
  const errors = [];
  for (const file of [...sourceFiles(path.join(root, 'src', 'pages')), ...sourceFiles(path.join(root, 'src', 'components'))]) {
    let source = fs.readFileSync(file, 'utf8');
    source = source.replace(/^---[\s\S]*?---/u, '');
    source = source.replace(/<style\b[^>]*>[\s\S]*?<\/style>/giu, '');
    source = source.replace(/<script(?![^>]*application\/ld\+json)[^>]*>[\s\S]*?<\/script>/giu, '');
    source = source.replace(/\{[^{}\n]+\}/gu, 'DATA');
    for (const [label, pattern] of Object.entries(patterns)) {
      for (const match of source.matchAll(pattern)) errors.push(`${path.relative(root, file)}: ${label}: ${match[0]}`);
    }
  }
  assert.deepEqual(errors, []);
});

test('commercial mutations propagate through the Astro build', { timeout: 120000 }, () => {
  const original = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(original);
  try {
    for (const service of Object.values(data.services)) service.price += 111;
    data.services['pet-standard'].name = 'Kjæledyr Ny Standard';
    data.services['pet-standard'].included_images = 1;
    data.services['pet-standard'].content[0] = 'Kanonisk testinnhold';
    data.digital.high_resolution.price = 511;
    data.digital.complete.price = 6601;
    Object.assign(data.rules, { deposit_percent: 25, balance_percent: 75, delivery_min_weeks: 2, delivery_max_weeks: 4 });
    fs.writeFileSync(dataPath, JSON.stringify(data, null, 2) + '\n');
    const result = build();
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const prices = page('priser.html');
    const booking = page('booking.html');
    for (const service of Object.values(data.services)) {
      assert.ok(prices.includes(`${price(service)} kr`), `${service.name} price missing from priser.html`);
      assert.ok(booking.includes(`${price(service, true)} kr`), `${service.name} price missing from booking.html`);
    }
    const pets = page('kjaeledyrsfotograf-ringsaker.html');
    for (const html of [prices, booking, pets]) assert.ok(html.includes('Kjæledyr Ny Standard'));
    assert.ok(pets.includes('Kanonisk testinnhold'));
    const schemas = [...pets.matchAll(/<script[^>]+type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gu)].map((match) => JSON.parse(match[1]));
    const offers = schemas[0].hasOfferCatalog.itemListElement;
    assert.equal(offers[1].price, String(data.services['pet-standard'].price));
    assert.equal(offers[1].name, 'Kjæledyr Ny Standard');
    assert.ok(prices.includes('1 digitalt bilde i høy kvalitet'));
    assert.ok(booking.includes('1 bilde inkludert'));
    for (const name of ['priser.html','booking.html','Konfirmasjon.html','familie-portrettfotograf-ringsaker.html','bryllupsfotograf-ringsaker.html','kjaeledyrsfotograf-ringsaker.html']) {
      const html = page(name); assert.ok(html.includes('511 kr')); assert.ok(html.includes('6 601 kr'));
    }
    assert.ok(prices.includes('Ekstra 30 minutter: +500 kr'));
    assert.ok(prices.includes('Ekspressredigering innen 48 timer: +500 kr'));
    assert.ok(page('bryllupsfotograf-ringsaker.html').includes('ikke større bryllupsgallerier'));
    assert.ok(booking.includes('avtales komplett galleri separat'));
    for (const name of ['priser.html','booking.html','takk.html','familie-portrettfotograf-ringsaker.html','bryllupsfotograf-ringsaker.html']) {
      const html = page(name); assert.ok(html.includes('25 %')); assert.ok(html.includes('75 %'));
    }
    for (const name of ['booking.html','Konfirmasjon.html','sommerfotografering.html']) assert.ok(page(name).includes('2–4 uker'));
  } finally {
    fs.writeFileSync(dataPath, original);
    fs.rmSync(output, { recursive: true, force: true });
  }
});

test('derived ranges and escaping propagate safely', { timeout: 120000 }, () => {
  const original = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(original);
  try {
    data.services['pet-mini'].price = 1900;
    data.services.total.price = 8100;
    data.services['pet-standard'].name = '<script>"test"</script>';
    fs.writeFileSync(dataPath, JSON.stringify(data, null, 2) + '\n');
    const result = build();
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.ok(page('index.html').includes('"1900-4000"'));
    assert.ok(page('familie-portrettfotograf-ringsaker.html').includes('"highPrice":"8100"'));
    assert.equal(page('booking.html').includes('<script>"test"</script>'), false);
    assert.ok(page('booking.html').includes('&lt;script&gt;'));
    const pets = page('kjaeledyrsfotograf-ringsaker.html');
    for (const match of pets.matchAll(/<script[^>]+type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gu)) JSON.parse(match[1]);
  } finally {
    fs.writeFileSync(dataPath, original);
    fs.rmSync(output, { recursive: true, force: true });
  }
});

test('invalid commercial data fails closed', { timeout: 120000 }, () => {
  const original = fs.readFileSync(dataPath, 'utf8');
  const mutations = [
    ['payment split', (data) => { data.rules.balance_percent = 71; }, /Deposit and balance must sum to 100/],
    ['negative price', (data) => { data.services['pet-standard'].price = -1; }, /pet-standard\.price must be an integer/],
    ['boolean image count', (data) => { data.services['pet-standard'].included_images = true; }, /pet-standard\.included_images must be an integer/],
    ['delivery range', (data) => { data.rules.delivery_min_weeks = 9; }, /Invalid delivery range/],
    ['empty exception', (data) => { data.digital.complete.separately_quoted = ''; }, /separately_quoted must contain text/],
    ['duplicate booking service', (data) => { data.booking_groups[0].services.push('pet-standard'); }, /Each service must appear once/],
  ];
  try {
    for (const [label, mutate, message] of mutations) {
      const data = JSON.parse(original);
      mutate(data);
      fs.writeFileSync(dataPath, JSON.stringify(data, null, 2) + '\n');
      const result = build();
      assert.notEqual(result.status, 0, `${label} unexpectedly built`);
      assert.match(result.stdout + result.stderr, message, label);
    }
  } finally {
    fs.writeFileSync(dataPath, original);
    fs.rmSync(output, { recursive: true, force: true });
  }
});
