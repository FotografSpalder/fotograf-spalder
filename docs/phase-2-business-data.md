# Fase 2 – én kilde for kommersielle data

Dato: 6. september 2026. Bygger på fase 1, draft-PR #3.

## Resultat

`data/services.json` er nå redigeringskilden for 17 pakker, kategorier, navn, pris, fra-pris/prisintervall, antall inkluderte bilder, pakkeinnhold, bookinggrupper, fotograferingstillegg, digitale bildepriser, komplett galleri, betalingsandeler, leveringstid og detaljerte bookingvilkår.

`scripts/build_site.py` genererer de eksisterende 12 HTML-sidene fra `templates/pages/*.html.tmpl`. Bygget bruker bare Python-standardbiblioteket. Nettsiden bruker fortsatt vanlig statisk HTML på GitHub Pages, uten backend, nettverksavhengig bygg, nytt frontendrammeverk eller uthenting av priser i nettleseren.

Første generering var identisk med eksisterende HTML etter normalisering av CRLF/LF. Deretter ble etterfølgende mellomrom på fem tomme linjer fjernet for å bestå git diff --check. Dette er de eneste endringene i de genererte HTML-filene. Ingen priser, synlige tekster, CSS-regler, JavaScript, skjema-attributter, bildeutvalg, URL-er eller metadata ble endret i denne fasen.

## Slik oppdateres en pris

1. Endre riktig felt i `data/services.json`, for eksempel `services.pet-standard.price`.
2. Kjør `python scripts/build_site.py` fra repo-roten.
3. Kontroller diffen i genererte HTML-filer og kjør kontrollene nedenfor.
4. Ved en tilsiktet kommersiell endring: gjennomgå og oppdater de berørte forventningene i `.github/site-baseline.json` i samme endring. Dette er et testgrunnlag fra fase 1, ikke en kilde brukt i genereringen. Det skal ikke automatisk overskrives for å skjule avvik.
5. Commit datakilden, generert HTML og eventuelt gjennomgått testgrunnlag samlet.

En pris trenger ikke oppdateres manuelt i flere sider. CI kjører `--check` og feiler dersom HTML ikke svarer til gjeldende data/maler. Direkte redigering av generert HTML blir dermed oppdaget. CI skriver ikke automatisk til main.

## Datamodell

- `services`: hver pakke har stabil ID, navn, kategori, numerisk pris, `from_price`, eventuell `max_price`, `included_images` og `content`.
- `included_images: null` betyr at antall bilder avtales skriftlig, som for kultur/arrangement. Det betyr ikke null inkluderte bilder.
- `landing_content`: eksisterende kortere/annerledes godkjente formuleringer på tjenestesidene. Identiske punkter refererer tilbake til `content`, og inkluderte antall refererer alltid til samme numeriske felt. Redaksjonelle variasjoner er bevart i datafilen for å unngå uønsket tekstendring.
- `booking_groups`: autoritativ rekkefølge og gruppering av alle 17 bookingvalg. Hver tjeneste må forekomme nøyaktig én gang.
- `extras`: ekstra person, tidsutvidelse, reise og ekspressredigering har egne prisfelt. To tillegg som begge koster 500 kr er uavhengige produkter og deler ikke prisfelt.
- `digital`: mobil, høy oppløsning, full oppløsning og komplett digital pakke har separate felt.
- `digital.complete.scope` og `separately_quoted`: avgrensningen for 6 500 kr er eksplisitt; bryllup og større arrangementer har separat avtalt komplett galleri.
- `rules`: 30/70-andeler, levering 1–3 uker, varselfrist, forsinkelse, refusjonsklausul, værregel, leverandørnavn og bookingvilkår. De godkjente vilkårstekstene refererer til samme numeriske felter.

Generelle markedsføringstekster, tjenestebeskrivelser og formuleringer rundt reglene forblir redaksjonelt innhold. Det er ikke innført en regelmotor som automatisk omskriver juridiske eller markedsføringsmessige formuleringer. En endring av hva en regel betyr krever fortsatt at de berørte formuleringene gjennomgås.

## Maler og SEO

Maler bruker små datareferanser, for eksempel `{{ services.pet-standard.name }}`, `{{ services.pet-standard | price }}` og `{{ services.pet-standard.included_images | images }}`. Prisfilteret bevarer dagens tusenskilletegn og fra-merking per visning. Bildefilteret velger entall/flertall. Bookingvalg genereres som HTML med riktig escaping, mens tilbudsverdier i JSON-LD bruker JSON-escaping.

Eksisterende SEO-tilbud er koblet til tjenestedata, inkludert kjæledyrtilbud, bryllupspris og min-/makspriser for familie/portrett. Forsidens eksisterende intervaller beregnes fra de samme tjenestene den allerede omtaler. Oppgaven endrer ikke type eller struktur på schema.org-dataene.

Alle 11 sitemap-URL-er og takk.html beholdes. Dette inkluderer `/Konfirmasjon.html`, `/sommerfotografering.html`, www-canonical og CNAME. Ingen redirect eller domeneendring er innført.

Bygget validerer data og renderer alle sider før det begynner å skrive dem, slik at ugyldige data eller malreferanser ikke gir et delvis generert nettsted. Ukjente felter, sykliske referanser, ugyldige summer for betalingsandeler og feil i pris-/leveringsintervaller stopper bygget.

## Kontroller

Kjør fra repo-roten:

```text
python scripts/build_site.py --check
python scripts/check_commercial.py
python -m unittest discover -s .github/scripts -p "test_*.py" -v
node .github/scripts/test_runtime.cjs
python .github/scripts/site_quality.py
python .github/scripts/site_audit.py --report site-audit.json
git diff --check
```

15 nye datatester dekker blant annet:

- Alle 17 pakkepriser slår gjennom i priskort og bookingvalg.
- Endring av Kjæledyr Standards navn/pris/antall når tjenestesiden og JSON-LD.
- Digitale tillegg og fotograferingstillegg med samme opprinnelige beløp er uavhengige.
- Komplett digital pakke oppdateres på alle seks sider; bryllupsunntaket bevares.
- Endrede betalingsandeler og leveringstider når alle eksisterende forekomster.
- Min-/makspriser i SEO avledes fra data.
- Delt pakkeinnhold oppdaterer både pris- og tjenesteside.
- HTML-/JSON-escaping, ugyldig data, ukjente/sykliske referanser og manglende delvis skriving.
- `--check` skriver ikke filer, og gjentatt bygg er idempotent.

`check_commercial.py` avviser nye hardkodede priser, inkluderte bildeantall, kjente betalingsprosenter, leveringsintervaller og numeriske SEO-priser i redigeringsmalene. Generert HTML og det eksplisitte testgrunnlaget er unntak fordi de skal inneholde ferdig gjengitte verdier.

Lokalt resultat: alle 34 Python-tester består, i tillegg til de eksisterende runtime-testene for booking og samtykke. Bygg, kontroll av kommersielle data og begge kvalitetskontrollene består. Fase 1s 44 registrerte observasjoner er uendret. Alle 12 sidene er identiske med utgangspunktet etter normalisering av linjeskift og etterfølgende mellomrom på fem tomme linjer.

Ingen ekte booking er sendt. Visuell nettleser-/mobiltest og produksjonsnettverk er fortsatt ikke verifisert. Siden HTML kun har fem endringer av usynlige mellomrom, og CSS-regler og JavaScript er uendret, er det heller ikke gjort en visuell redesignkontroll i denne fasen. GitHub CI-resultatet rapporteres separat i PR-en/leveransen.

## Filendringer og neste steg

Opprettet: `data/services.json`, `scripts/build_site.py`, `scripts/check_commercial.py`, 12 filer under `templates/pages/`, `.github/scripts/test_business_data.py` og denne rapporten. CI-workflowen er utvidet med byggkontroll og kommersiell kontroll. Fem HTML-filer har kun fått fjernet mellomrom på én tom linje hver. Ingen produksjonsfunksjonalitet er fjernet. En .gitignore utelater Python-cache og lokal auditrapport, og README dokumenterer redigering og bygg.

Fase 3–4 gjenstår: trekke felles CSS/JS og header/footer ut av malene, med kontroll av dagens ulike layoutvarianter. Deretter bildearkitektur, sesongkonfigurasjon og videre QA. Augustinnholdet, bildeoptimaliseringen og Meg.jpg/meg.jpg-kollisjonen er fortsatt registrert teknisk gjeld. Git-historikken er ikke omskrevet.

