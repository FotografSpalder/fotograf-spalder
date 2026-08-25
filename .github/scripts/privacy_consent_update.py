from pathlib import Path
import re

ROOT = Path('.')
GA_ID = 'G-FHTXJM4638'
CONSENT_SCRIPT = 'samtykke.js'
PRIVACY_PAGE = 'personvern.html'

CONSENT_JS = r'''(() => {
  'use strict';

  const GA_ID = 'G-FHTXJM4638';
  const STORAGE_KEY = 'fotografSpalderConsentV1';
  const ALLOW = 'analytics-allowed';
  const REJECT = 'analytics-rejected';
  let analyticsLoaded = false;

  // Gjør gtag trygt å kalle fra øvrig sidekode også når analyse ikke er tillatt.
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () {
    window.dataLayer.push(arguments);
  };

  function getChoice() {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (_) {
      return null;
    }
  }

  function saveChoice(value) {
    try {
      window.localStorage.setItem(STORAGE_KEY, value);
    } catch (_) {
      // Hvis lagring er blokkert, brukes valget bare for denne sidevisningen.
    }
  }

  function loadAnalytics() {
    if (analyticsLoaded || document.querySelector('script[data-fs-google-analytics]')) {
      window['ga-disable-' + GA_ID] = false;
      return;
    }

    analyticsLoaded = true;
    window['ga-disable-' + GA_ID] = false;

    window.gtag('consent', 'default', {
      analytics_storage: 'granted'
    });
    window.gtag('js', new Date());
    window.gtag('config', GA_ID);

    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
    script.dataset.fsGoogleAnalytics = 'true';
    document.head.appendChild(script);
  }

  function clearAnalyticsCookies() {
    const cookieNames = document.cookie
      .split(';')
      .map(cookie => cookie.split('=')[0].trim())
      .filter(name => /^(_ga|_gid|_gat)/.test(name));

    const host = window.location.hostname;
    const domains = ['', host, '.' + host, 'fotograf-spalder.com', '.fotograf-spalder.com'];

    cookieNames.forEach(name => {
      domains.forEach(domain => {
        const domainPart = domain ? '; domain=' + domain : '';
        document.cookie = name + '=; Max-Age=0; path=/' + domainPart + '; SameSite=Lax';
      });
    });
  }

  function disableAnalytics() {
    window['ga-disable-' + GA_ID] = true;
    window.gtag('consent', 'update', {
      analytics_storage: 'denied'
    });
    clearAnalyticsCookies();
  }

  function addStyles() {
    if (document.getElementById('fs-consent-styles')) return;

    const style = document.createElement('style');
    style.id = 'fs-consent-styles';
    style.textContent = `
      #fs-consent-overlay {
        position: fixed;
        inset: 0;
        z-index: 2147483645;
        background: rgba(2, 6, 23, .62);
        display: flex;
        align-items: flex-end;
        justify-content: center;
        padding: 1rem;
      }
      #fs-consent-panel {
        width: min(100%, 760px);
        background: #111827;
        color: #f8fafc;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 20px;
        box-shadow: 0 24px 70px rgba(0,0,0,.45);
        padding: 1.25rem;
        font-family: Arial, Helvetica, sans-serif;
        line-height: 1.5;
      }
      #fs-consent-panel h2 {
        margin: 0 0 .65rem;
        font-size: 1.35rem;
        color: #fff;
      }
      #fs-consent-panel p {
        margin: .5rem 0;
        color: #cbd5e1;
      }
      #fs-consent-panel a {
        color: #fde68a;
        text-decoration: underline;
        text-underline-offset: 2px;
      }
      .fs-consent-actions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .75rem;
        margin-top: 1rem;
      }
      .fs-consent-button {
        min-height: 48px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.22);
        padding: .75rem 1rem;
        font: inherit;
        font-weight: 800;
        cursor: pointer;
      }
      .fs-consent-button.allow {
        background: #f59e0b;
        color: #111827;
        border-color: #f59e0b;
      }
      .fs-consent-button.reject {
        background: transparent;
        color: #f8fafc;
      }
      #fs-privacy-settings {
        position: fixed;
        right: .8rem;
        bottom: .8rem;
        z-index: 2147483644;
        border: 1px solid rgba(255,255,255,.22);
        border-radius: 999px;
        background: rgba(17,24,39,.94);
        color: #fde68a;
        padding: .55rem .8rem;
        font: 700 .82rem Arial, Helvetica, sans-serif;
        cursor: pointer;
        box-shadow: 0 10px 28px rgba(0,0,0,.3);
      }
      @media (max-width: 560px) {
        #fs-consent-overlay { padding: .65rem; }
        #fs-consent-panel { border-radius: 16px; padding: 1rem; }
        .fs-consent-actions { grid-template-columns: 1fr; }
        #fs-privacy-settings { right: .55rem; bottom: .55rem; }
      }
    `;
    document.head.appendChild(style);
  }

  function closePanel() {
    const overlay = document.getElementById('fs-consent-overlay');
    if (overlay) overlay.remove();
  }

  function showPanel() {
    addStyles();
    closePanel();

    const overlay = document.createElement('div');
    overlay.id = 'fs-consent-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-labelledby', 'fs-consent-title');

    const panel = document.createElement('div');
    panel.id = 'fs-consent-panel';
    panel.innerHTML = `
      <h2 id="fs-consent-title">Personvern og analyse</h2>
      <p>Nettsiden bruker nødvendige teknologier for grunnleggende funksjon og for å huske personvernvalget ditt.</p>
      <p>Med ditt samtykke bruker Fotograf Spalder også Google Analytics for å forstå hvordan nettsiden brukes. Google Analytics lastes ikke inn før du aktivt tillater analyse.</p>
      <p><a href="personvern.html">Les personvernerklæringen</a></p>
      <div class="fs-consent-actions">
        <button type="button" class="fs-consent-button reject" data-consent-reject>Kun nødvendige</button>
        <button type="button" class="fs-consent-button allow" data-consent-allow>Tillat analyse</button>
      </div>
    `;

    overlay.appendChild(panel);
    document.body.appendChild(overlay);

    panel.querySelector('[data-consent-allow]').addEventListener('click', () => {
      saveChoice(ALLOW);
      loadAnalytics();
      closePanel();
    });

    panel.querySelector('[data-consent-reject]').addEventListener('click', () => {
      saveChoice(REJECT);
      disableAnalytics();
      closePanel();
    });

    const firstButton = panel.querySelector('[data-consent-reject]');
    if (firstButton) firstButton.focus();
  }

  function addSettingsButton() {
    if (document.getElementById('fs-privacy-settings')) return;
    addStyles();

    const button = document.createElement('button');
    button.type = 'button';
    button.id = 'fs-privacy-settings';
    button.textContent = 'Personvernvalg';
    button.setAttribute('aria-label', 'Endre valg for personvern og analyse');
    button.addEventListener('click', showPanel);
    document.body.appendChild(button);

    document.querySelectorAll('[data-open-privacy-settings]').forEach(el => {
      el.addEventListener('click', showPanel);
    });
  }

  function init() {
    addSettingsButton();
    const choice = getChoice();

    if (choice === ALLOW) {
      loadAnalytics();
    } else if (choice === REJECT) {
      disableAnalytics();
    } else {
      disableAnalytics();
      showPanel();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
'''

PRIVACY_HTML = r'''<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Personvern og informasjonskapsler | Fotograf Spalder</title>
  <meta name="description" content="Personvernerklæring for Fotograf Spalder. Les hvordan bookingopplysninger, kundedata og Google Analytics behandles, og hvordan du kan endre samtykke.">
  <meta name="robots" content="index, follow">
  <meta property="og:title" content="Personvern og informasjonskapsler | Fotograf Spalder">
  <meta property="og:description" content="Slik behandler Fotograf Spalder personopplysninger og analysevalg på nettsiden.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://www.fotograf-spalder.com/personvern.html">
  <link rel="canonical" href="https://www.fotograf-spalder.com/personvern.html">
  <link rel="icon" type="image/png" href="Untitled-1.png">
  <meta name="theme-color" content="#0f172a">
  <script src="samtykke.js" defer></script>
  <style>
    :root{--bg:#0f172a;--card:rgba(255,255,255,.07);--text:#f8fafc;--muted:#cbd5e1;--line:rgba(255,255,255,.13);--accent:#f59e0b;--accent-light:#fde68a;--max:900px;--radius:20px;--shadow:0 18px 40px rgba(0,0,0,.25)}
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Arial,Helvetica,sans-serif;background:radial-gradient(circle at top,rgba(245,158,11,.13),transparent 34%),linear-gradient(180deg,#0b1120 0%,#111827 100%);color:var(--text);line-height:1.65}a{color:var(--accent-light)}.container{width:min(100% - 2rem,var(--max));margin:0 auto}.header{padding:4rem 0 2rem}.eyebrow{display:inline-block;padding:.35rem .7rem;border-radius:999px;background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.35);color:var(--accent-light);font-weight:800}.header h1{font-size:clamp(2rem,5vw,3.6rem);line-height:1.1;margin:.9rem 0}.lead{color:var(--muted);font-size:1.08rem;max-width:70ch}.summary,.section{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:1.35rem;margin:1rem 0;box-shadow:var(--shadow)}.summary strong{color:#fff}.section h2{margin-top:0}.section p,.section li{color:var(--muted)}.section ul{padding-left:1.2rem}.table-wrap{overflow-x:auto}.privacy-table{width:100%;border-collapse:collapse;min-width:620px}.privacy-table th,.privacy-table td{text-align:left;vertical-align:top;padding:.8rem;border-bottom:1px solid var(--line)}.privacy-table th{color:#fff}.privacy-table td{color:var(--muted)}.actions{display:flex;gap:.75rem;flex-wrap:wrap;margin:1.25rem 0 3rem}.button{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:.75rem 1rem;border-radius:999px;text-decoration:none;font-weight:800;border:1px solid var(--line);background:transparent;color:var(--text);cursor:pointer}.button.primary{background:var(--accent);color:#111827;border-color:var(--accent)}.footer{border-top:1px solid var(--line);padding:1.5rem 0 4rem;color:var(--muted)}@media(max-width:600px){.header{padding-top:2.5rem}.summary,.section{padding:1rem}.actions{flex-direction:column}.button{width:100%}}
  </style>
</head>
<body>
  <main class="container">
    <header class="header">
      <span class="eyebrow">Fotograf Spalder</span>
      <h1>Personvern og informasjonskapsler</h1>
      <p class="lead">Her forklares hvilke personopplysninger som behandles når du besøker nettsiden, sender en bookingforespørsel eller bruker kundetjenester, og hvilke valg du har.</p>
      <p class="lead"><strong>Sist oppdatert: 25. august 2026.</strong></p>
    </header>

    <section class="summary">
      <strong>Kort fortalt:</strong> Google Analytics er valgfritt og lastes ikke inn før du aktivt tillater analyse. Bookingopplysninger brukes for å svare på forespørselen og håndtere et eventuelt kundeoppdrag. Du kan endre analysevalget når som helst.
    </section>

    <section class="section">
      <h2>1. Hvem er behandlingsansvarlig?</h2>
      <p>Fotograf Spalder er behandlingsansvarlig for personopplysninger som behandles i forbindelse med nettsiden og fotografvirksomheten.</p>
      <ul>
        <li>Virksomhet: Fotograf Spalder</li>
        <li>Område: Ringsaker, Innlandet</li>
        <li>E-post: <a href="mailto:fotograf.spalder@outlook.com">fotograf.spalder@outlook.com</a></li>
        <li>Telefon/SMS: <a href="tel:+4799535760">+47 99 53 57 60</a></li>
      </ul>
    </section>

    <section class="section">
      <h2>2. Bookingforespørsler og kundekontakt</h2>
      <p>Når du bruker bookingformularen kan det behandles opplysninger som navn, e-postadresse, telefonnummer, ønsket fotografering, dato, sted, antall personer eller dyr og informasjon du selv skriver i meldingsfeltet.</p>
      <p>Formålet er å kunne svare på forespørselen, avklare pris og tilgjengelighet, planlegge fotograferingen og eventuelt inngå eller oppfylle en avtale. Behandlingen bygger normalt på at opplysningene er nødvendige for tiltak før avtale eller for å oppfylle en avtale.</p>
      <p>Bookingformularen sendes via Formspree. Ikke skriv sensitive eller unødvendige personopplysninger i fritekstfeltet.</p>
    </section>

    <section class="section">
      <h2>3. Privatgalleri og betaling</h2>
      <p>Når et fotooppdrag gjennomføres kan kundens kontaktopplysninger og informasjon knyttet til oppdraget brukes for levering, privatgalleri, betaling og kundedialog. Privatgalleri og betaling knyttet til bildefremvisning håndteres gjennom FotoSky etter det avtalte betalingsløpet.</p>
      <p>Opplysninger som må oppbevares på grunn av regnskaps-, dokumentasjons- eller andre lovkrav lagres så lenge loven krever det.</p>
    </section>

    <section class="section">
      <h2>4. Google Analytics – bare med samtykke</h2>
      <p>Fotograf Spalder bruker Google Analytics for å forstå hvilke sider som besøkes og hvordan nettsiden brukes. Dette kan blant annet omfatte informasjon om sidevisninger, nettleser/enhet, tekniske opplysninger og omtrentlig geografisk informasjon.</p>
      <p><strong>Google Analytics lastes ikke inn før du aktivt velger «Tillat analyse».</strong> Hvis du velger «Kun nødvendige», blir Google Analytics ikke aktivert.</p>
      <p>Du kan når som helst trekke tilbake eller endre valget ved å trykke på «Personvernvalg» nederst på nettsiden eller knappen under.</p>
      <button class="button primary" type="button" data-open-privacy-settings>Endre analysevalg</button>
    </section>

    <section class="section">
      <h2>5. Informasjonskapsler og lokal lagring</h2>
      <div class="table-wrap">
        <table class="privacy-table">
          <thead>
            <tr><th>Teknologi</th><th>Formål</th><th>Når brukes den?</th></tr>
          </thead>
          <tbody>
            <tr><td><code>fotografSpalderConsentV1</code> i lokal lagring</td><td>Husker om du har tillatt eller avslått analyse, slik at valget ikke må gjentas på hver side.</td><td>Nødvendig for å huske personvernvalget.</td></tr>
            <tr><td>Google Analytics, blant annet <code>_ga</code> og <code>_ga_*</code></td><td>Måling av bruk og statistikk for nettsiden.</td><td>Kun etter aktivt samtykke. Levetid styres av Google Analytics og nettleserinnstillinger.</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2>6. Tjenesteleverandører</h2>
      <p>For å drifte nettsiden og levere tjenestene brukes eksterne leverandører. Relevante leverandører kan blant annet være:</p>
      <ul>
        <li>GitHub Pages – publisering og hosting av nettsiden.</li>
        <li>Formspree – overføring av bookingforespørsler fra nettskjemaet.</li>
        <li>Google Analytics – valgfri besøksstatistikk etter samtykke.</li>
        <li>FotoSky – privat kundegalleri og tilknyttet betalingsflyt.</li>
      </ul>
      <p>Leverandører kan behandle opplysninger i andre land. Dersom personopplysninger overføres utenfor EØS, skal dette skje på et gyldig overføringsgrunnlag etter gjeldende personvernregler.</p>
    </section>

    <section class="section">
      <h2>7. Hvor lenge lagres opplysningene?</h2>
      <p>Opplysninger lagres ikke lenger enn nødvendig for formålet de ble samlet inn for. En vanlig bookingforespørsel beholdes så lenge det er nødvendig for å svare og følge opp forespørselen. Opplysninger knyttet til et gjennomført kundeoppdrag kan beholdes så lenge det er nødvendig for kundedialog, levering, dokumentasjon, rettskrav og lovpålagte plikter.</p>
    </section>

    <section class="section">
      <h2>8. Dine rettigheter</h2>
      <p>Avhengig av situasjonen kan du ha rett til innsyn, retting, sletting, begrensning, dataportabilitet og å protestere mot behandling. Når behandlingen bygger på samtykke, kan samtykket trekkes tilbake.</p>
      <p>Kontakt Fotograf Spalder på <a href="mailto:fotograf.spalder@outlook.com">fotograf.spalder@outlook.com</a> dersom du ønsker å bruke rettighetene dine eller har spørsmål om personvern.</p>
      <p>Du kan også klage til <a href="https://www.datatilsynet.no/" target="_blank" rel="noopener noreferrer">Datatilsynet</a>.</p>
    </section>

    <section class="section">
      <h2>9. Endringer i erklæringen</h2>
      <p>Personvernerklæringen kan oppdateres dersom nettsiden, leverandørene eller behandlingen av personopplysninger endres. Datoen øverst viser siste vesentlige oppdatering.</p>
    </section>

    <div class="actions">
      <a class="button primary" href="booking.html">Til booking</a>
      <a class="button" href="index.html">Til forsiden</a>
      <button class="button" type="button" data-open-privacy-settings>Personvernvalg</button>
    </div>
  </main>

  <footer class="footer">
    <div class="container">Fotograf Spalder · Personvern og informasjonskapsler</div>
  </footer>
</body>
</html>
'''

GA_BLOCK_PATTERNS = [
    re.compile(
        r'\s*(?:<!--\s*(?:Google tag \(gtag\.js\)|Google Analytics)\s*-->\s*)?'
        r'<script[^>]*src=["\']https://www\.googletagmanager\.com/gtag/js\?id=G-FHTXJM4638["\'][^>]*></script>\s*'
        r'<script>\s*window\.dataLayer\s*=\s*window\.dataLayer\s*\|\|\s*\[\];\s*'
        r'(?:function\s+gtag\(\)\s*\{dataLayer\.push\(arguments\);\}|function\s+gtag\(\)\{dataLayer\.push\(arguments\);\})\s*'
        r"gtag\('js',\s*new Date\(\)\);\s*gtag\('config',\s*'G-FHTXJM4638'\);\s*</script>\s*",
        re.S,
    ),
]


def remove_direct_analytics(html: str) -> str:
    updated = html
    for pattern in GA_BLOCK_PATTERNS:
        updated = pattern.sub('\n', updated)
    return updated


def ensure_consent_script(html: str) -> str:
    if 'src="samtykke.js"' in html or "src='samtykke.js'" in html:
        return html
    return html.replace('</head>', '  <script src="samtykke.js" defer></script>\n</head>', 1)


def add_booking_privacy_notice(html: str) -> str:
    marker = '<!-- BOOKING_PRIVACY_NOTICE -->'
    if marker in html or '<form id="bookingForm">' not in html:
        return html

    notice = '''    <!-- BOOKING_PRIVACY_NOTICE -->
    <div class="status-box">
      <strong>Personvern:</strong><br>
      Opplysningene du sender inn brukes for å svare på bookingforespørselen og planlegge et eventuelt fotooppdrag. Skjemaet sendes via Formspree. <a href="personvern.html">Les personvernerklæringen</a>.
    </div>

'''
    return html.replace('    <form id="bookingForm">', notice + '    <form id="bookingForm">', 1)


def update_html_pages():
    for path in ROOT.glob('*.html'):
        if path.name == PRIVACY_PAGE:
            continue
        html = path.read_text(encoding='utf-8')
        html = remove_direct_analytics(html)
        html = ensure_consent_script(html)
        if path.name == 'booking.html':
            html = add_booking_privacy_notice(html)
        path.write_text(html, encoding='utf-8', newline='\n')


def update_sitemap():
    sitemap_path = ROOT / 'sitemap.xml'
    if not sitemap_path.exists():
        return
    sitemap = sitemap_path.read_text(encoding='utf-8')
    if 'https://www.fotograf-spalder.com/personvern.html' in sitemap:
        return
    block = '''
  <url>
    <loc>https://www.fotograf-spalder.com/personvern.html</loc>
    <lastmod>2026-08-25</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>

'''
    sitemap = sitemap.replace('</urlset>', block + '</urlset>')
    sitemap_path.write_text(sitemap, encoding='utf-8', newline='\n')


def validate():
    problems = []
    for path in ROOT.glob('*.html'):
        html = path.read_text(encoding='utf-8')
        if 'www.googletagmanager.com/gtag/js' in html:
            problems.append(f'{path}: laster Google Analytics direkte')
        if 'src="samtykke.js"' not in html and "src='samtykke.js'" not in html:
            problems.append(f'{path}: mangler samtykke.js')

    booking = (ROOT / 'booking.html').read_text(encoding='utf-8')
    if '<!-- BOOKING_PRIVACY_NOTICE -->' not in booking:
        problems.append('booking.html: mangler kontekstuell personverninfo')

    consent = (ROOT / CONSENT_SCRIPT).read_text(encoding='utf-8')
    if 'Google Analytics lastes ikke inn før' not in consent:
        problems.append('samtykke.js: forventet samtykketekst mangler')

    if problems:
        raise SystemExit('\n'.join(problems))


(ROOT / CONSENT_SCRIPT).write_text(CONSENT_JS, encoding='utf-8', newline='\n')
(ROOT / PRIVACY_PAGE).write_text(PRIVACY_HTML, encoding='utf-8', newline='\n')
update_html_pages()
update_sitemap()
validate()
print('Personvern, samtykke og Google Analytics er oppdatert og validert.')
