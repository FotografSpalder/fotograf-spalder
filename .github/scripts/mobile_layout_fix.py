from __future__ import annotations

import re
from pathlib import Path

ROOT = Path.cwd()
START = "/* MOBILE_LAYOUT_FIX_START */"
END = "/* MOBILE_LAYOUT_FIX_END */"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8", newline="\n")


def replace_all(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def upsert_css(text: str, css: str) -> str:
    block = f"\n{START}\n{css.strip()}\n{END}\n"
    pattern = re.compile(
        rf"\n?{re.escape(START)}.*?{re.escape(END)}\n?",
        flags=re.S,
    )
    if pattern.search(text):
        return pattern.sub(block, text, count=1)
    if "</style>" not in text:
        raise RuntimeError("Fant ikke </style>")
    return text.replace("</style>", block + "</style>", 1)


def update_index() -> None:
    path = "index.html"
    text = read(path)
    text = replace_all(
        text,
        [
            ("Kjæledyr, portrett og bryllup", "Kjæledyr, familie og portrett"),
            (">Se sommerfoto<", ">Se sensommerfoto<"),
            ("Om sommeren kan du lese mer om", "I sensommeren kan du lese mer om"),
            (">sommerfotografering i Ringsaker<", ">sensommerfotografering i Ringsaker<"),
        ],
    )

    css = r"""
/* Sikrer at brede og absolutt plasserte elementer ikke dekker innhold. */
.season-card > *,
.contact-box > * {
  min-width: 0;
}

.season-badge {
  max-width: 100%;
}

.contact-box {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 2rem;
  align-items: end;
  position: relative;
}

.contact-box > div:not(.contact-logo) {
  min-width: 0;
  order: 1;
}

.contact-logo {
  position: static;
  order: 2;
  align-self: end;
  width: 180px;
  max-width: 100%;
  height: auto;
  padding: 12px;
  border-radius: 14px;
  background: rgba(255,255,255,0.94);
  border: 1px solid rgba(255,255,255,0.28);
}

.contact-list,
.contact-list div,
.contact-list a {
  min-width: 0;
  overflow-wrap: anywhere;
}

@media (max-width: 950px) {
  .site-header {
    position: static;
    backdrop-filter: none;
  }

  section {
    padding: 3rem 0;
  }

  .hero {
    padding: 3rem 0 2.5rem;
  }

  .season-card {
    width: 100%;
    max-width: 100%;
    overflow: hidden;
    padding: 1.5rem;
    gap: 1.25rem;
  }

  .season-badge {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    justify-self: stretch;
    margin: 0;
    padding: 1.25rem 1rem;
  }

  .contact-box {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .contact-logo {
    width: min(180px, 100%);
    justify-self: start;
    margin-top: 0.25rem;
  }

  h1,
  h2,
  h3,
  .button {
    overflow-wrap: anywhere;
    hyphens: auto;
  }

  .button {
    max-width: 100%;
    white-space: normal;
    text-align: center;
    line-height: 1.25;
  }
}

@media (max-width: 600px) {
  .container {
    width: min(100% - 1.5rem, var(--max));
  }

  .nav {
    align-items: center;
    padding: 0.85rem 0;
  }

  .brand strong {
    font-size: 1rem;
  }

  .brand span {
    font-size: 0.82rem;
  }

  h1 {
    font-size: clamp(2rem, 10vw, 3rem);
  }

  h2 {
    font-size: clamp(1.65rem, 8vw, 2.15rem);
  }

  section {
    padding: 2.5rem 0;
  }

  .season-card {
    padding: 1.25rem;
  }

  .season-card .button,
  .contact-box .button {
    width: 100%;
  }

  .footer {
    padding: 1.5rem 0 2rem;
  }
}
"""
    text = upsert_css(text, css)
    write(path, text)


def update_sensommer() -> None:
    path = "sommerfotografering.html"
    text = read(path)
    text = replace_all(
        text,
        [
            ("Sommerfotografering kan tilpasses både små og store oppdrag.", "Sensommerfotografering kan tilpasses både små og store oppdrag."),
            ("Passer godt når familien er samlet i ferien.", "Passer godt når familien er samlet."),
            ("Steder for sommerfotografering", "Steder for sensommerfotografering"),
            ("Praktisk før sensommerfotograferingen", "Praktisk før fotograferingen"),
        ],
    )

    css = r"""
.hero-grid > *,
.info-box,
.card,
.step,
.cta {
  min-width: 0;
}

h1,
h2,
h3,
.button {
  overflow-wrap: anywhere;
  hyphens: auto;
}

.button {
  max-width: 100%;
  white-space: normal;
  text-align: center;
  line-height: 1.25;
}

@media (max-width: 900px) {
  .site-header {
    position: static;
    backdrop-filter: none;
  }

  .nav {
    align-items: center;
    padding: 0.85rem 0;
  }

  section {
    padding: 3rem 0;
  }

  .hero {
    padding: 3rem 0 2.5rem;
  }

  .info-box,
  .card,
  .step,
  .cta,
  .hero-card {
    overflow: hidden;
  }

  .hero-image::after {
    max-width: calc(100% - 2rem);
    white-space: normal;
    text-align: center;
    line-height: 1.25;
  }

  .cta {
    padding: 1.5rem;
  }
}

@media (max-width: 600px) {
  .container {
    width: min(100% - 1.5rem, var(--max));
  }

  .brand strong {
    font-size: 1rem;
  }

  .brand span {
    font-size: 0.82rem;
  }

  h1 {
    font-size: clamp(2rem, 10vw, 3rem);
  }

  h2 {
    font-size: clamp(1.65rem, 8vw, 2.15rem);
  }

  section {
    padding: 2.5rem 0;
  }

  .hero {
    padding: 2.25rem 0 2.5rem;
  }

  .hero-actions,
  .cta-actions {
    align-items: stretch;
  }

  .hero-actions .button,
  .cta-actions .button {
    width: 100%;
  }

  .info-box,
  .card,
  .step {
    padding: 1.2rem;
  }

  .hero-image {
    min-height: 360px;
  }

  .footer {
    padding: 1.5rem 0 2rem;
  }
}
"""
    text = upsert_css(text, css)
    write(path, text)


def main() -> None:
    update_index()
    update_sensommer()
    print("Mobilvisningen er oppdatert for index.html og sommerfotografering.html")


if __name__ == "__main__":
    main()
