# Fase 2 – sentral kommersiell datakilde

Dato: 6. september 2026. Dette er en historisk faserapport; dagens bygge- og testkommandoer står i README.

## Varig resultat

`data/services.json` ble etablert som én strukturert kilde for priser, pakker, inkluderte bilder, tillegg, digitale produkter, betalingsfordeling, leveringstid og bookingvilkår. Datakilden bruker schema v2 med strukturert tekst og uten generelle teksttokens.

Astro leser datafilen gjennom `src/lib/services.ts`. Modulen validerer skjemaet, formatterer priser og bildeantall, bygger bookingtekster og beregner prisintervaller. Ugyldige priser, bildeantall, betalingssummer, leveringsintervaller, bookinggrupper og nødvendige unntakstekster stopper bygget.

## Arbeidsflyt

1. Endre den aktuelle verdien i `data/services.json`.
2. Kjør `pnpm check`, `pnpm build` og `pnpm test`.
3. Gjennomgå `dist/` og den kommersielle diffen.
4. Oppdater `.github/site-baseline.json` bare når den tilsiktede produksjonsendringen er eksplisitt gjennomgått.

En pris skal ikke oppdateres manuelt i flere sider. `tests/commercial-mutations.test.mjs` bygger Astro med kontrollerte datamutasjoner og verifiserer blant annet:

- alle pakkepriser i pris- og bookingvisning;
- navn, innhold og inkluderte bilder på kjæledyrpakken;
- JSON-LD-tilbud og avledede prisintervaller;
- digitale produktpriser og uavhengige tillegg/unntak;
- betalingsfordeling og leveringstid;
- HTML- og JSON-sikker escaping;
- at ugyldige kommersielle data stopper bygget;
- at Astro-kildene ikke hardkoder sentrale kommersielle tall.

## Historikk og grenser

Fasen ble opprinnelig innført før Astro-migreringen. Selve datamodellen og testintensjonen er beholdt, mens den midlertidige genereringsimplementasjonen ble avviklet etter godkjent produksjonscutover. Ingen kommersielle verdier ble endret ved avviklingen.

Datamodellen skal ikke brukes som anledning til å normalisere tekst, pakker eller unntak. `priser`, `fra`, intervall, inkluderte bilder og unntaket for større bryllupsgallerier har fortsatt den betydningen som er uttrykt i data og Astro-sidene.
