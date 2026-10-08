# Export the Korean -> English translation table as a CSV for review in Excel.
import io, json, glob, csv, re, os

src, tr = {}, {}
for f in glob.glob('src/*.json'):
    page = os.path.splitext(os.path.basename(f))[0]
    for x in json.load(io.open(f, encoding='utf-8')):
        src[x['id']] = (x['ko'], page)
for f in glob.glob('tr/*.json'):
    tr.update(json.load(io.open(f, encoding='utf-8')))
order = ['index', 'ai-platform', 'hq-operations', 'sales-analytics', 'sodam', 'contact']
rows = sorted(src.items(), key=lambda kv: (order.index(kv[1][1]), int(kv[0].split('-')[-1])))
strip = lambda t: re.sub(r'\s+', ' ', re.sub(r'<br\s*/?>', ' / ', re.sub(r'<(?!br)[^>]+>', '', t))).strip()
with io.open('번역표_ko-en.csv', 'w', encoding='utf-8-sig', newline='') as fp:
    w = csv.writer(fp)
    w.writerow(['id', '페이지', '한국어', '영어'])
    for i, (ko, pg) in rows:
        w.writerow([i, pg, strip(ko), strip(tr[i])])
print(len(rows))
