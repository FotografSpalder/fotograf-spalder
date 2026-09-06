# Fase 1 – kartlegging og sikkerhetsnett

Dato: 6. september 2026. Repo: FotografSpalder/fotograf-spalder.
Kontrollert kildecommit: `010de7af5271a3eda3399ece97d49317104a479b`.

## Omfang og status

Dette er første kontrollerte endring, ikke en ferdig gjennomføring av fase 2–12. Produksjonssidene, samtykke.js, bilder, priser, URL-er og bookingkode er uendret. Fase 1 legger til kartlegging, eksplisitt registrering av eksisterende teknisk gjeld og regresjonstester. Ingen produksjonsdeploy eller omskriving av Git-historikk utført.

## Hva som faktisk finnes

12 HTML-sider; 11 indekserbare URL-er og takk.html med noindex. Ingen frontendpakker, eksterne CSS-filer eller build-system. Én ekstern JavaScript-fil (samtykke.js) og 10 kjørbare inline-skript. To Actions: teknisk kvalitetskontroll og JPEG-optimalisering. GitHub Pages-domenet i CNAME er www.fotograf-spalder.com; canonicals bruker også www. DNS, faktisk Pages-konfigurasjon og produksjonsnettverk er ikke verifisert.

Alle HTML-sider har innebygd CSS. Tabellen viser UTF-8-byte i style-blokker, kjørbare inline-skript, img-forekomster og hvilke som oppgir begge dimensjoner. Bakgrunnsbilder inngår i den separate referanselisten.

| Side | CSS-byte | Inline JS | img | Med dimensjoner | Navlenker | Footer |
|---|---:|---:|---:|---:|---:|---:|
| `Konfirmasjon.html` | 7464 | 1 | 3 | 0 | 6 | 1 |
| `booking.html` | 3835 | 1 | 0 | 0 | 0 | 0 |
| `bryllupsfotograf-ringsaker.html` | 5669 | 1 | 3 | 0 | 5 | 1 |
| `familie-portrettfotograf-ringsaker.html` | 5879 | 1 | 5 | 0 | 5 | 1 |
| `index.html` | 11973 | 1 | 7 | 2 | 10 | 1 |
| `kjaeledyrsfotograf-ringsaker.html` | 9191 | 1 | 5 | 0 | 7 | 1 |
| `om.html` | 8018 | 1 | 4 | 0 | 5 | 1 |
| `personvern.html` | 2098 | 0 | 0 | 0 | 0 | 1 |
| `portfolio.html` | 2585 | 1 | 37 | 19 | 0 | 0 |
| `priser.html` | 4931 | 1 | 0 | 0 | 0 | 0 |
| `sommerfotografering.html` | 6262 | 1 | 1 | 1 | 5 | 1 |
| `takk.html` | 3390 | 0 | 0 | 0 | 0 | 0 |

Full filoversikt, metadata, kommersielle tekstforekomster med linjenummer, bildeattributter, CSS-regler og samtlige lokale referanser finnes i `site-inventory.json` levert sammen med rapporten. CI genererer samme type rapport som artefakt.

## Forretningsdata og konsistens

Priser.html er foreløpig autoritativ. Gjennomgåtte bookingvalg samsvarer med prissiden for pris, fra-/intervallpris og antall inkluderte bilder. De relevante tjenestesidene viser samme beløp og antall; eksisterende JSON-LD er kartlagt og låst i kontrollgrunnlaget. Ingen sikker numerisk konflikt er funnet i denne sammenligningen. Det finnes semantiske forskjeller og overlappende formuleringer som ikke skal normaliseres blindt.

| Pakke | Pris i NOK | Inkluderte bilder |
|---|---:|---:|
| Kjæledyr Mini | 1 800 | 1 |
| Kjæledyr Standard | 3 000 | 3 |
| Kjæledyr Premium | 4 000 | 5 |
| Portrett | 1 500 | 1 |
| Familiefoto | 2 500 | 2 |
| Grunnpakke | 3 200 | 3 |
| Favorittpakke | 4 500 | 5 |
| Totalpakke | 8 000 | 10 |
| Bryllup | Fra 10 000 | 8 |
| Konfirmasjon | Fra 3 000 | 2 |
| Dåp | Fra 3 000 | 2 |
| Slektsfotografering | 7 500 | 5 |
| Kultur og arrangement, halv dag | Fra 4 000–7 000 | Avtales skriftlig |
| Kultur og arrangement, heldag | Fra 7 000–15 000 | Avtales skriftlig |
| Cosplay Grunnpakke | 1 200 | 1 |
| Cosplay Magipakke | 1 800 | 2 |
| Cosplay Epos | 2 800 | 3 |

Tillegg: ekstra person 300 kr; ekstra 30 minutter 500 kr; reise 5 kr/km over 2 mil fra Ringsaker; ekspressredigering innen 48 timer 500 kr. Digitale tillegg: 350/500/700 kr etter filtype. Komplett digital pakke 6 500 kr for ordinære fotograferinger og mindre private oppdrag. Bryllup og større arrangementer har separat avtalt komplett galleri; denne avgrensningen må modelleres uttrykkelig.

Betaling: 30 % forskudd etter godkjent booking, dato reservert først når betalingen er registrert. Forskuddet trekkes fra og refunderes ikke ved avbestilling. 70 % etter fotograferingen via FotoSky før galleriet åpnes. Tilleggskjøp kommer i tillegg. Levering normalt 1–3 uker. Bookingvilkårene sier minst 24 timers varsel ved avbestilling/endring, mulig forkorting/flytting ved over 15 minutters forsinkelse og ny time uten tillegg ved dårlig vær. Disse reglene er ikke endret eller juridisk vurdert.

Dupliseringskart:

- Kjæledyrpakker: priser.html, booking.html, kjæledyrsiden og dens JSON-LD.
- Portrett/familie og generelle pakker: priser.html, booking.html, familiesiden; JSON-LD har utvalgte tilbud.
- Bryllup: priser.html, booking.html, bryllupsiden og JSON-LD.
- Konfirmasjon: priser.html, booking.html og Konfirmasjon.html.
- Dåp, slekt, arrangement og cosplay: priser.html og booking.html.
- Digitale tillegg og 6 500 kr: priser.html flere steder, booking.html og fire tjenestesider.
- Betalingsregler: priser.html, booking.html, takk.html, familie- og bryllupsiden.
- Levering/vær: booking.html, Konfirmasjon.html, sommerfotografering.html og deler av kjæledyrsiden.

Fase 2 bør bruke et lite Python-build med data/services.json og enkle HTML-maler. Eksisterende HTML-URL-er kan beholdes. Dette gir tydelig gevinst uten Astro eller SPA. Datafilen bør inneholde tjeneste-ID, visningsnavn, pris/fra/intervall, antall bilder eller avtalt antall, pakkeinnhold, tillegg og eksplisitte unntak. Generer priskort, bookingvalg og tilbud i JSON-LD fra samme data. Baseline-filen i fase 1 er et kontrollgrunnlag og er IKKE denne sannhetskilden.

## CSS, navigasjon og footer

Gjennomgående identitet: mørk blå/svart bakgrunn, lys tekst, gyllen/oransje aksent, Arial/Helvetica, avrundede kort og pilleformede knapper. Variabler, body, container, header/nav, knapper, kort/grid, typografi, footer og responsive regler gjentas i inline CSS. Like selektorer har både reelle variasjoner og legitime media-overstyringer. De må sammenlignes i kaskaderekkefølge; likt navn er ikke alene grunn til sletting.

Index.html har AUGUST_GALLERY_MEDIA og MOBILE_LAYOUT_FIX_START/END; portfolio.html har AUGUST_GALLERY_MEDIA. Sommerfotografering.html har både MOBILE_LAYOUT_FIX og FULL_HERO_IMAGE. Sistnevnte fjerner den tidligere hero-bakgrunnen med cover, setter min-height til 0 og lar et img-element vise hele motivet med height:auto og object-fit:contain. Disse blokkene krever visuell kontroll før sammenslåing.

Forsidens hovednav har 10 lenker, kjæledyrsiden 7, Konfirmasjon 6 og flere andre 5. Om-siden har både Booking og Book fotografering til samme mål. Pris-, portfolio-, booking-, personvern- og takkesiden mangler nav-elementet; noen har enklere tilbake-/CTA-lenker. Footer finnes på 8 sider, med varierende personvernlenke og oppsett. Booking og takk kan begrunnes som egne fokuserte flyter, men ordinære sider bør få en felles grunnstruktur.

Forslag til neste fase: felles mal for header/footer, site.css for felles komponenter, små sidespesifikke regler og site.js for mobilmeny/årstall. Behold portfoliotabber og bookinglogikk som egne funksjoner. Samtykke.js er allerede delt og skal bevares bak aktivt samtykke.

## Bilder og filstruktur

Git-tree inneholder 104 bildefiler og 46.62 MiB bildedata. Det finnes 62 bildefiler i roten. 19 WebP-filer har JPEG-motparter under kattunger/natur. Ingen AVIF. 65 img-forekomster: 43 uten eksplisitte dimensjoner; 22 med dimensjoner og picture. Alle registrerte img har alt-attributt. Eksisterende alt/title-tekster er stedvis generiske eller repeterer fotograf/sted, særlig naturbildenes nummererte tekster; motivbeskrivelser bør gjennomgås manuelt senere.

To separate Git-blobs heter Meg.jpg og meg.jpg. Windows materialiserer bare én av dem; git status viser derfor en kunstig bildeendring i lokal kopi. Ingen av disse er referert av de kartlagte HTML/CSS-kildene. Bildene er ikke endret eller tatt med i fase 1-patchen. Fremtidig bildearbeid bør skje på et case-sensitivt filsystem eller etter en eksplisitt kontrollert navneopprydding.

Eksisterende optimizer behandler JPEG-er over 1 200 000 byte, begrenser lengste side til 2400, prøver kvalitet 86/82/78 og skriver over originalen hvis reduksjonen er over 5 %. Den beholder ICC når tilgjengelig, bruker EXIF-transponering og genererer ikke WebP/AVIF. Pillow installeres uversjonert med --upgrade. Workflowen skriver direkte til main, kjører ikke full nettsidekontroll, og gjenkjører ikke nødvendigvis ved alle stavemåter av bildeendelser. Dette bør endres i bildefasen; originaler og genererte varianter bør skilles, og generering bør være deterministisk med fast verktøyversjon.

Porteføljen har 37 aktive img-forekomster og kategoriene kjæledyr, konfirmasjon, familie, bryllup, cosplay og natur. Bilder finnes også i gallery.json for natur, men HTML er hardkodet. Behold nåværende utvalg; et kuratert manifest kan generere HTML uten å inkludere alle filene automatisk.

## URL-er, sesong og SEO

Alle 11 sitemap-URL-er beholdes, inkludert /Konfirmasjon.html og /sommerfotografering.html. Konfirmasjon.html skal ikke bare omdøpes: GitHub Pages støtter ikke vilkårlige serverredirects gjennom vanlig statisk HTML. Behold den indekserte URL-en inntil en separat migrering med kompatibel gammel URL og testet canonical/redirect er bestemt.

Forsiden viser fortsatt «Aktuelt i august» per 6. september. Det er et dokumentert sesongavvik. Ingen kampanjedatoer eller sesongkonfigurasjon finnes. Fase 9 bør innføre gyldighetsdatoer og skjule utløpt fremheving, med planlagt build slik at utløp faktisk får effekt. Behold landingssiden av SEO-hensyn. Sesonginnholdet er ikke endret i denne fase 1-leveransen.

Takk.html er riktig noindex og utelatt fra sitemap, men har ingen canonical. Det registreres som et eksisterende avvik fra den strenge generelle canonical-kontrollen, ikke som en påvist SEO-feil som må rettes på en noindex-side. Title/description finnes på alle 12 sider; eksisterende JSON-LD lar seg parse.

## Nytt sikkerhetsnett

site_audit.py bruker bare Python-standardbiblioteket. Det kontrollerer alle HTML-sider, ikke bare en hardkodet liste, og undersøker titler, beskrivelser, canonical, Open Graph-URL, sitemap, robots, CNAME, noindex, lokale lenker med fragment og eksakt casing, src/srcset, CSS-bilder, bilde-alt, dimensjoner, dupliserte ID-er, JSON-LD og store aktive bilder. Direkte Analytics-lasting i HTML og JS utenfor samtykke.js avvises; kjøretidstester kontrollerer samtykkemodulen separat.

Baseline-filen registrerer nøyaktig 43 dimensjonsmangler og én canonical-observasjon, samt navnekollisjonen. Nye feil og ekstra forekomster av en eksisterende feil stopper CI. Rettede avvik krever at tilhørende baseline-oppføring fjernes. Pris-/regeltekst, bookingvalg/skjemaattributter, metadata og JSON-LD sammenlignes mot den gjennomgåtte starten. Baseline skal bare oppdateres etter konkret gjennomgang; aldri automatisk for å få grønn CI. Etter fase 2 erstattes relevante kommersielle snapshots med tester mot den autoritative datafilen.

site-quality.yml kjøres nå også ved pull requests. Det kjører eksisterende kvalitetskontroll, den nye auditen, 19 mutasjonstester, runtime-tester for samtykke/booking og git diff --check. Rapporten lastes opp som CI-artefakt. Den eksisterende site_quality.py er beholdt som ekstra kontroll.

## Testresultater og grenser

- Eksisterende site_quality.py: bestått på uendret kilde.
- Ny audit: ingen nye regresjoner; 44 nøyaktig registrerte eksisterende observasjoner.
- 19 Python-tester: bestått, inkludert injiserte feil i lenker/casing/fragmenter/srcset, priser, obligatoriske skjemafelt, JSON-LD, ID-er, Analytics, alt/dimensjoner, store WebP-filer, metadata, sitemap, robots og domene.
- Samtykke: ukjent, avvist, godkjent, tilbakekalt, gjentatt godkjenning og blokkert localStorage testet med ekte samtykkekode i en minimal DOM-modell.
- Booking: vellykket respons, HTTP-feil og nettverksfeil testet med ekte inline-handler og mock av Formspree. Riktig endpoint, POST, FormData, status og redirect til takk.html kontrollert. Ingen ekte booking sendt.
- Ingen HTML, eksisterende JS, bilder, sitemap, robots eller CNAME endret i leveransen.
- Mobilresponsivitet er kartlagt gjennom CSS/media-regler. Ingen visuell nettlesertest eller skjermbildesammenligning gjennomført. DOM-modellen er ikke en full nettleser og verifiserer ikke layout eller tredjepartsnettverk.
- Ingen produksjonsdeploy, faktisk Formspree-levering, DNS-sjekk eller full HTML-standardvalidering utført. CI-resultat fra GitHub må skilles fra lokale testresultater.

## Repository-størrelse og videre steg

Nåværende tracked tree er 46.86 MiB. GitHub rapporterte repository size 468 340 KiB (omtrent 457 MiB). Det tyder på at historikk/lagring utgjør mye mer enn nåværende filer, men API-størrelsen er ikke en presis summering av gamle bilder. Kopien er shallow; største historiske blobs og andelen gamle bildeversjoner er derfor ikke fastslått. Ikke anslå differansen som dokumentert bildestørrelse. I fase 12 kan en separat mirror-kopi analyseres med rev-list --objects --all og cat-file --batch-check. Eventuell git filter-repo krever separat eksplisitt beslutning, sikkerhetskopi og koordinering av kloner.

Neste logiske steg er fase 2: migrere priser/regler til én strukturert kilde og generere dagens HTML-uttrykk. Deretter felles CSS/JS og navigasjon med visuelle før/etter-kontroller, før bilde-/sesongarbeid. Ingen større kommersiell avklaring er nødvendig for å starte datamodellen; bevar alle eksisterende unntak.

Største filer i nåværende tree:

| Fil | Byte |
|---|---:|
| `IMG_1165.jpg` | 1094070 |
| `IMG_0457.jpg` | 1053034 |
| `IMG_1006.jpg` | 1037887 |
| `IMG_1118.jpg` | 1013370 |
| `IMG_0362.jpg` | 944477 |
| `hund7.jpg` | 939731 |
| `IMG_1246.jpg` | 886857 |
| `IMG_0379.jpg` | 870652 |
| `konfirmant.jpg` | 840488 |
| `familie1.jpg` | 803820 |
| `IMG_0556.jpg` | 791709 |
| `konfirmasjon2.jpg` | 769807 |
| `IMG_0842.jpg` | 753962 |
| `IMG_1265.jpg` | 750095 |
| `familie2.jpg` | 700357 |

## Filendringer

Opprettet: `.github/scripts/site_audit.py`, `.github/scripts/test_site_audit.py`, `.github/scripts/test_runtime.cjs`, `.github/site-baseline.json`, `docs/phase-1-audit.md`. Endret: `.github/workflows/site-quality.yml`. Ingen eksisterende filer fjernet eller redusert.
