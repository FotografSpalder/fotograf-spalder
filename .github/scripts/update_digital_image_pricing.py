from pathlib import Path
import re

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Fant ikke forventet tekst: {label}')
    return text.replace(old, new, 1)


# Felles terminologi: ikke kall ferdigredigerte JPEG-filer "originalfiler".
terminology_files = [
    'priser.html',
    'booking.html',
    'kjaeledyrsfotograf-ringsaker.html',
    'familie-portrettfotograf-ringsaker.html',
    'bryllupsfotograf-ringsaker.html',
    'Konfirmasjon.html',
    'sommerfotografering.html',
]
for filename in terminology_files:
    text = read(filename)
    text = text.replace('originalfiler i full oppløsning', 'fulloppløselige ferdigredigerte JPEG-filer')
    text = text.replace('Originalfiler i full oppløsning', 'Fulloppløselige ferdigredigerte JPEG-filer')
    text = text.replace('originalfiler', 'fulloppløselige bilder')
    text = text.replace('Originalfiler', 'Fulloppløselige bilder')
    write(filename, text)


# 1) Hovedprissiden: eksakte FotoSky-priser, gratisfane og regel for komplett galleri.
path = 'priser.html'
text = read(path)
text = replace_once(
    text,
    '<strong>Flere bilder enn det som står inkludert i pakken, fulloppløselige ferdigredigerte JPEG-filer og hele galleriet kjøpes separat.</strong>',
    '<strong>Bildene som er inkludert i pakken velges uten ekstra kostnad. Flere bilder uten vannmerke og eventuell komplett digital pakke kjøpes separat i FotoSky.</strong>',
    'innledende bildeinformasjon',
)

old_extra = '''  <div class="card">
    <h2>Bilder som kjøpes separat</h2>
    <div class="separate-badge">Ikke inkludert utover antallet i valgt pakke</div>
    <ul>
      <li>Ekstra digitale bilder i høy kvalitet kan kjøpes i kundegalleriet</li>
      <li>Fulloppløselige bilder kan kjøpes separat</li>
      <li>Pakkepris for hele galleriet kan tilbys ved større bestillinger</li>
    </ul>
    <p class="small">Prisene for ekstra bilder vises i kundegalleriet etter fotograferingen.</p>
  </div>'''
new_extra = '''  <div class="card">
    <h2>Digitale bilder uten vannmerke</h2>
    <div class="separate-badge">Kjøpes i standardfanen i FotoSky utover antallet som følger med pakken</div>
    <ul>
      <li><strong>Mobil &amp; sosiale medier:</strong> 350 kr per bilde</li>
      <li><strong>Høyoppløselig digitalt bilde:</strong> 500 kr per bilde</li>
      <li><strong>Fulloppløselig ferdigredigert JPEG:</strong> 700 kr per bilde</li>
      <li><strong>Komplett digital pakke – hele det ferdigredigerte galleriet:</strong> 6 500 kr ved ordinære fotograferinger og mindre private oppdrag</li>
    </ul>
    <p class="card-note">Ved bryllup og større arrangementer avtales prisen for komplett galleri separat ut fra omfang og antall ferdigredigerte bilder.</p>
  </div>

  <div class="card">
    <h2>Gratis delingsbilder</h2>
    <div class="included-badge">Egen «Gratis bilder»-fane i FotoSky</div>
    <p>Utvalgte delingsbilder legges i en egen fane i privatgalleriet og kan lastes ned uten ekstra betaling. Disse har Fotograf Spalder-vannmerke og er laget for enkel deling på mobil og sosiale medier.</p>
    <p class="small">Bilder uten vannmerke ligger i standardfanen og følger prisene over.</p>
  </div>'''
text = replace_once(text, old_extra, new_extra, 'tilleggspriser')

old_share = '''  <div class="info-box">
    <h2>Hva er et lavoppløselig delingsbilde?</h2>
    <p>
      Etter fotograferingen kan du motta lavoppløselige delingsbilder med vannmerke. Disse passer til mobil, Facebook og sosiale medier, men er ikke ment for store utskrifter.
    </p>
  </div>'''
new_share = '''  <div class="info-box">
    <h2>Hvordan fungerer gratis delingsbilder?</h2>
    <p>
      Utvalgte bilder legges i en egen «Gratis bilder»-fane i FotoSky. De kan lastes ned uten ekstra betaling, har Fotograf Spalder-vannmerke og er beregnet for mobil og sosiale medier. Bilder uten vannmerke ligger i standardfanen og kjøpes etter prislisten over.
    </p>
  </div>'''
text = replace_once(text, old_share, new_share, 'gratis delingsbilder FAQ')

old_original = '''  <div class="info-box">
    <h2>Hva er en originalfil?</h2>
    <p>
      Fulloppløselige bilder leveres i full oppløsning uten nedskalering og passer best til store utskrifter og maksimal bildekvalitet. Disse kjøpes separat.
    </p>
  </div>'''
new_original = '''  <div class="info-box">
    <h2>Hva er et fulloppløselig ferdigredigert bilde?</h2>
    <p>
      Dette er en ferdigredigert JPEG-fil i maksimal levert oppløsning, uten vannmerke. Den passer best når du ønsker størst mulig fleksibilitet til utskrift og videre privat bruk. RAW-filer leveres ikke som en del av denne bildeprisen.
    </p>
  </div>'''
text = replace_once(text, old_original, new_original, 'fulloppløselig FAQ')

# Privat-arrangementer får tydelige bildepriser. Kommersielle arrangementer avtales separat.
event_marker = '<div id="event" class="section" role="tabpanel" aria-labelledby="tab-event" hidden>\n'
private_event_info = '''<div id="event" class="section" role="tabpanel" aria-labelledby="tab-event" hidden>
  <div class="card">
    <h2>Digitale bilder ved private arrangementer</h2>
    <p>For bryllup, konfirmasjon, dåp og andre private oppdrag kan ekstra bilder uten vannmerke kjøpes i FotoSky:</p>
    <ul>
      <li>Mobil &amp; sosiale medier: 350 kr per bilde</li>
      <li>Høyoppløselig digitalt bilde: 500 kr per bilde</li>
      <li>Fulloppløselig ferdigredigert JPEG: 700 kr per bilde</li>
    </ul>
    <p class="card-note">Komplett digital pakke koster 6 500 kr ved ordinære fotograferinger og mindre private oppdrag. Ved bryllup og større arrangementer avtales komplett galleri separat ut fra omfang og antall ferdigredigerte bilder.</p>
    <p class="small">Utvalgte vannmerkede delingsbilder kan lastes ned gratis fra egen «Gratis bilder»-fane.</p>
  </div>

  <div class="card">
    <h2>Kultur, organisasjon og kommersiell bruk</h2>
    <p>Ved oppdrag for bedrift, organisasjon, presse, kulturarrangement eller annen kommersiell bruk avtales antall bilder, leveransepris og bruksrettigheter skriftlig ut fra oppdragets formål.</p>
  </div>
'''
text = replace_once(text, event_marker, private_event_info, 'arrangementspriser')
write(path, text)


# 2) Familie/portrett: vis hele standardprisen uten at kunden må gå til prissiden.
path = 'familie-portrettfotograf-ringsaker.html'
text = read(path)
old = '''        <div class="info-box" style="margin-top:1rem"><p><strong>Flere bilder enn det som er inkludert i pakken kjøpes separat.</strong> Se <a href="priser.html" style="color:#fde68a;font-weight:800;">full og oppdatert prisliste</a> før booking.</p></div>'''
new = '''        <div class="info-box" style="margin-top:1rem">
          <h3>Flere bilder og komplett galleri</h3>
          <p>Bildene som følger med pakken velges uten ekstra kostnad. Ønsker du flere bilder uten vannmerke, gjelder disse prisene i FotoSky:</p>
          <ul>
            <li>Mobil &amp; sosiale medier: <strong>350 kr per bilde</strong></li>
            <li>Høyoppløselig digitalt bilde: <strong>500 kr per bilde</strong></li>
            <li>Fulloppløselig ferdigredigert JPEG: <strong>700 kr per bilde</strong></li>
            <li>Komplett digital pakke – hele det ferdigredigerte galleriet: <strong>6 500 kr</strong></li>
          </ul>
          <p>Utvalgte delingsbilder med Fotograf Spalder-vannmerke legges i egen «Gratis bilder»-fane og kan lastes ned uten ekstra betaling.</p>
          <p><a href="priser.html" style="color:#fde68a;font-weight:800;">Se full prisliste og vilkår</a>.</p>
        </div>'''
text = replace_once(text, old, new, 'familie/portrett bildepriser')
write(path, text)


# 3) Kjæledyr: rett gammel "web-bilde"-tekst og legg inn standardprisene.
path = 'kjaeledyrsfotograf-ringsaker.html'
text = read(path)
text = text.replace('1 digitalt web-bilde inkludert', '1 digitalt bilde i høy kvalitet uten vannmerke inkludert')
text = text.replace('3 digitale web-bilder inkludert', '3 digitale bilder i høy kvalitet uten vannmerke inkludert')
text = text.replace('5 digitale web-bilder inkludert', '5 digitale bilder i høy kvalitet uten vannmerke inkludert')
old = '''        <div class="hero-actions" style="margin-top: 2rem;">
          <a class="button primary" href="booking.html">Book fotografering</a>
          <a class="button secondary" href="priser.html">Se full prisliste</a>
        </div>'''
new = '''        <div class="info-box" style="margin-top:2rem;">
          <h3>Flere digitale bilder</h3>
          <p>Bildene som følger med valgt kjæledyrspakke velges uten ekstra kostnad. Flere bilder uten vannmerke kjøpes i FotoSky:</p>
          <ul class="check-list">
            <li>Mobil &amp; sosiale medier: <strong>350 kr per bilde</strong></li>
            <li>Høyoppløselig digitalt bilde: <strong>500 kr per bilde</strong></li>
            <li>Fulloppløselig ferdigredigert JPEG: <strong>700 kr per bilde</strong></li>
            <li>Komplett digital pakke – hele det ferdigredigerte galleriet: <strong>6 500 kr</strong></li>
          </ul>
          <p>Utvalgte delingsbilder med vannmerke ligger i egen «Gratis bilder»-fane og kan lastes ned uten ekstra betaling.</p>
        </div>

        <div class="hero-actions" style="margin-top: 2rem;">
          <a class="button primary" href="booking.html">Book fotografering</a>
          <a class="button secondary" href="priser.html">Se full prisliste</a>
        </div>'''
text = replace_once(text, old, new, 'kjæledyr bildepriser')
text = text.replace('Noen bilder er inkludert i pakken, og flere bilder eller fulloppløselige bilder kan kjøpes separat.', 'Noen bilder er inkludert i pakken. Flere bilder uten vannmerke kan kjøpes for 350, 500 eller 700 kr per bilde, og komplett digital pakke koster 6 500 kr.')
write(path, text)


# 4) Bryllup: stykkpriser er faste, men komplett galleri prises separat.
path = 'bryllupsfotograf-ringsaker.html'
text = read(path)
insert_before = '''    <section>
      <div class="container">
        <div class="section-head"><h2>Slik fungerer betaling og levering</h2></div>'''
price_section = '''    <section>
      <div class="container">
        <div class="section-head"><h2>Pris på flere bryllupsbilder</h2><p class="lead">Dere kan se prisene før booking og trenger ikke be om et eget prisoverslag for enkeltbilder.</p></div>
        <div class="info-box">
          <ul>
            <li>Mobil &amp; sosiale medier uten vannmerke: <strong>350 kr per bilde</strong></li>
            <li>Høyoppløselig digitalt bilde uten vannmerke: <strong>500 kr per bilde</strong></li>
            <li>Fulloppløselig ferdigredigert JPEG uten vannmerke: <strong>700 kr per bilde</strong></li>
          </ul>
          <p><strong>Komplett bryllupsgalleri:</strong> prisen avtales separat ut fra hvor stor del av dagen som fotograferes og hvor mange ferdigredigerte bilder galleriet inneholder. Den faste komplette galleri-pakken på 6 500 kr gjelder ordinære fotograferinger og mindre private oppdrag, ikke større bryllupsgallerier.</p>
          <p>Utvalgte vannmerkede delingsbilder legges i egen «Gratis bilder»-fane i FotoSky og kan lastes ned uten ekstra betaling.</p>
        </div>
      </div>
    </section>

''' + insert_before
text = replace_once(text, insert_before, price_section, 'bryllup bildepriser')
text = text.replace('Bryllupspakken inkluderer 8 ferdigredigerte digitale bilder i høy kvalitet. Flere bilder kan kjøpes separat etter at galleriet er åpnet.', 'Bryllupspakken inkluderer 8 ferdigredigerte digitale bilder i høy kvalitet. Flere bilder koster 350, 500 eller 700 kr per bilde avhengig av filtype. Pris for komplett bryllupsgalleri avtales etter omfang.')
write(path, text)


# 5) Konfirmasjon: vis pakkepris og tillegg direkte på siden.
path = 'Konfirmasjon.html'
text = read(path)
insert_before = '''    <section>
      <div class="container">
        <div class="cta-box">
          <h2>Ønsker dere fotograf til konfirmasjonen?</h2>'''
konf_prices = '''    <section>
      <div class="container">
        <div class="section-head">
          <h2>Pris og flere digitale bilder</h2>
          <p class="lead">Konfirmasjonsfotografering starter fra 3 000 kr og inkluderer 2 ferdigredigerte digitale bilder i høy kvalitet uten vannmerke.</p>
        </div>
        <div class="card highlight">
          <h3>Bilder utover de 2 inkluderte</h3>
          <ul>
            <li>Mobil &amp; sosiale medier uten vannmerke: <strong>350 kr per bilde</strong></li>
            <li>Høyoppløselig digitalt bilde uten vannmerke: <strong>500 kr per bilde</strong></li>
            <li>Fulloppløselig ferdigredigert JPEG uten vannmerke: <strong>700 kr per bilde</strong></li>
            <li>Komplett digital pakke ved ordinær konfirmant-/portrettfotografering: <strong>6 500 kr</strong></li>
          </ul>
          <p>Hvis oppdraget omfatter større deler av selve feiringen som et større arrangement, avtales pris for komplett galleri separat ut fra omfang og antall ferdigredigerte bilder.</p>
          <p>Utvalgte bilder med Fotograf Spalder-vannmerke kan lastes ned gratis fra egen «Gratis bilder»-fane i FotoSky.</p>
        </div>
      </div>
    </section>

''' + insert_before
text = replace_once(text, insert_before, konf_prices, 'konfirmasjon bildepriser')
write(path, text)


# 6) Booking: behold skjemaet enkelt, men gjør bildeprisene synlige før innsending.
path = 'booking.html'
text = read(path)
old = '''    <div class="notice">
      <strong>Viktig om pris og bilder:</strong><br>
      Prisen du velger under gjelder fotograferingsoppdraget og inkluderer kun det antallet digitale bilder som står oppført på <a href="priser.html">pris-siden</a>.
      Flere digitale bilder, fulloppløselige bilder og eventuelle bildeprodukter kjøpes separat etter at du har sett bildene i ditt private nettgalleri.
    </div>'''
new = '''    <div class="notice">
      <strong>Viktig om pris og bilder:</strong><br>
      Prisen du velger under gjelder fotograferingsoppdraget og inkluderer kun det antallet digitale bilder som står oppført på <a href="priser.html">pris-siden</a>.
      Ekstra bilder uten vannmerke koster 350 kr for mobil/sosiale medier, 500 kr i høy oppløsning eller 700 kr som fulloppløselig ferdigredigert JPEG. Komplett digital pakke koster 6 500 kr ved ordinære fotograferinger og mindre private oppdrag. Ved bryllup og større arrangementer avtales komplett galleri separat.
      Utvalgte vannmerkede delingsbilder kan lastes ned gratis fra egen «Gratis bilder»-fane i FotoSky.
    </div>'''
text = replace_once(text, old, new, 'booking bildepriser')
write(path, text)


# 7) Oppdater sitemap-dato for sidene som faktisk endres i denne runden.
path = 'sitemap.xml'
text = read(path)
for page in [
    'priser.html',
    'booking.html',
    'bryllupsfotograf-ringsaker.html',
    'familie-portrettfotograf-ringsaker.html',
    'Konfirmasjon.html',
    'kjaeledyrsfotograf-ringsaker.html',
]:
    pattern = re.compile(rf'(<loc>https://www\.fotograf-spalder\.com/{re.escape(page)}</loc>\s*<lastmod>)[^<]+(</lastmod>)')
    text, count = pattern.subn(r'\g<1>2026-08-25\g<2>', text, count=1)
    if count != 1:
        raise SystemExit(f'Fant ikke sitemap-rad for {page}')
write(path, text)

print('Digitale bildepriser og galleri-regler er oppdatert.')
