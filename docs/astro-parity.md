# Astro-paritet – første migreringsetappe

## Avgrensning

Denne etappen flytter den statiske produksjonsbyggingen til Astro 7.3.1 uten React, Vue, Svelte eller andre UI-rammeverk. Arbeidet er en paritetsmigrering. Navigasjon, design, priser, forretningsregler, bildearkitektur, offentlige URL-er og GitHub Pages-deploy er ikke endret.

`astro.config.mjs` bruker statisk output, nettstedets eksisterende domene og `build.format: 'file'`. HTML-komprimering er slått av fordi mellomrommene i dagens HTML inngår i den autoritative semantiske sammenligningen.

## Porterede sider

Alle 12 autoritative HTML-sider har en tilsvarende Astro-side under `src/pages/`:

- `index.html`
- `priser.html`
- `booking.html`
- `portfolio.html`
- `kjaeledyrsfotograf-ringsaker.html`
- `familie-portrettfotograf-ringsaker.html`
- `bryllupsfotograf-ringsaker.html`
- `Konfirmasjon.html`
- `sommerfotografering.html`
- `om.html`
- `personvern.html`
- `takk.html`

Den eksisterende HTML-strukturen, klassene og sidens egne stilblokker er beholdt i første pass. `Konfirmasjon.html` beholder nøyaktig samme filnavn og innholdsstruktur. Den er ikke normalisert.

## Data og kommersielle regler

`data/services.json` bruker schema v2. Generelle `{{ ... }}`-uttrykk er fjernet fra datakilden. Dynamisk pakkeinnhold bruker et lite, eksplisitt sett med typer for inkluderte bilder, innholdsreferanser og varighet. Bookingvilkårene bruker navngitte regeltyper.

`src/lib/services.ts` inneholder den typesikre modellen, valideringen og formatteringshjelperne for priser, bildeantall, pakkeinnhold, bookingvilkår og avledede prisintervaller. Samme regler finnes midlertidig i Python-generatoren slik at den fortsatt kan bygge og kontrollere den autoritative Fase 3a-utgaven under overgangen.

## Statiske filer

Aktive bilder, `site.css`, `site.js`, `booking.js`, `samtykke.js`, `CNAME`, `robots.txt` og `sitemap.xml` ligger under `public/`. Astro kopierer dem uten navneendringer, slik at alle offentlige URL-er er de samme.

Den eksisterende Windows-kollisjonen mellom de sporede filene `Meg.jpg` og `meg.jpg` er ikke endret. Ingen av dem er i aktiv bruk på nettstedet, og begge håndteres fortsatt som kjent overgangsgjeld.

## Paritetskontroll

`scripts/compare_astro_output.py` sammenligner `dist/` mot de autoritative rotfilene på:

- ruteinventar og eksakte `.html`-navn
- title, meta description, robots, canonical og Open Graph
- JSON-LD
- kommersielle tekster, priser, inkluderte bildeantall og betalingsregler
- bookingalternativer, felt og Formspree-relatert struktur
- navigasjon og footer
- bilderekkefølge og bildeattributter
- lokale assetreferanser
- CSS-regler, variabler og media queries
- `CNAME`, `robots.txt` og `sitemap.xml`

Resultat: alle 12 ruter og 279 lokale referanser er semantisk identiske med Fase 3a-autoriteten. `takk.html` er fortsatt `noindex, nofollow` og er ikke med i sitemap. Audit rapporterer de samme 44 kjente gjeldsfunnene som før og ingen nye regresjoner.

## Tester

- Astro check: 0 feil, 0 advarsler, 0 tips.
- Astro build: 12 statiske sider bygget til `dist/`.
- Eksisterende Python-kontroller: 36 tester bestått.
- Nye Astro-tester: schema v2, full kommersiell mutasjon og ugyldige betalingsprosenter bestått.
- JavaScript: samtykke, mobilmeny, faner, årstall og bookingens suksess-/feilflyt bestått uten reell innsending.
- Sidekvalitet og audit mot `dist/`: bestått, ingen nye regresjoner.
- `git diff --check`: bestått.

## Lokal nettleserkontroll

Microsoft Edge ble kjørt mot en lokal server med bred visning på 1440 × 1000 og mobil visning på 390 × 844. Følgende ble kontrollert:

- forside
- priser
- bookingfelt og uendret Formspree-endepunkt, uten innsending
- portefølje og bytte til familiefanen
- kjæledyrsiden
- om-siden
- mobilmeny, inkludert lukking med Escape
- samtykkedialog, avvisning og blokkert Analytics-lasting

Alle sidene svarte med 200, hadde forventet title, lastet aktive assets uten lokale HTTP-feil og hadde 0 piksler horisontal overflow i de testede visningene. Rapport og skjermbilder ligger i `outputs/astro-parity-browser-qa` utenfor repositoryet.

## Avvik og overgangsløsning

Det finnes ingen påviste produksjonsavvik i de kontrollerte egenskapene. Astro-kilden for `portfolio.html` har én eksplisitt avsluttende `div` som den gamle nettleserparseren la til automatisk for den ufullstendige HTML-en. Dette gir samme ferdige DOM og gjør kilden gyldig for Astro.

Følgende beholdes med vilje som overgangsløsning:

- Python-generatoren og `templates/pages/`
- de 12 autoritative rotfilene
- dobbel implementasjon av formatteringsreglene i Python og TypeScript
- eksisterende sidevise CSS-blokker
- eksisterende `site.js`, `booking.js` og `samtykke.js`
- eksisterende bildeoppsett og filnavn
- dagens GitHub Pages-deploy

## Klar for neste Astro-fase

Astro kan nå bygge en verifisert produksjonskopi fra schema v2. Neste fase kan derfor gjøre Pages-cutover som en egen, reverserbar endring. Etter at den publiserte Astro-utgaven er kontrollert, kan Python-generatoren og rot-HTML-en fjernes. Større komponentisering, CSS-konsolidering og eventuell bildeopprydding bør fortsatt behandles som separate faser med samme audit som sikkerhetsnett.
