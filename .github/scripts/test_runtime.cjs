// Execute the real shared scripts without network calls.
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
  vm.runInNewContext(fs.readFileSync(path.join(root, 'public/samtykke.js'), 'utf8'), { window, document, encodeURIComponent });
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
  assert.match(html, /<script src="assets\/js\/booking\.js" defer><\/script>/);
  const script = fs.readFileSync(path.join(root, 'public/assets/js/booking.js'), 'utf8');
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

function siteBehavior() {
  function node(id) {
    const classes = new Set();
    return {
      id, textContent: '', hidden: false, tabIndex: -1, focused: false, handlers: {}, attrs: {},
      classList: {
        toggle(name, force) { force ? classes.add(name) : classes.delete(name); },
        contains(name) { return classes.has(name); },
      },
      setAttribute(name, value) { this.attrs[name] = value; },
      getAttribute(name) { return this.attrs[name]; },
      addEventListener(name, fn) { this.handlers[name] = fn; },
      focus() { this.focused = true; },
      querySelectorAll() { return this.links || []; },
    };
  }
  const year = node('year'), toggle = node('mobileToggle'), nav = node('navLinks'), link = node('link');
  nav.links = [link];
  const tab1 = node('tab1'), tab2 = node('tab2'), panel1 = node('panel1'), panel2 = node('panel2');
  tab1.attrs['aria-controls'] = 'panel1'; tab2.attrs['aria-controls'] = 'panel2';
  const tabList = { querySelectorAll: () => [tab1, tab2] };
  const nodes = { year, mobileToggle: toggle, navLinks: nav, panel1, panel2 };
  const handlers = {};
  const document = {
    getElementById: id => nodes[id],
    querySelector: selector => selector === '[role="tablist"]' ? tabList : null,
    addEventListener(name, fn) { handlers[name] = fn; },
  };
  class FixedDate { getFullYear() { return 2026; } }
  vm.runInNewContext(fs.readFileSync(path.join(root, 'public/assets/js/site.js'), 'utf8'), { document, Date: FixedDate, Array });
  assert.equal(year.textContent, 2026);
  assert.equal(toggle.attrs['aria-expanded'], 'false');
  toggle.handlers.click();
  assert.equal(nav.classList.contains('open'), true);
  assert.equal(toggle.attrs['aria-label'], 'Lukk meny');
  link.handlers.click();
  assert.equal(nav.classList.contains('open'), false);
  toggle.handlers.click();
  handlers.keydown({ key: 'Escape' });
  assert.equal(nav.classList.contains('open'), false);
  assert.equal(toggle.focused, true);
  tab2.handlers.click();
  assert.equal(tab2.attrs['aria-selected'], 'true');
  assert.equal(panel2.hidden, false);
  let prevented = false;
  tab2.handlers.keydown({ key: 'ArrowRight', preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(tab1.focused, true);
  assert.equal(panel1.hidden, false);
  assert.equal(panel2.hidden, true);
  console.log('Shared site behavior: year, mobile menu, Escape, link-close and keyboard tabs passed.');
}

siteBehavior();
(async () => {
  for (const mode of ['success', 'http-error', 'network-error']) await booking(mode);
  console.log('Booking: success, HTTP error and network error passed; no real submission made.');
})().catch(error => { console.error(error); process.exitCode = 1; });
