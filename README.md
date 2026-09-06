# Fotograf Spalder

Statisk nettsted for www.fotograf-spalder.com på GitHub Pages.

## Redigering og bygg

- Kommersielle data: `data/services.json`.
- HTML-kilder: `templates/pages/*.html.tmpl`.
- Generert nettsted: de eksisterende HTML-filene i roten. Rediger malene, ikke de genererte filene.

```text
python scripts/build_site.py
python scripts/build_site.py --check
python scripts/check_commercial.py
python -m unittest discover -s .github/scripts -p "test_*.py"
node .github/scripts/test_runtime.cjs
python .github/scripts/site_quality.py
python .github/scripts/site_audit.py
```

Bygget bruker Python 3.12+ uten tredjepartspakker. Node 22 brukes kun i tester. HTML sjekkes inn sammen med endringer i datakilde/maler, slik at eksisterende GitHub Pages-oppsett fortsatt kan publisere rotens statiske filer. CI kontrollerer at data, maler og generert HTML stemmer overens.

Ved tilsiktede endringer i priser, regler eller SEO må det gjennomgåtte testgrunnlaget også oppdateres. Ikke regenerer baseline automatisk for å skjule en testfeil. Se [datamodell, arbeidsflyt og begrensninger](docs/phase-2-business-data.md).

## Kartlegging

- [Fase 1: audit og sikkerhetsnett](docs/phase-1-audit.md)
- [Fase 2: kommersielle data og statisk generering](docs/phase-2-business-data.md)

Repoet har to historiske bildefiler med navnene `Meg.jpg` og `meg.jpg`. De kan ikke begge representeres riktig i en vanlig Windows-kopi. Ikke inkluder den kunstige bildeendringen fra dette i commits; bruk et case-sensitivt filsystem før arbeid på disse bildene.

