import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const root = path.resolve(import.meta.dirname, '..');
const source = fs.readFileSync(path.join(root, 'src', 'pages', 'restaurering-gamle-bilder', 'index.astro'), 'utf8');
const imageDirectory = path.join(root, 'public', 'images', 'restaurering-gamle-bilder');
const mailto = 'mailto:fotograf.spalder@outlook.com?subject=Vurdering%20av%20gammelt%20bilde';
const processImages = [
  'steg-1-originalt-negativ.jpg',
  'steg-2-renset-negativ.jpg',
  'steg-3-restaurert-fargelagt.jpg',
  'steg-4-ferdig-restaurering.jpg',
];

test('restoration inquiry CTAs use the dedicated email address', () => {
  assert.equal(source.match(/href=\{inquiryEmail\}/gu)?.length, 2);
  assert.ok(source.includes(`const inquiryEmail = '${mailto}';`));
  assert.equal(source.match(/Send bilde på e-post/gu)?.length, 2);
  assert.equal(source.includes('Send bilde til vurdering'), false);
  assert.equal(source.match(/Send gjerne et mobilbilde eller en skannet kopi av originalen\. Jeg vurderer hva som er mulig og gir pris før arbeidet starter\./gu)?.length, 2);
});

test('all four restoration process images remain available', () => {
  for (const image of processImages) {
    assert.ok(source.includes(`${imageBasePlaceholder(image)}`), `${image} is not referenced by the page`);
    assert.ok(fs.existsSync(path.join(imageDirectory, image)), `${image} is missing from public assets`);
  }
});

test('process images are contained within desktop and mobile height limits', () => {
  assert.ok(source.includes('.process-card img{width:100%;height:min(65vw,520px);max-height:520px;object-fit:contain;background:#080d18}'));
  assert.ok(source.includes('@media(max-width:700px){.process-grid{grid-template-columns:1fr}.process-card img{height:50vh;max-height:50vh}}'));
  assert.equal(source.includes('.process-card img{aspect-ratio:auto}'), false);
});

function imageBasePlaceholder(image) {
  return `\${imageBase}/${image}`;
}
