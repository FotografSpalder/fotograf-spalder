// Execute the real inline booking code and consent module without network calls.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../..');

function consent(choice, blocked = false) {
  const elements = new Map();
  const appendedScripts = [];
  const storage = new Map(choice ? [['fotografSpalderConsentV1', choice]] : []);
  function element(tag = 'div') {
    return {
      tag, dataset: {}, handlers: {}, children: [],
      setAttribute() {}, focus() {},
      addEventListener(event, fn) { this.handlers[event] = fn; },
      appendChild(child) { this.children.push(child); if (child.id) elements.set(child.id, child); },
      remove() { elements.delete(this.id); },
      querySelector(selector) { return this.buttons[selector]; },
      set innerHTML(value) { this.buttons = { '[data-consent-allow]': element('button'), '[data-consent-reject]': element('button') }; },
    };
  }
  const document = {
    readyState: 'complete', cookie: '',
    createElement: element,
    getElementById: id => elements.get(id),
    querySelector: () => appendedScripts[0],
    querySelectorAll: () => [],
    head: { appendChild(el) { if (el.tag === 'script') appendedScripts.push(el); if (el.id) elements.set(el.id, el); } },
    body: { appendChild(el) { elements.set(el.id, el); } },
  };
  const window = { location: { hostname: 'www.fotograf-spalder.com' }, localStorage: {
    getItem(k) { if (blocked) throw Error('blocked'); return storage.get(k) ?? null; },
    setItem(k, v) { if (blocked) throw Error('blocked'); storage.set(k, v); },
  } };
  vm.runInNewContext(fs.readFileSync(path.join(root, 'samtykke.js'), 'utf8'), { window, document, encodeURIComponent });
  return { window, appendedScripts, elements,
    click(selector) { elements.get('fs-consent-overlay').children[0].buttons[selector].handlers.click(); },
    open() { elements.get('fs-privacy-settings').handlers.click(); },
  };
}

for (const choice of [null, 'analytics-rejected', 'unexpected']) {
  const c = consent(choice);
  assert.equal(c.appendedScripts.length, 0, 'No analytics before active consent');
  assert.equal(c.window['ga-disable-G-FHTXJM4638'], true);
}
const c = consent(null);
c.click('[data-consent-allow]');
assert.equal(c.appendedScripts.length, 1);
assert.match(c.appendedScripts[0].src, /^https:\/\/www\.googletagmanager\.com\/gtag\/js\?id=G-FHTXJM4638$/);
c.open(); c.click('[data-consent-reject]');
assert.equal(c.window['ga-disable-G-FHTXJM4638'], true);
c.open(); c.click('[data-consent-allow]');
assert.equal(c.appendedScripts.length, 1, 'Do not add duplicate analytics scripts');
assert.equal(consent('analytics-allowed').appendedScripts.length, 1);
const blocked = consent(null, true);
assert.equal(blocked.appendedScripts.length, 0);
blocked.click('[data-consent-allow]');
assert.equal(blocked.appendedScripts.length, 1);
console.log('Consent: unknown, rejected, accepted, revoked, repeated acceptance and blocked storage passed.');

async function booking(mode) {
  const html = fs.readFileSync(path.join(root, 'booking.html'), 'utf8');
  const script = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]).find(s => s.includes('form.addEventListener'));
  assert.ok(script, 'Booking handler exists');
  let handler;
  const form = { addEventListener: (event, fn) => { assert.equal(event, 'submit'); handler = fn; } };
  const button = { disabled: false }, status = {}, requests = [];
  const window = { location: {}, gtag() {} };
  const context = { window,
    document: { getElementById: id => ({ bookingForm: form, submitButton: button, formStatus: status })[id] },
    FormData: class { constructor(value) { assert.equal(value, form); } },
    fetch: async (url, options) => {
      assert.equal(button.disabled, true);
      requests.push({ url, options });
      if (mode === 'network-error') throw Error('Network');
      return { ok: mode === 'success' };
    },
  };
  vm.runInNewContext(script, context);
  let prevented = false;
  await handler({ preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(requests.length, 1);
  assert.equal(requests[0].url, 'https://formspree.io/f/xeepjwnb');
  assert.equal(requests[0].options.method, 'POST');
  assert.equal(requests[0].options.headers.Accept, 'application/json');
  if (mode === 'success') assert.equal(window.location.href, 'takk.html');
  else {
    assert.equal(window.location.href, undefined);
    assert.equal(button.disabled, false);
    assert.match(status.textContent, /Noe gikk galt/);
  }
}
(async () => {
  for (const mode of ['success', 'http-error', 'network-error']) await booking(mode);
  console.log('Booking: success, HTTP error and network error passed; no real submission made.');
})().catch(error => { console.error(error); process.exitCode = 1; });
