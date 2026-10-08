# Build the English static site (en.fdam.co.kr) from the Korean dist pages + translation maps.
import io, json, re, os, shutil, glob, copy
from bs4 import BeautifulSoup, NavigableString
from i18n import parse, units, HANGUL

DIST = '../dist/'
OUT = 'out/'
EN = 'https://en.fdam.co.kr'
KO = 'https://fdam.co.kr'
PAGES = {  # dist file -> (en path, ko path)
    'index': ('/', '/'),
    'ai-platform': ('/ai-platform/', '/ai-platform'),
    'hq-operations': ('/hq-operations/', '/hq-operations'),
    'sales-analytics': ('/sales-analytics/', '/sales-analytics'),
    'sodam': ('/sodam/', '/sodam'),
    'contact': ('/contact/', '/register'),
}

# ---------- translation map: Korean source string -> English ----------
src, tr = {}, {}
for f in glob.glob('src/*.json'):
    for x in json.load(io.open(f, encoding='utf-8')):
        src[x['id']] = x['ko']
for f in glob.glob('tr/*.json'):
    tr.update(json.load(io.open(f, encoding='utf-8')))
FIX = [('Baljoo.com', 'Balju.com'), ('CEO: Mansuk Oh', 'CEO Oh Manseok'), ('Mansuk Oh', 'Oh Manseok')]
T = {}
for i, ko in src.items():
    en = tr[i]
    for a, b in FIX:
        en = en.replace(a, b)
    T[ko] = en
# contact page: the Korean draft had developer notes here; give real English copy
OVERRIDE = {
    '도입 상담과 유입 분석을 위한 개인정보 수집 및 이용에 동의합니다. 실제 적용 시 개인정보처리방침 링크와 보유 기간을 연결해 주세요.':
        'I agree to the collection and use of my personal information to respond to this inquiry. See our <a href="https://fdam.co.kr/?mode=privacy" target="_blank" rel="noopener">privacy policy</a>.',
    '초안에서는 전송되지 않습니다. 실제 운영 시 CRM 또는 이메일 수신 시스템을 연결해 주세요.':
        'Thank you. Your inquiry has been sent, and our team will reply by email within one business day.',
    '선택한 경로와 함께 광고·검색 캠페인 정보가 자동으로 기록되어 상담 유입 분석에 활용됩니다.':
        'Campaign details (such as ad or search source) are recorded with your inquiry to help us improve our outreach.',
    '010-0000-0000': '+82 10 0000 0000',
    '예: 프담프랜차이즈': 'e.g., FDAM Chicken',
}
T.update(OVERRIDE)
if os.path.exists('clients_tr.json'):
    T.update(json.load(io.open('clients_tr.json', encoding='utf-8')))  # client logo alt text


# extra strings that live only inside JSON-LD
LD_EXTRA = {
    '㈜엠에스벤터': 'MS Venter Co., Ltd.', '엠에스벤터': 'MS Venter', '프담': 'FDAM', '소담': 'Sodam', '소담 by 프담': 'Sodam by FDAM',
    '프랜차이즈 AI 운영 플랫폼 · 프랜차이즈 본사 ERP': 'AI operations platform for franchises · Franchisor HQ ERP',
    '벚꽃로 130-3 101-1003': '101-1003, 130-3 Beotkkot-ro', '연수구': 'Yeonsu-gu', '인천광역시': 'Incheon',
    'AI 발주 추천': 'AI order recommendations', 'AI 매출 하락 예측': 'AI sales-decline prediction', 'AI 폐점 위험 예측': 'AI store-closure risk prediction',
    'AI 사입 분석': 'AI off-catalog purchasing analysis', 'AI 회의 노트': 'AI meeting notes', 'AI 리뷰 답글': 'AI review replies', 'AI 운영 보고서': 'AI operations reports',
    '가맹 영업·전자계약·오픈 관리': 'Franchise sales, e-contracts and store openings', 'POS·배달앱 통합 매출 분석': 'Unified POS and delivery-app sales analytics',
    '가맹점 앱 소담': 'Sodam store app',
    '프랜차이즈 본사 및 가맹점': 'Franchisor headquarters and franchise stores',
    '프담 AI 플랫폼': 'FDAM AI Platform', '프담 프랜차이즈 본사 운영 관리': 'FDAM HQ Operations', '프담 통합 매출 분석': 'FDAM Unified Sales',
    '프랜차이즈 AI 예측 및 업무 자동화': 'Franchise AI prediction and workflow automation',
    '프랜차이즈 본사 ERP · 가맹 영업·계약·오픈·운영 통합 관리': 'Franchisor HQ ERP: franchise sales, contracts, openings and operations',
    '프랜차이즈 POS·배달앱 매출 통합 조회 및 분석': 'Unified POS and delivery-app sales reporting for franchises',
}
LD_LONG = {  # long LD descriptions, keyed by a Korean prefix
    '프랜차이즈 AI 운영 플랫폼 프담(fdam)을 만든 회사': 'The company behind FDAM, an AI operations platform for franchises. Since launching automated ARS ordering in 2003, MS Venter has built franchise IT for over 20 years, from the FMS logistics ERP (2006) and the Balju.com ordering app (2018) to the FDAM franchise operations ERP (2023).',
    '프담(fdam)은 ㈜엠에스벤터가 만든 프랜차이즈 AI 운영 플랫폼입니다. 가맹 영업·계약·오픈 등': 'FDAM is an AI operations platform for franchises built by MS Venter Co., Ltd. It connects HQ operations (franchise sales, contracts, store openings), unified POS and delivery-app sales, and the Sodam store app on one data layer, with AI order recommendations, sales-decline prediction and AI reports.',
    '프담(fdam)의 AI 기능': "FDAM's AI capabilities: analyze POS, delivery, ordering, inventory and operations data to recommend order quantities, predict sales declines and closure risk, and generate meeting notes, review replies and operations reports.",
    '프담(fdam)의 본사 운영 기능': "FDAM's HQ operations module connects franchise inquiries, consultations, e-contracts, store openings and day-to-day operations into one record per store.",
    '프담(fdam)의 통합 매출 기능': "FDAM's unified sales module consolidates POS, special-venue and delivery-app sales so you can compare by brand, store, channel and period and link it to AI predictions.",
    '프랜차이즈 AI 운영 플랫폼 프담(fdam)과 연결된 가맹점 전용 프로그램': 'The store app connected to FDAM, the AI operations platform for franchises: ordering, inventory, HQ communication, staff management and AI order recommendations.',
}


def tr_ld(v):
    if isinstance(v, dict):
        return {k: tr_ld(x) for k, x in v.items()}
    if isinstance(v, list):
        return [tr_ld(x) for x in v]
    if isinstance(v, str) and HANGUL.search(v):
        if v in T:
            return re.sub(r'<[^>]+>', '', T[v])
        if v in LD_EXTRA:
            return LD_EXTRA[v]
        for k, e in LD_LONG.items():
            if v.startswith(k):
                return e
        MISSING.add(v)
    return v


MISSING = set()


def link(href, here):
    if href.startswith(('http', 'mailto:', 'tel:', '#', 'javascript')):
        if href.startswith('https://fdam.co.kr/blog'):
            return '/blog/'
        return href
    if href.startswith('/?mode='):
        return KO + href
    m = re.match(r'([a-z-]+)\.html(#.*)?$', href)
    if m:
        page, frag = m.group(1), m.group(2) or ''
        return PAGES.get(page, ('/' + page + '/',))[0] + frag
    if href.startswith('assets/'):
        return '/' + href
    return href


def build(page):
    en_path, ko_path = PAGES[page]
    soup = parse(io.open(DIST + page + '.html', encoding='utf-8').read())
    for kind, node, key in units(soup):
        en = T.get(key)
        if en is None:
            MISSING.add(key); continue
        if kind == 'html':
            node.clear()
            for c in list(parse(en).contents):
                node.append(c)
        elif kind == 'text':
            raw = str(node)
            node.replace_with(NavigableString(raw[:len(raw) - len(raw.lstrip())] + en + raw[len(raw.rstrip()):]))
        else:
            node.attrs[kind.split(':', 1)[1]] = re.sub(r'<[^>]+>', '', en)
    soup.html['lang'] = 'en'
    kw = soup.find('meta', attrs={'name': 'keywords'})
    KW = {'index': 'FDAM, franchise AI, franchise ERP, franchisor headquarters software, franchise management system, unified sales, store ordering app, Sodam',
          'ai-platform': 'franchise AI, AI order recommendation, sales decline prediction, store closure prediction, franchise data analytics, AI reports',
          'hq-operations': 'franchisor headquarters management, franchise sales management, store opening management, franchise operations system, QSCV inspection',
          'sales-analytics': 'franchise sales management, delivery app sales integration, POS sales analytics, store sales reporting',
          'sodam': 'franchise ordering app, store inventory management, food service ordering, AI order recommendation, Sodam',
          'contact': 'FDAM contact, franchise software demo'}
    if kw is not None:
        kw['content'] = KW.get(page, KW['index'])
    # links
    for a in soup.find_all(['a', 'link']):
        h = a.get('href')
        if not h:
            continue
        n = link(h, en_path)
        if n is None:
            a.decompose(); continue
        a['href'] = n
    for el in soup.find_all(src=True):
        if el['src'].startswith('assets/'):
            el['src'] = '/' + el['src']
    # language switch: EN button becomes KO
    for a in soup.select('a.nav-en'):
        a['href'] = KO + ko_path
        a.string = 'KO'
        a['hreflang'] = 'ko'
        a['lang'] = 'ko'
    # head: canonical, hreflang, og, font
    head = soup.head
    for t in head.find_all('link', rel=lambda r: r and ('canonical' in r or 'alternate' in r)):
        t.decompose()
    title = soup.title.get_text() if soup.title else 'FDAM'
    desc = (soup.find('meta', attrs={'name': 'description'}) or {}).get('content', '')
    add = [
        f'<link rel="canonical" href="{EN}{en_path}">',
        f'<link rel="alternate" hreflang="en" href="{EN}{en_path}">',
        f'<link rel="alternate" hreflang="ko" href="{KO}{ko_path}">',
        f'<link rel="alternate" hreflang="x-default" href="{KO}{ko_path}">',
        '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>',
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">',
        f'<meta property="og:type" content="website">', f'<meta property="og:site_name" content="FDAM">',
        f'<meta property="og:locale" content="en_US">', f'<meta property="og:url" content="{EN}{en_path}">',
        f'<meta property="og:title" content="{title}">', f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:image" content="{EN}/assets/og/og-{page}.png">', '<meta name="twitter:card" content="summary_large_image">',
    ]
    for t in head.find_all('meta', attrs={'property': re.compile('^og:')}):
        t.decompose()
    anchor = head.find('link', rel='stylesheet')
    for h in add:
        anchor.insert_before(parse(h))
        anchor.insert_before('\n  ')
    # JSON-LD
    for sc in soup.find_all('script', attrs={'type': 'application/ld+json'}):
        data = json.loads(sc.string)
        data = tr_ld(data)
        txt = json.dumps(data, ensure_ascii=False)
        for pg, (ep, kp) in PAGES.items():
            if kp != '/':
                txt = txt.replace(f'"{KO}{kp}#', f'"{EN}{ep}#').replace(f'"{KO}{kp}"', f'"{EN}{ep}"')
        txt = txt.replace('"inLanguage": "ko-KR"', '"inLanguage": "en"')
        sc.string = txt
    html = str(soup)
    # layout fixes for longer English strings
    html = html.replace('order-visual"><b>18 items</b><span>Recommended</span>', 'order-visual"><b>18</b><span>items recommended</span>')
    html = html.replace('placeholder="010-0000-0000"', 'placeholder="+82 10 0000 0000"')
    out = OUT + en_path.strip('/') + '/index.html' if en_path != '/' else OUT + 'index.html'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    io.open(out, 'w', encoding='utf-8', newline='').write(html)
    left = [m for m in re.findall(r'[^<>"]*[가-힣]+[^<>"]*', re.sub(r'<script[\s\S]*?</script>', '', html))]
    return out, left


if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
shutil.copytree(DIST + 'assets', OUT + 'assets')
shutil.copy('assets-en/en-logo.png', OUT + 'assets/fdam_logo.png')
if os.path.isdir('assets-en/clients'):
    shutil.copytree('assets-en/clients', OUT + 'assets/clients')  # English wordmark (FDAM) instead of the Korean one
if os.path.isdir('assets-en/og'):
    shutil.copytree('assets-en/og', OUT + 'assets/og')
# the English wordmark is wider than the Korean one; give it a little more width so it keeps its visual weight
io.open(OUT + 'assets/styles.css', 'a', encoding='utf-8').write(
    '\n/* en: wider FDAM wordmark */\n.brand img{width:126px}.footer-brand .brand img{width:140px}@media (max-width:760px){.brand img{width:104px}}\n')
report = {}
for p in PAGES:
    o, left = build(p)
    report[p] = left
    print(p, '->', o, '| Hangul left:', len(left))

# English app.js: language strings, page links, real form submission (FormSubmit -> fdam@fdam.co.kr)
js = io.open(OUT + 'assets/app.js', encoding='utf-8').read()
js = js.replace("'메뉴 닫기'", "'Close menu'").replace("'메뉴 열기'", "'Open menu'")
for pg, (ep, kp) in PAGES.items():
    js = js.replace(f"'{pg}.html", f"'{ep}").replace(f'"{pg}.html', f'"{ep}')
js = js.replace("""form?.addEventListener('submit', (event) => {
  event.preventDefault();
  const success = form.querySelector('.form-success');
  success?.classList.add('show');
  success?.setAttribute('tabindex', '-1');
  success?.focus();
});""", """form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  const success = form.querySelector('.form-success');
  const data = Object.fromEntries(new FormData(form).entries());
  data._subject = `[FDAM EN] Inquiry from ${data.company || data.name || 'website'}`;
  data._template = 'table';
  data._captcha = 'false';
  if (button) { button.disabled = true; button.dataset.label = button.innerHTML; button.textContent = 'Sending…'; }
  try {
    const res = await fetch('https://formsubmit.co/ajax/fdam@fdam.co.kr', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(data) });
    if (!res.ok) throw new Error(String(res.status));
    form.querySelectorAll('input:not([type=hidden]),select,textarea').forEach((f) => { if (f.type !== 'checkbox') f.value = ''; });
    if (success) success.textContent = 'Thank you. Your inquiry has been sent, and our team will reply by email within one business day.';
  } catch (e) {
    if (success) success.innerHTML = 'Sorry, the form could not be sent. Please email us at <a href="mailto:fdam@fdam.co.kr">fdam@fdam.co.kr</a>.';
  }
  if (button) { button.disabled = false; button.innerHTML = button.dataset.label; }
  success?.classList.add('show');
  success?.setAttribute('tabindex', '-1');
  success?.focus();
});""")
assert 'formsubmit.co' in js
io.open(OUT + 'assets/app.js', 'w', encoding='utf-8', newline='').write(js)

# old English URLs, robots, sitemap, 404
for old, new in [('register', '/contact/')]:
    os.makedirs(OUT + old, exist_ok=True)
    io.open(OUT + old + '/index.html', 'w', encoding='utf-8').write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>FDAM</title><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={new}"><link rel="canonical" href="{new if new.startswith("http") else EN + new}"></head><body><a href="{new}">Continue</a></body></html>')
io.open(OUT + 'robots.txt', 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\n\nSitemap: {EN}/sitemap.xml\n')
urls = ''.join(f'''  <url>
    <loc>{EN}{ep}</loc>
    <xhtml:link rel="alternate" hreflang="en" href="{EN}{ep}"/>
    <xhtml:link rel="alternate" hreflang="ko" href="{KO}{kp}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{KO}{kp}"/>
  </url>
''' for ep, kp in PAGES.values())
io.open(OUT + 'sitemap.xml', 'w', encoding='utf-8').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}</urlset>\n')
nf = io.open(OUT + 'index.html', encoding='utf-8').read()
io.open(OUT + '404.html', 'w', encoding='utf-8').write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | FDAM</title><meta name="robots" content="noindex"><link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"><style>body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:Pretendard,system-ui,sans-serif;background:#f6f7fb;color:#151a2e;text-align:center}a{color:#435BA8;font-weight:700}</style></head><body><div><p style="color:#8496CB;font-weight:800;letter-spacing:.08em">404</p><h1>Page not found</h1><p>The page you are looking for has moved.</p><p><a href="/">Go to FDAM home</a></p></div></body></html>')
print('missing translations:', len(MISSING))
for m in list(MISSING)[:40]:
    print('  MISSING:', m[:120])
for p, l in report.items():
    for x in l[:10]:
        print('  LEFT', p, x[:100])
