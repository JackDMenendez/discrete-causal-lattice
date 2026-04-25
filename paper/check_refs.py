import re, glob
labels = set()
refs = []
files = glob.glob('sections/*.tex') + glob.glob('../figures/*.tex') + ['main.tex']
for f in files:
    with open(f, encoding='utf-8') as fh:
        text = fh.read()
    for m in re.finditer(r'\\label\{([^}]+)\}', text):
        labels.add(m.group(1))
    for m in re.finditer(r'\\ref\{([^}]+)\}', text):
        refs.append((m.group(1), f))

missing = [(r, f) for r, f in refs if r not in labels]
print(f'Total labels: {len(labels)}')
print(f'Total refs: {len(refs)}')
print(f'Unresolved refs: {len(missing)}')
print()
for r, f in missing:
    print(f'  {r}  (in {f})')

cites = []
for f in files:
    with open(f, encoding='utf-8') as fh:
        text = fh.read()
    for m in re.finditer(r'\\cite\{([^}]+)\}', text):
        for k in m.group(1).split(','):
            cites.append((k.strip(), f))

bib_entries = set()
with open('paper-bib/references.bib', encoding='utf-8') as fh:
    for line in fh:
        m = re.match(r'@\w+\{([^,]+),', line)
        if m:
            bib_entries.add(m.group(1).strip())

missing_cites = [(c, f) for c, f in cites if c not in bib_entries]
print()
print(f'Total bib entries: {len(bib_entries)}')
print(f'Total cite calls: {len(cites)}')
print(f'Unresolved cites: {len(missing_cites)}')
print()
for c, f in missing_cites:
    print(f'  {c}  (in {f})')
