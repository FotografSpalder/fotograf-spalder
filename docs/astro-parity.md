# Astro-paritet og produksjonsstatus

Astro-cutoveren er produksjonsverifisert og godkjent. Astro er eneste autoritative nettstedssystem. `astro.config.mjs` bygger statiske filer med nettstedets eksisterende domene og `build.format: 'file'`.

## Bevarte produksjonskontrakter

Alle 12 offentlige ruter ligger under `src/pages/` og bygges med de samme filnavnene som før, inkludert `Konfirmasjon.html` og `takk.html`. Eksisterende HTML-struktur, klasser, stilblokker, synlige tekster, metadata og offentlige URL-er er bevart.

`src/lib/services.ts` inneholder typesikker modell, validering og formatteringshjelpere. `data/services.json` er eneste kilde for priser, pakker, bildeantall, betalingsregler, bookingvilkår og avledede prisintervaller. De kommersielle mutasjonstestene bygger reelle Astro-sider og kontrollerer at endringer slår gjennom i priser, booking, landingssider og JSON-LD.

Statiske filer i `public/` beholder de offentlige URL-ene. Dette gjelder også `assets/js/site.js`, `assets/js/booking.js`, `samtykke.js`, `assets/css/site.css`, bilder, `robots.txt`, `sitemap.xml` og `CNAME`.

## Kontrollgrunnlag

`.github/site-baseline.json` låser den gjennomgåtte produksjonskontrakten for title, meta description, canonical, Open Graph, robots, JSON-LD, bookingfelt, kommersielt innhold og skjema. `site_audit.py` og `site_quality.py` leser `dist/`. Runtime-testene bruker de faktiske JavaScript-filene og sender ingen ekte Formspree-booking.

Den godkjente paritetsfasen dokumenterte samme 12 ruter, SEO, kommersielle data, lokale ressurser og brukerflyt. Oppryddingen etter cutover skal derfor gi identisk `dist/`; overgangsarkitekturen er ikke lenger en sammenligningskilde.

## Avgrensninger

Oppryddingen endrer ikke komponentstruktur, CSS, bilder, metadata, URL-er, Formspree, samtykke, Analytics eller GitHub Pages-oppsett. Manglende `og:image` på `personvern.html`, metadata på `takk.html`, Actions-varsler og `Meg.jpg`/`meg.jpg` håndteres eventuelt i egne senere faser.
