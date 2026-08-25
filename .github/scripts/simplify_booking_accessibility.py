from pathlib import Path
import re

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


# 1) Forenkle bookingformularen.
path = 'booking.html'
text = read(path)
form_start = text.index('    <form id="bookingForm">')
form_end = text.index('    </form>', form_start) + len('    </form>')
new_form = '''    <form id="bookingForm">
      <p class="small">Felt merket med <span class="required">*</span> er obligatoriske. Du trenger ikke ha alle detaljer klare for å sende en forespørsel.</p>

      <input type="hidden" name="_subject" value="Ny bookingforespørsel – Fotograf Spalder">

      <label for="navn">Navn <span class="required">*</span></label>
      <input id="navn" type="text" name="navn" placeholder="Ditt navn" autocomplete="name" required>

      <label for="email">E-post <span class="required">*</span></label>
      <input id="email" type="email" name="email" placeholder="Din e-postadresse" autocomplete="email" required>

      <label for="telefon">Telefonnummer <span class="small">(valgfritt)</span></label>
      <input id="telefon" type="tel" name="telefon" placeholder="F.eks. 98765432" autocomplete="tel" inputmode="tel">

      <label for="pakke">Hva ønsker du å fotografere? <span class="required">*</span></label>
      <select id="pakke" name="pakke" required>
        <option value="">Velg fotografering eller pakke</option>
        <optgroup label="Vanlige fotoshoots">
          <option>Grunnpakke – 3200 kr – 3 bilder inkludert</option>
          <option>Favorittpakke – 4500 kr – 5 bilder inkludert</option>
          <option>Totalpakke – 8000 kr – 10 bilder inkludert</option>
        </optgroup>
        <optgroup label="Kjæledyr">
          <option>Kjæledyr Mini – 1800 kr – 1 bilde inkludert</option>
          <option>Kjæledyr Standard – 3000 kr – 3 bilder inkludert</option>
          <option>Kjæledyr Premium – 4000 kr – 5 bilder inkludert</option>
        </optgroup>
        <optgroup label="Portrett og familie">
          <option>Portrett – 1500 kr – 1 bilde inkludert</option>
          <option>Familiefoto – 2500 kr – 2 bilder inkludert</option>
        </optgroup>
        <optgroup label="Arrangement">
          <option>Konfirmasjon – fra 3000 kr – 2 bilder inkludert</option>
          <option>Dåp – fra 3000 kr – 2 bilder inkludert</option>
          <option>Bryllup – fra 10 000 kr – 8 bilder inkludert</option>
          <option>Slektsfotografering – 7500 kr – 5 bilder inkludert</option>
          <option>Kultur og arrangement – halv dag, fra 4000–7000 kr</option>
          <option>Kultur og arrangement – heldag, fra 7000–15 000 kr</option>
        </optgroup>
        <optgroup label="Cosplay">
          <option>Cosplay Grunnpakke – 1200 kr – 1 bilde inkludert</option>
          <option>Cosplay Magipakke – 1800 kr – 2 bilder inkludert</option>
          <option>Cosplay Epos – 2800 kr – 3 bilder inkludert</option>
        </optgroup>
      </select>
      <p class="small">Usikker på pakke? Velg det som ligger nærmest. Vi kan avklare riktig løsning før booking. <a href="priser.html">Se alle priser</a>.</p>

      <label for="dato">Ønsket dato <span class="small">(valgfritt)</span></label>
      <input id="dato" type="date" name="dato">

      <label for="sted">Sted eller område <span class="small">(valgfritt)</span></label>
      <input id="sted" type="text" name="sted" placeholder="F.eks. Brumunddal, Moelv, Hamar eller vet ikke enda">

      <label for="melding">Fortell kort hva du ønsker <span class="required">*</span></label>
      <textarea id="melding" name="melding" rows="5" required placeholder="Hvem eller hva skal fotograferes, og er det noe jeg bør vite på forhånd?"></textarea>

      <!-- spam filter -->
      <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">

      <details id="vilkar" class="terms-box">
        <summary>Se vilkår for booking og betaling</summary>
        <ul>
          <li>Gi beskjed minst 24 timer før ved avbestilling eller endring.</li>
          <li>Ved mer enn 15 minutters forsinkelse kan fotograferingen forkortes eller flyttes.</li>
          <li>Dårlig vær gir ny time uten ekstra kostnad.</li>
          <li>Booking bekreftes først etter skriftlig bekreftelse og betaling av 30 % forskudd.</li>
          <li>Forskuddet reserverer ønsket dato, trekkes fra fotograferingsprisen og refunderes ikke ved avbestilling.</li>
          <li>De resterende 70 % betales via FotoSky etter fotograferingen og før privatgalleriet åpnes.</li>
          <li>Når restbeløpet er betalt, åpnes galleriet. Eventuelle tilleggskjøp kommer i tillegg.</li>
          <li>Leveringstid er normalt 1–3 uker via privat galleri.</li>
          <li>Kun antallet digitale bilder som står oppført for pakken er inkludert. Flere bilder og fulloppløselige filer kjøpes separat.</li>
        </ul>
      </details>

      <label class="checkbox-label">
        <input type="checkbox" name="vilkar_godkjent" value="Ja" required>
        <span>Jeg har lest og godtar <a href="#vilkar">vilkårene</a>, og forstår at 30 % reserverer datoen og at resterende 70 % betales via FotoSky før galleriet åpnes. <span class="required">*</span></span>
      </label>

      <label class="checkbox-label">
        <input type="checkbox" name="markedsforing_samtykke" value="Ja">
        <span>Ja, jeg samtykker til at utvalgte bilder fra oppdraget kan brukes i Fotograf Spalders portefølje, nettside og sosiale medier. Dette er frivillig og påvirker ikke bookingen.</span>
      </label>

      <p class="small">Opplysningene brukes for å behandle forespørselen. <a href="personvern.html">Les personvernerklæringen</a>.</p>
      <button id="submitButton" type="submit">Send bookingforespørsel</button>
      <p id="formStatus" class="small" role="status" aria-live="polite">Svar vanligvis innen 24 timer.</p>
    </form>'''
text = text[:form_start] + new_form + text[form_end:]

css_extra = '''

    summary {
      cursor: pointer;
      font-weight: 800;
      color: var(--accent-light);
    }

    summary:focus-visible,
    button:focus-visible,
    a:focus-visible,
    input[type="checkbox"]:focus-visible {
      outline: 3px solid var(--accent);
      outline-offset: 3px;
    }

    .terms-box[open] summary { margin-bottom: 0.8rem; }
'''
text = text.replace('    @media (max-width: 600px) {', css_extra + '\n    @media (max-width: 600px) {', 1)

script_pattern = re.compile(r'    <script>\s*const form = document\.getElementById\("bookingForm"\);.*?    </script>', re.S)
new_script = '''    <script>
      const form = document.getElementById("bookingForm");
      const submitButton = document.getElementById("submitButton");
      const formStatus = document.getElementById("formStatus");

      form.addEventListener("submit", async function(e) {
        e.preventDefault();
        submitButton.disabled = true;
        submitButton.textContent = "Sender ...";
        formStatus.textContent = "Sender forespørselen ...";

        try {
          const data = new FormData(form);
          const response = await fetch("https://formspree.io/f/xeepjwnb", {
            method: "POST",
            body: data,
            headers: { "Accept": "application/json" }
          });

          if (!response.ok) throw new Error("Formspree returnerte feilstatus");

          if (typeof window.gtag === "function") {
            window.gtag("event", "booking_sent", {
              event_category: "booking",
              event_label: "booking_form"
            });
          }
          window.location.href = "takk.html";
        } catch (error) {
          formStatus.textContent = "Noe gikk galt. Prøv igjen, eller kontakt Fotograf Spalder på e-post eller SMS.";
          submitButton.disabled = false;
          submitButton.textContent = "Send bookingforespørsel";
        }
      });
    </script>'''
text, count = script_pattern.subn(new_script, text, count=1)
if count != 1:
    raise SystemExit('Kunne ikke oppdatere booking-scriptet')
write(path, text)


# 2) Gjør tabs semantiske og tastaturvennlige på priser og portefølje.
def improve_tabs(path, tabs):
    text = read(path)
    old_tabs_match = re.search(r'<div class="tabs">.*?</div>', text, re.S)
    if not old_tabs_match:
        raise SystemExit(f'Fant ikke tabs i {path}')

    buttons = []
    for i, (panel, label) in enumerate(tabs):
        active = ' active' if i == 0 else ''
        selected = 'true' if i == 0 else 'false'
        tab_index = '0' if i == 0 else '-1'
        buttons.append(f'  <button type="button" id="tab-{panel}" class="tab{active}" role="tab" aria-selected="{selected}" aria-controls="{panel}" tabindex="{tab_index}">{label}</button>')
    new_tabs = '<div class="tabs" role="tablist" aria-label="Velg kategori">\n' + '\n'.join(buttons) + '\n</div>'
    text = text[:old_tabs_match.start()] + new_tabs + text[old_tabs_match.end():]

    for i, (panel, _) in enumerate(tabs):
        pat = re.compile(rf'<div id="{re.escape(panel)}" class="section( active)?">')
        repl = f'<div id="{panel}" class="section' + (' active' if i == 0 else '') + f'" role="tabpanel" aria-labelledby="tab-{panel}"' + ('' if i == 0 else ' hidden') + '>'
        text, n = pat.subn(repl, text, count=1)
        if n != 1:
            raise SystemExit(f'Fant ikke panel {panel} i {path}')

    if 'font: inherit;' not in text:
        text = text.replace('  user-select: none;\n}', '  user-select: none;\n  font: inherit;\n  color: var(--text);\n  appearance: none;\n}\n\n.tab:focus-visible {\n  outline: 3px solid var(--accent);\n  outline-offset: 3px;\n}', 1)

    old_script = re.compile(r'<script>\s*function showTab\(event, tab\).*?</script>', re.S)
    new_script = '''<script>
const tabList = document.querySelector('[role="tablist"]');
if (tabList) {
  const tabs = Array.from(tabList.querySelectorAll('[role="tab"]'));

  function activateTab(tab, moveFocus = false) {
    tabs.forEach(button => {
      const selected = button === tab;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-selected', String(selected));
      button.tabIndex = selected ? 0 : -1;
      const panel = document.getElementById(button.getAttribute('aria-controls'));
      if (panel) {
        panel.classList.toggle('active', selected);
        panel.hidden = !selected;
      }
    });
    if (moveFocus) tab.focus();
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab));
    tab.addEventListener('keydown', event => {
      let next = null;
      if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
      if (event.key === 'ArrowLeft') next = tabs[(index - 1 + tabs.length) % tabs.length];
      if (event.key === 'Home') next = tabs[0];
      if (event.key === 'End') next = tabs[tabs.length - 1];
      if (next) {
        event.preventDefault();
        activateTab(next, true);
      }
    });
  });
}
</script>'''
    text, n = old_script.subn(new_script, text, count=1)
    if n != 1:
        raise SystemExit(f'Kunne ikke oppdatere tab-script i {path}')
    write(path, text)


improve_tabs('priser.html', [
    ('dyr', 'Kjæledyr'),
    ('portrett', 'Portrett & familie'),
    ('event', 'Arrangement'),
    ('cosplay', 'Cosplay'),
    ('tillegg', 'Tillegg'),
])

improve_tabs('portfolio.html', [
    ('dyr', 'Kjæledyr'),
    ('portrett', 'Portrett'),
    ('familie', 'Familie'),
    ('bryllup', 'Bryllup'),
    ('cosplay', 'Cosplay'),
    ('natur', 'Natur og dyreliv'),
])


# 3) Oppgrader mobilmenyer med riktig ARIA, Escape og fokusretur.
menu_pages = [
    'index.html',
    'om.html',
    'kjaeledyrsfotograf-ringsaker.html',
    'Konfirmasjon.html',
    'sommerfotografering.html',
    'bryllupsfotograf-ringsaker.html',
    'familie-portrettfotograf-ringsaker.html',
]

menu_script = '''<script>
  const yearElement = document.getElementById('year');
  if (yearElement) yearElement.textContent = new Date().getFullYear();

  const mobileToggle = document.getElementById('mobileToggle');
  const mobileNav = document.getElementById('navLinks');

  if (mobileToggle && mobileNav) {
    const setMenuState = (open) => {
      mobileNav.classList.toggle('open', open);
      mobileToggle.setAttribute('aria-expanded', String(open));
      mobileToggle.setAttribute('aria-label', open ? 'Lukk meny' : 'Åpne meny');
      mobileToggle.textContent = open ? 'Lukk' : 'Meny';
    };

    setMenuState(false);

    mobileToggle.addEventListener('click', () => {
      setMenuState(!mobileNav.classList.contains('open'));
    });

    mobileNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => setMenuState(false));
    });

    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && mobileNav.classList.contains('open')) {
        setMenuState(false);
        mobileToggle.focus();
      }
    });
  }
</script>'''

for path in menu_pages:
    text = read(path)

    def button_repl(match):
        tag = match.group(0)
        if 'type=' not in tag:
            tag = tag[:-1] + ' type="button">'
        if 'aria-controls=' not in tag:
            tag = tag[:-1] + ' aria-controls="navLinks">'
        if 'aria-expanded=' not in tag:
            tag = tag[:-1] + ' aria-expanded="false">'
        return tag

    text, n = re.subn(r'<button\b[^>]*id="mobileToggle"[^>]*>', button_repl, text, count=1)
    if n != 1:
        raise SystemExit(f'Fant ikke mobilknapp i {path}')

    text = re.sub(r'<nav class="nav-links" id="navLinks"(?![^>]*aria-label)', '<nav class="nav-links" id="navLinks" aria-label="Hovedmeny"', text, count=1)

    focus_css = '''\n.mobile-toggle:focus-visible,\n.nav-links a:focus-visible {\n  outline: 3px solid var(--accent);\n  outline-offset: 3px;\n}\n'''
    if '.mobile-toggle:focus-visible' not in text:
        text = text.replace('</style>', focus_css + '</style>', 1)

    blocks = list(re.finditer(r'<script>(.*?)</script>', text, re.S))
    target = None
    for block in blocks:
        if 'mobileToggle' in block.group(1):
            target = block
    if not target:
        raise SystemExit(f'Fant ikke mobilmeny-script i {path}')
    text = text[:target.start()] + menu_script + text[target.end():]
    write(path, text)

print('Booking, tabs og mobilmenyer oppdatert.')
