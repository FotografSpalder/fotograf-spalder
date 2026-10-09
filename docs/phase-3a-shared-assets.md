# Fase 3a – felles JavaScript og CSS-grunnlag

Dato: 6. september 2026. Bygger på fase 2, draft-PR #4.

## Resultat

Alle 12 statiske sider laster nå `assets/js/site.js` og `assets/css/site.css`. Mobilmenyen som var kopiert på sju sider, årstallsoppdateringen og de identiske fanekontrollene fra pris- og portfoliosiden er samlet i ett nettstedsskript. Bookingens Formspree-kode er flyttet uendret i funksjon til `assets/js/booking.js`.

Det finnes ikke lenger kjørbar inline-JavaScript i sidene. JSON-LD forblir inline fordi det er strukturerte data, ikke programkode. `samtykke.js` forblir en egen felles modul og lastes fortsatt med `defer` på alle sider.

Den felles CSS-filen inneholder foreløpig den identiske focus-visible-regelen som var kopiert på sju sider. Regelen er fjernet fra disse inline-stilblokkene. På de øvrige sidene gjør selektoren ingenting med mindre de samme navigasjonselementene finnes. CSS-konsolideringen fortsetter i neste, separat gjennomgåbare endring; denne fasen påstår ikke at all felles CSS allerede er flyttet.

## Bevaring av oppførsel

- Mobilmenyen initialiseres lukket, oppdaterer `aria-expanded`, etikett og synlig tekst, lukkes ved lenkevalg og Escape, og returnerer fokus til menyknappen.
- Faner beholder klikk, høyre/venstre pil, Home, End, `aria-selected`, `tabIndex`, skjuling av paneler og valgfri fokusflytting.
- Booking bruker fortsatt `POST`, FormData, `Accept: application/json`, samme Formspree-endepunkt, valgfri gtag-hendelse, redirect til `takk.html` ved suksess og eksisterende feiltekst/reaktivering ved feil.
- Analyse lastes fortsatt bare av `samtykke.js` etter aktivt samtykke.
- Ingen navigasjonslenker, footere, priser, bilder, SEO-URL-er eller synlige tekster er endret.

`site_audit.py` krever nå site.js og site.css på alle sider, booking.js på bookingsiden, og avviser ny kjørbar inline-JavaScript. Lokale ressursreferanser kontrolleres som før.

## Verifikasjon

Runtime-testene kjører den faktiske nye JavaScript-koden i en minimal DOM-modell og dekker årstall, menyåpning, lenkelukking, Escape/fokus, tab-klikk og tastaturnavigasjon. Booking testes fortsatt for suksess, HTTP-feil og nettverksfeil uten å sende et virkelig skjema. Samtykket testes for ukjent, avvist, godkjent, tilbakekalt og gjentatt valg samt blokkert localStorage.

Det statiske Astro-bygget, kontrollen av kommersielle data, audit-testene, runtime-testene, eksisterende kvalitetskontroll, den utvidede auditen og `git diff --check` skal bestå før en endring regnes som ferdig.

En lokal nettleserkontroll på desktop omfattet forsiden, bookingsiden, porteføljesiden og prissiden. Forsiden og bookingskjemaet beholdt layout og innhold. På porteføljesiden ble fanen «Natur og dyreliv» aktivert og viste riktig panel med 12 bilder. På prissiden ble fanen «Arrangement» aktivert og viste riktig panel og priser. I begge tilfeller fulgte synlig markering, `aria-selected` og panelinnhold hverandre. Analyse ble avvist i personvernvalget under kontrollen, og bookingskjemaet ble ikke sendt.

## Filendringer

Fasen opprettet `assets/js/site.js`, `assets/js/booking.js`, `assets/css/site.css` og denne rapporten. Den oppdaterte de 12 daværende sidekildene, runtime-testene, audit-koden og audit-testene. Etter Astro-cutover ligger sidekildene under `src/pages/`, mens de samme offentlige ressurs-URL-ene er bevart i `public/`.

Neste steg er fase 3b: flytte og konsolidere felles variabler, grunnstil, container, header/nav, knapper, kort, grid, typografi, footer og responsive regler med nettleserbasert før/etter-kontroll. Deretter følger autoritativ header/footer i fase 4.
