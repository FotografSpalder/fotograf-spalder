import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = path.resolve('dist');
const pagePath = path.join(root, 'arrangementsfotografering.html');

test('arrangementssiden har komplett SEO- og innholdskontrakt', () => {
  const html = fs.readFileSync(pagePath, 'utf8');
  assert.match(html, /<title>Arrangementsfotograf i Ringsaker og Innlandet \| Fotograf Spalder<\/title>/);
  assert.match(html, /<link rel="canonical" href="https:\/\/www\.fotograf-spalder\.com\/arrangementsfotografering\.html">/);
  assert.match(html, /<meta name="robots" content="index, follow">/);
  assert.match(html, /<meta property="og:url" content="https:\/\/www\.fotograf-spalder\.com\/arrangementsfotografering\.html">/);
  assert.match(html, /<h1>Arrangements<wbr>fotografering i Ringsaker og Innlandet<\/h1>/);
  assert.match(html, /4 000–7 000 kr/);
  assert.match(html, /7 000–15 000 kr/);
  assert.match(html, /"@type":"Service"/);
  assert.match(html, /href="booking\.html"/);
});

test('arrangementssiden bruker 18 lokale fotografier med dimensjoner og lazy loading i galleriet', () => {
  const html = fs.readFileSync(pagePath, 'utf8');
  const imageTags = [...html.matchAll(/<img\b[^>]*>/g)].map(([tag]) => tag);
  assert.equal(imageTags.length, 18);
  assert.equal(imageTags.filter((tag) => tag.includes('loading="lazy"')).length, 17);
  for (const tag of imageTags) {
    assert.match(tag, /\bwidth="\d+"/);
    assert.match(tag, /\bheight="\d+"/);
    assert.match(tag, /\balt="[^"]+"/);
    const source = tag.match(/\bsrc="([^"]+\.jpg)"/)?.[1];
    assert.ok(source, `Mangler lokal JPEG-kilde i ${tag}`);
    assert.ok(fs.existsSync(path.join(root, source)), `Mangler bildefil ${source}`);
    assert.ok(fs.existsSync(path.join(root, source.replace(/\.jpg$/, '.webp'))), `Mangler WebP-fil for ${source}`);
  }
});

test('arrangementssiden er lenket internt og registrert i sitemap', () => {
  const home = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
  const portfolio = fs.readFileSync(path.join(root, 'portfolio.html'), 'utf8');
  const sitemap = fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8');
  assert.match(home, /href="arrangementsfotografering\.html"/);
  assert.match(portfolio, /href="arrangementsfotografering\.html"/);
  assert.match(sitemap, /https:\/\/www\.fotograf-spalder\.com\/arrangementsfotografering\.html/);
});
