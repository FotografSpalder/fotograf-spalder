from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Fant ikke forventet tekst i {path}: {old[:90]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


# Forsiden: permanente tjenester skal være lettere å finne enn en sesongside.
replace_once(
    "index.html",
    '          <a href="portfolio.html">Portefølje</a>\n          <a href="sommerfotografering.html">Sommerfoto</a>\n          <a href="kjaeledyrsfotograf-ringsaker.html">Kjæledyr</a>',
    '          <a href="portfolio.html">Portefølje</a>\n          <a href="familie-portrettfotograf-ringsaker.html">Familie/portrett</a>\n          <a href="bryllupsfotograf-ringsaker.html">Bryllup</a>\n          <a href="kjaeledyrsfotograf-ringsaker.html">Kjæledyr</a>'
)

replace_once(
    "index.html",
    '      Jeg spesialiserer meg på kjæledyrsfotografering, portrettfoto, familiefoto og bryllup.',
    '      Jeg spesialiserer meg på kjæledyrsfotografering, <a href="familie-portrettfotograf-ringsaker.html" style="color:#fde68a;font-weight:700;">portrett- og familiefoto</a> og <a href="bryllupsfotograf-ringsaker.html" style="color:#fde68a;font-weight:700;">bryllupsfotografering</a>.'
)

replace_once(
    "index.html",
    '''          <article class="card">
            <h3>Portrett og familie</h3>
            <p>Naturlige portretter ute eller i avtalt miljø. Passer både enkeltpersoner, par og familier.</p>
            <a href="sommerfotografering.html" class="button secondary">Se sensommerfoto</a>
          </article>''',
    '''          <article class="card">
            <h3>Portrett og familie</h3>
            <p>Naturlige portretter ute eller i avtalt miljø. Passer både enkeltpersoner, par og familier – hele året.</p>
            <a href="familie-portrettfotograf-ringsaker.html" class="button secondary">Les mer</a>
          </article>'''
)

replace_once(
    "index.html",
    '''          <article class="card">
            <h3>Bryllup og spesielle anledninger</h3>
            <p>Dokumentarisk og stemningsfull fotografering av store dager, med fokus på ekte øyeblikk.</p>
          </article>''',
    '''          <article class="card">
            <h3>Bryllupsfotografering</h3>
            <p>Dokumentarisk og stemningsfull fotografering av bryllupsdagen, med fokus på ekte øyeblikk.</p>
            <a href="bryllupsfotograf-ringsaker.html" class="button secondary">Les mer</a>
          </article>'''
)

replace_once(
    "index.html",
    '''      <p>© <span id="year"></span> Fotograf Spalder. Alle rettigheter reservert.</p>

    </div>''',
    '''      <p>© <span id="year"></span> Fotograf Spalder. Alle rettigheter reservert.</p>
      <p><a href="personvern.html" style="color:#fde68a;">Personvern og informasjonskapsler</a></p>
    </div>'''
)

# Porteføljen: send interesserte videre til de permanente tjenestesidene.
replace_once(
    "portfolio.html",
    '''      <div class="gallery-item">
        <img src="konfirmant3.jpg" loading="lazy" alt="Ekslusivt portrett innendørs i Innlandet av Fotograf Spalder" title="Portrettfotograf Innlandet">
      </div>
    </div>
  </div>''',
    '''      <div class="gallery-item">
        <img src="konfirmant3.jpg" loading="lazy" alt="Ekslusivt portrett innendørs i Innlandet av Fotograf Spalder" title="Portrettfotograf Innlandet">
      </div>
    </div>
    <div class="button-row"><a class="button" href="familie-portrettfotograf-ringsaker.html">Les om portrettfotografering</a></div>
  </div>'''
)

replace_once(
    "portfolio.html",
    '''      <div class="gallery-item">
        <img src="familie2.jpg" loading="lazy" alt="Naturlig familiebilde i Innlandet av Fotograf Spalder" title="Familiefoto Innlandet">
      </div>
    </div>
  </div>''',
    '''      <div class="gallery-item">
        <img src="familie2.jpg" loading="lazy" alt="Naturlig familiebilde i Innlandet av Fotograf Spalder" title="Familiefoto Innlandet">
      </div>
    </div>
    <div class="button-row"><a class="button" href="familie-portrettfotograf-ringsaker.html">Les om familiefotografering</a></div>
  </div>'''
)

replace_once(
    "portfolio.html",
    '''    <div class="gallery-item">
      <img src="bryllup3.jpg" loading="lazy" alt="Dokumentarisk bryllupsbilde tatt av Fotograf Spalder">
    </div>
  </div>
</div>''',
    '''    <div class="gallery-item">
      <img src="bryllup3.jpg" loading="lazy" alt="Dokumentarisk bryllupsbilde tatt av Fotograf Spalder">
    </div>
  </div>
  <div class="button-row"><a class="button" href="bryllupsfotograf-ringsaker.html">Les om bryllupsfotografering</a></div>
</div>'''
)

# Forsiden og porteføljen er endret i dag; sitemap skal ikke påstå gammel endringsdato.
sitemap = Path("sitemap.xml")
text = sitemap.read_text(encoding="utf-8")
text = text.replace(
    '<loc>https://www.fotograf-spalder.com/</loc>\n    <lastmod>2026-08-04</lastmod>',
    '<loc>https://www.fotograf-spalder.com/</loc>\n    <lastmod>2026-08-25</lastmod>',
    1,
)
text = text.replace(
    '<loc>https://www.fotograf-spalder.com/portfolio.html</loc>\n    <lastmod>2026-08-04</lastmod>',
    '<loc>https://www.fotograf-spalder.com/portfolio.html</loc>\n    <lastmod>2026-08-25</lastmod>',
    1,
)
sitemap.write_text(text, encoding="utf-8")

print("Permanente sider for bryllup og familie/portrett er koblet inn i nettstedet.")