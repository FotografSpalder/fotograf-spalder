from pathlib import Path

ROOT = Path.cwd()
MARKER = "<!-- PAYMENT_FLOW_30_70 -->"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8", newline="\n")


def replace_required(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Fant ikke forventet tekst for {label}")
    return text.replace(old, new, 1)


def update_prices() -> None:
    path = "priser.html"
    text = read(path)
    if MARKER in text:
        return

    text = replace_required(
        text,
        "  grid-template-columns: repeat(3, 1fr);",
        "  grid-template-columns: repeat(4, 1fr);",
        "fire betalingstrinn på prissiden",
    )

    text = replace_required(
        text,
        "    Pakkeprisen dekker planlegging, tiden under fotograferingen, utvelgelse, redigering og tilgang til privat nettgalleri. Hver pakke inneholder også et tydelig oppgitt antall digitale bilder i høy kvalitet.",
        "    Pakkeprisen dekker planlegging, tiden under fotograferingen, utvelgelse, redigering og opprettelse av privat nettgalleri. Hver pakke inneholder også et tydelig oppgitt antall digitale bilder i høy kvalitet.",
        "galleriordlyd på prissiden",
    )

    old_steps = '''<div class="steps" aria-label="Slik fungerer bestillingen">
  <div class="step">
    <div class="step-number">1</div>
    <h2>Velg fotografering</h2>
    <p>Du betaler for selve oppdraget. Se alltid linjen «inkludert i prisen» på hver pakke.</p>
  </div>
  <div class="step">
    <div class="step-number">2</div>
    <h2>Se bildene</h2>
    <p>Etter fotograferingen får du et privat nettgalleri med de ferdig redigerte bildene.</p>
  </div>
  <div class="step">
    <div class="step-number">3</div>
    <h2>Velg eventuelle tillegg</h2>
    <p>Du kan kjøpe flere bilder, originalfiler eller hele galleriet dersom du ønsker det.</p>
  </div>
</div>'''

    new_steps = f'''{MARKER}
<div class="steps" aria-label="Slik fungerer betaling og levering">
  <div class="step">
    <div class="step-number">1</div>
    <h2>Reserver datoen</h2>
    <p>Når bookingen er godkjent, betaler du 30 % av fotograferingsprisen i forskudd. Først når forskuddet er betalt, er ønsket dato reservert.</p>
  </div>
  <div class="step">
    <div class="step-number">2</div>
    <h2>Fotografering</h2>
    <p>Vi gjennomfører fotograferingen som avtalt. De resterende 70 % betales ikke før etter fotograferingen.</p>
  </div>
  <div class="step">
    <div class="step-number">3</div>
    <h2>Betal 70 % i FotoSky</h2>
    <p>Når det private galleriet er klargjort, betaler du de resterende 70 % av fotograferingsprisen via FotoSky for å åpne galleriet.</p>
  </div>
  <div class="step">
    <div class="step-number">4</div>
    <h2>Åpne galleriet</h2>
    <p>Når restbeløpet er betalt, får du tilgang til galleriet. Der velger du bildene som er inkludert i pakken og kan kjøpe eventuelle tillegg separat.</p>
  </div>
</div>'''
    text = replace_required(text, old_steps, new_steps, "betalingstrinn på prissiden")

    text = replace_required(
        text,
        '''  <div class="info-box">
    <h2>Hvordan fungerer bildegalleriet?</h2>
    <p>
      Etter fotograferingen får du tilgang til et privat nettgalleri. Der velger du de bildene som følger med pakken og kan kjøpe flere bilder eller originalfiler dersom du ønsker det.
    </p>
  </div>''',
        '''  <div class="info-box">
    <h2>Hvordan fungerer bildegalleriet?</h2>
    <p>
      Etter fotograferingen klargjøres et privat galleri hos FotoSky. Galleriet er låst frem til de resterende 70 % av fotograferingsprisen er betalt via FotoSky. Når betalingen er registrert, åpnes galleriet. Der velger du bildene som følger med pakken og kan kjøpe flere bilder eller andre tillegg separat.
    </p>
  </div>''',
        "galleriinformasjon på prissiden",
    )

    text = replace_required(
        text,
        '''  <div class="info-box">
    <h2>Booking og forskudd</h2>
    <p>
      For å sikre booking betales et forskudd på 30 % av fotograferingsprisen. Beløpet trekkes fra totalsummen. Ved avbestilling refunderes ikke forskuddet.
    </p>
  </div>''',
        '''  <div class="info-box">
    <h2>Betaling: 30 % + 70 %</h2>
    <p>
      Når bookingen er godkjent, betales 30 % av fotograferingsprisen i forskudd for å reservere ønsket dato. Forskuddet trekkes fra fotograferingsprisen og refunderes ikke ved avbestilling. Etter fotograferingen betales de resterende 70 % via FotoSky før det private galleriet kan åpnes. Eventuelle kjøp av flere bilder eller andre tillegg i galleriet kommer i tillegg til fotograferingsprisen.
    </p>
  </div>''',
        "30/70-informasjon på prissiden",
    )

    write(path, text)


def update_booking() -> None:
    path = "booking.html"
    text = read(path)
    if MARKER in text:
        return

    text = replace_required(
        text,
        '''    <div class="status-box">
      <strong>Dette er en forespørsel – ikke en ferdig reservasjon.</strong><br>
      Tidspunktet er først bekreftet når du har mottatt skriftlig bekreftelse og forskuddet er betalt.
    </div>''',
        f'''    {MARKER}
    <div class="status-box">
      <strong>Dette er en forespørsel – ikke en ferdig reservasjon.</strong><br>
      Når forespørselen er godkjent, betaler du 30 % av fotograferingsprisen i forskudd. Ønsket dato er først reservert når forskuddet er registrert betalt.
    </div>

    <div class="notice">
      <strong>Slik betales resten:</strong><br>
      Etter fotograferingen klargjøres det private galleriet hos FotoSky. De resterende 70 % av fotograferingsprisen betales via FotoSky før galleriet kan åpnes. Når restbeløpet er betalt, får du tilgang til galleriet og kan velge inkluderte bilder og eventuelle tillegg.
    </div>''',
        "status og restbetaling på bookingsiden",
    )

    text = replace_required(
        text,
        '''          <li>Forskuddet er 30 % av prisen for det valgte fotograferingsoppdraget, trekkes fra denne prisen og refunderes ikke ved avbestilling.</li>''',
        '''          <li>Forskuddet er 30 % av prisen for det valgte fotograferingsoppdraget. Forskuddet reserverer ønsket dato, trekkes fra fotograferingsprisen og refunderes ikke ved avbestilling.</li>
          <li>De resterende 70 % av fotograferingsprisen betales via FotoSky etter fotograferingen og før det private galleriet kan åpnes.</li>
          <li>Når restbeløpet på 70 % er registrert betalt, åpnes galleriet. Eventuelle kjøp av flere bilder eller andre tillegg kommer i tillegg.</li>''',
        "betalingsvilkår på bookingsiden",
    )

    text = replace_required(
        text,
        '''      <label class="checkbox-label">
        <input type="checkbox" name="vilkar_godkjent" value="Ja" required>
        <span>Jeg har lest og godtar vilkårene over. <span class="required">*</span></span>
      </label>''',
        '''      <label class="checkbox-label">
        <input type="checkbox" name="betalingsforstaelse" value="Ja" required>
        <span>Jeg forstår betalingsløpet: 30 % betales for å reservere datoen, og de resterende 70 % betales via FotoSky etter fotograferingen før privatgalleriet åpnes. <span class="required">*</span></span>
      </label>

      <label class="checkbox-label">
        <input type="checkbox" name="vilkar_godkjent" value="Ja" required>
        <span>Jeg har lest og godtar vilkårene over. <span class="required">*</span></span>
      </label>''',
        "betalingsbekreftelse i bookingskjemaet",
    )

    write(path, text)


def update_thanks() -> None:
    path = "takk.html"
    text = read(path)
    if MARKER in text:
        return

    text = replace_required(
        text,
        '''      <div class="important">
        <strong>Dette er ikke en bekreftet booking ennå.</strong><br>
        Jeg svarer vanligvis innen 24 timer. Tidspunktet er først reservert når du har mottatt skriftlig bekreftelse og forskuddet er betalt.
      </div>''',
        f'''      {MARKER}
      <div class="important">
        <strong>Dette er ikke en bekreftet booking ennå.</strong><br>
        Jeg svarer vanligvis innen 24 timer. Når forespørselen er godkjent, betaler du 30 % av fotograferingsprisen i forskudd. Først når forskuddet er registrert betalt, er ønsket dato reservert.
      </div>''',
        "bookingstatus på takkesiden",
    )

    text = replace_required(
        text,
        '''      <ol class="steps">
        <li><strong>1. Jeg vurderer forespørselen</strong><br>Jeg sjekker ledig kapasitet og om ønskene dine lar seg gjennomføre.</li>
        <li><strong>2. Du mottar svar</strong><br>Du får informasjon om pris, tidspunkt, sted og neste steg.</li>
        <li><strong>3. Bookingen bekreftes</strong><br>Tidspunktet reserveres når avtalen er bekreftet skriftlig og forskuddet er betalt.</li>
      </ol>''',
        '''      <ol class="steps">
        <li><strong>1. Jeg vurderer forespørselen</strong><br>Jeg sjekker ledig kapasitet og om ønskene dine lar seg gjennomføre.</li>
        <li><strong>2. Du mottar svar og betaler 30 %</strong><br>Når forespørselen er godkjent, får du betalingsinformasjon. Datoen reserveres når forskuddet på 30 % er betalt.</li>
        <li><strong>3. Fotograferingen gjennomføres</strong><br>Vi møtes på avtalt tidspunkt og gjennomfører fotograferingen.</li>
        <li><strong>4. Du betaler de resterende 70 % i FotoSky</strong><br>Når det private galleriet er klargjort, betales restbeløpet via FotoSky før galleriet kan åpnes.</li>
        <li><strong>5. Privatgalleriet åpnes</strong><br>Når restbeløpet er registrert betalt, får du tilgang til galleriet. Der velger du inkluderte bilder og kan kjøpe eventuelle tillegg separat.</li>
      </ol>''',
        "betalingssteg på takkesiden",
    )

    write(path, text)


def main() -> None:
    update_prices()
    update_booking()
    update_thanks()


if __name__ == "__main__":
    main()
