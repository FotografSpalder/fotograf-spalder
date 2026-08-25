from pathlib import Path
import re

for filename in ['priser.html', 'portfolio.html']:
    path = Path(filename)
    text = path.read_text(encoding='utf-8')

    # Fjern rester fra de gamle klikkbare div-tabene som lå igjen etter konverteringen.
    pattern = re.compile(
        r'\n\s*(?:<div class="tab" onclick="showTab\(event, \'[^\']+\'\)">.*?</div>\s*)+\s*</div>\s*(?=\n\s*(?:<!--|<div id="dyr"))',
        re.S,
    )
    text, count = pattern.subn('\n', text, count=1)
    if count != 1:
        raise SystemExit(f'Fant ikke gamle tab-rester i {filename}')

    if '/* TAB_ACCESSIBILITY_FIX */' not in text:
        css = '''
/* TAB_ACCESSIBILITY_FIX */
.tabs button.tab {
  border: 1px solid transparent;
  font: inherit;
  color: var(--text);
  appearance: none;
}

.tabs button.tab:hover { border-color: var(--line); }
.tabs button.tab:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 3px;
}

[role="tabpanel"][hidden] { display: none !important; }
'''
        text = text.replace('</style>', css + '\n</style>', 1)

    path.write_text(text, encoding='utf-8')

print('Gamle tab-rester fjernet og knappestil kontrollert.')
