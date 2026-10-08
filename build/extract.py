# Collect every Korean unit from the dist pages into per-page batches for translation (deduplicated across pages).
import io, json, os
from i18n import parse, units

DIST = '../dist/'
PAGES = ['index', 'ai-platform', 'hq-operations', 'sales-analytics', 'sodam', 'contact']
os.makedirs('src', exist_ok=True)
seen = {}
for p in PAGES:
    soup = parse(io.open(DIST + p + '.html', encoding='utf-8').read())
    batch = []
    for kind, node, key in units(soup):
        if key in seen:
            continue
        seen[key] = p
        batch.append({'id': f'{p}-{len(batch) + 1}', 'type': 'html' if kind == 'html' else ('attr' if kind.startswith('attr') else 'text'), 'ko': key})
    json.dump(batch, io.open(f'src/{p}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(p, len(batch), sum(len(b['ko']) for b in batch))
