# Fotograf Spalder

Statisk Astro-nettsted for www.fotograf-spalder.com på GitHub Pages. Astro er repositoryets og produksjonens eneste autoritative nettstedssystem.

## Autoritative kilder

- Sider og metadata: `src/pages/*.astro`.
- Delte Astro-hjelpere og typesikker kommersiell modell: `src/lib/` og `src/components/`.
- Priser, pakker og forretningsregler: `data/services.json`.
- Offentlige filer med stabile URL-er: `public/`.
- Produksjonsartefakt: `dist/`, bygget av Astro og ikke sjekket inn.

Endre aldri kommersielle verdier direkte i sidene. `.github/site-baseline.json` er den gjennomgåtte produksjonskontrakten for SEO, kommersiell tekst, booking og kjente avvik. Baseline skal bare oppdateres etter konkret gjennomgang, aldri automatisk for å skjule en feil.

## Lokal bygging og kontroll

```text
pnpm install --frozen-lockfile
pnpm check
pnpm build
pnpm test
python -m unittest discover -s .github/scripts -p "test_*.py" -v
node .github/scripts/test_runtime.cjs
python .github/scripts/site_quality.py
python .github/scripts/site_audit.py --report site-audit.json
git diff --check
```

Kvalitets- og auditverktøyene leser `dist/` som standard. Bygget bruker Node 22 og pnpm. Python brukes kun til repositoryets uavhengige audit- og kvalitetssikkerhetsnett.

## Dokumentasjon

- [Fase 1: opprinnelig audit og sikkerhetsnett](docs/phase-1-audit.md)
- [Fase 2: kommersielle data](docs/phase-2-business-data.md)
- [Fase 3a: felles JavaScript og CSS-grunnlag](docs/phase-3a-shared-assets.md)
- [Astro-paritet og produksjonsstatus](docs/astro-parity.md)
- [Opprydding etter Astro-cutover](docs/astro-cleanup.md)

Repoet har to historiske bildefiler med navnene `Meg.jpg` og `meg.jpg`. De kan ikke begge representeres riktig i en vanlig Windows-kopi. Ikke inkluder den kunstige bildeendringen fra dette i commits; bruk et case-sensitivt filsystem før arbeid på disse bildene.
