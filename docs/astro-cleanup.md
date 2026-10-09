# Opprydding etter Astro-cutover

Denne fasen fjerner overgangssystemet etter at Astro-cutoveren ble produksjonsverifisert og godkjent. Produksjonskontrakten er uendret.

## Fjernet overgangssystem

- Den midlertidige Python-byggeren og dens kommersielle kontroll/sammenligner under `scripts/`.
- Tolv `.html.tmpl`-filer under `templates/pages/`.
- Tolv tidligere genererte `.html`-filer i repository-roten.
- Den generator-spesifikke testen `.github/scripts/test_business_data.py`.

De slettede filene er listet nøyaktig i pull request-diffen. Ingen av dem inngår i GitHub Pages-artefakten; Actions bygger og publiserer `dist/` fra Astro.

## Beholdt testintensjon

`tests/commercial-mutations.test.mjs` tester kommersielle mutasjoner gjennom et faktisk Astro-bygg. Testen dekker pris- og bookingvisning, landingssider, JSON-LD, avledede prisintervaller, tillegg og unntak, betalingsregler, leveringstid, escaping, kildekontroll mot hardkodede tall og fail-closed-validering.

`.github/scripts/test_site_audit.py`, `.github/scripts/test_runtime.cjs`, `site_quality.py` og `site_audit.py` er beholdt. Kvalitets- og auditverktøyene leser `dist/` som standard. `.github/site-baseline.json` er fortsatt den gjennomgåtte produksjonskontrakten.

## Autoritativ struktur

- `src/pages/`, `src/lib/` og `src/components/` er nettstedskilden.
- `data/services.json` er den kommersielle datakilden.
- `public/` inneholder statiske filer med eksisterende offentlige URL-er.
- `dist/` er det eneste publiserbare nettstedet.

Oppryddingen skal verifiseres ved å sammenligne et komplett fil- og SHA-256-manifest av `dist/` før og etter endringen. Lik manifest betyr at sider, metadata, tekst, priser, JavaScript, CSS og ressurser er uendret på byte-nivå.
