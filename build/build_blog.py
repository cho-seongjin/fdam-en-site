# English blog for en.fdam.co.kr: /blog/ list + /blog/<slug>/ posts, built from blog/en/*.json (translated) and blog/clean/*.json (dates, images).
# Run after build_en.py. Reuses the header/footer of the generated English home page.
import io, json, glob, re, os, html, datetime
from bs4 import BeautifulSoup

OUT = 'out/'
EN = 'https://en.fdam.co.kr'
KO = 'https://fdam.co.kr'

posts = []
for f in glob.glob('blog/en/*.json'):
    e = json.load(io.open(f, encoding='utf-8'))
    k = json.load(io.open('blog/clean/' + e['idx'] + '.json', encoding='utf-8'))
    d = datetime.datetime.fromisoformat(k['date'])
    posts.append({**e, 'date': d, 'image': k.get('image', '')})
posts.sort(key=lambda p: p['date'], reverse=True)
by_idx = {p['idx']: p for p in posts}

home = io.open(OUT + 'index.html', encoding='utf-8').read()
HEADER = re.search(r'<header class="site-header">[\s\S]*?</header>', home).group(0)
FOOTER = re.search(r'<footer class="site-footer">[\s\S]*?</footer>', home).group(0)
PROGRESS = '<div aria-hidden="true" class="scroll-progress"><i></i></div>'

INTERNAL = {'': '/', 'index': '/', 'register': '/contact/', 'ai-platform': '/ai-platform/', 'hq-operations': '/hq-operations/',
            'sales-analytics': '/sales-analytics/', 'sodam': '/sodam/'}


def fix_links(h):
    soup = BeautifulSoup(h, 'html.parser')
    for a in soup.find_all('a', href=True):
        u = html.unescape(a['href']).strip()
        m = re.match(r'https?://(?:www\.)?fdam\.co\.kr/blog/?\?.*idx=(\d+)', u)
        if m and m.group(1) in by_idx:
            a['href'] = '/blog/' + by_idx[m.group(1)]['slug'] + '/'; continue
        m = re.match(r'https?://(?:www\.)?(?:fdam\.co\.kr|xn--erp-jc7my74dh1cm8fmov\.com)/?([a-z-]*)', u)
        if m and m.group(1) in INTERNAL:
            a['href'] = INTERNAL[m.group(1)]; continue
        if u.startswith('http://pf.kakao.com'):
            a['href'] = 'https://' + u[len('http://'):]
        if u.startswith('tel:'):
            a['href'] = 'tel:+82-1544-7120'
        if a['href'].startswith('http') and 'fdam.co.kr' not in a['href']:
            a['target'] = '_blank'; a['rel'] = 'noopener'
    for img in soup.find_all('img'):
        img['loading'] = 'lazy'; img['decoding'] = 'async'
        if img.get('src', '').startswith('alt='):
            img.decompose()
    # editor comment that leaked into visible text in one source post
    for t in soup.find_all(string=re.compile(r'^\s*<!--')):
        t.extract()
    return str(soup)


def fmt(d):
    return d.strftime('%b %-d, %Y') if os.name != 'nt' else d.strftime('%b %#d, %Y')


def page(title, desc, path, body, og_image, extra_head=''):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width,initial-scale=1" name="viewport"/>
<title>{html.escape(title)}</title>
<meta content="{html.escape(desc)}" name="description"/>
<meta content="#f5f4ff" name="theme-color"/>
<link href="/assets/logo.png" rel="icon"/>
<link href="{EN}{path}" rel="canonical"/>
<link href="{EN}/blog/rss.xml" rel="alternate" title="FDAM Blog" type="application/rss+xml"/>
<link crossorigin="" href="https://cdn.jsdelivr.net" rel="preconnect"/>
<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css" rel="stylesheet"/>
<meta content="FDAM" property="og:site_name"/><meta content="en_US" property="og:locale"/>
<meta content="{EN}{path}" property="og:url"/><meta content="{html.escape(title)}" property="og:title"/>
<meta content="{html.escape(desc)}" property="og:description"/><meta content="{og_image}" property="og:image"/>
<meta content="summary_large_image" name="twitter:card"/>
<link href="/assets/styles.css" rel="stylesheet"/>
<link href="/assets/blog.css" rel="stylesheet"/>
{extra_head}
</head>
<body class="en-blog">
<a class="skip-link" href="#main">Skip to content</a>
{PROGRESS}
{HEADER}
<main id="main">
{body}
</main>
{FOOTER}
<script src="/assets/app.js"></script>
</body>
</html>
'''


def card(p):
    img = f'<img src="{p["image"]}" alt="" loading="lazy" decoding="async">' if p['image'] else '<span class="eb-noimg"></span>'
    return (f'<a class="eb-card" href="/blog/{p["slug"]}/"><span class="eb-thumb">{img}</span>'
            f'<span class="eb-body"><time datetime="{p["date"].date()}">{fmt(p["date"])}</time><b>{html.escape(p["title"])}</b>'
            f'<span>{html.escape(p["description"])}</span></span></a>')


CTA = ('<aside class="eb-cta"><div><span class="eyebrow">Talk to sales</span><h2>See what FDAM can do for your franchise.</h2>'
       '<p>Tell us about your brand and current systems. We will suggest the right rollout scope.</p></div>'
       '<a class="button button-primary" href="/contact/">Contact sales <span class="arrow">→</span></a></aside>')

# ---------- list ----------
os.makedirs(OUT + 'blog', exist_ok=True)
lst = (f'<section class="eb-hero"><div class="container"><span class="eyebrow">FDAM Insights</span>'
       f'<h1>Franchise operations,<br><span class="gradient-text">answered in the field.</span></h1>'
       f'<p>Practical notes for franchisor headquarters: store openings, contracts, logistics, unified sales and AI in day-to-day operations.</p></div></section>'
       f'<section class="eb-list"><div class="container"><div class="eb-grid">{"".join(card(p) for p in posts)}</div></div></section>')
ld_list = {'@context': 'https://schema.org', '@type': 'Blog', 'name': 'FDAM Blog', 'url': EN + '/blog/', 'inLanguage': 'en',
           'publisher': {'@id': KO + '/#org'},
           'blogPost': [{'@type': 'BlogPosting', 'headline': p['title'], 'url': f'{EN}/blog/{p["slug"]}/', 'datePublished': p['date'].isoformat()} for p in posts[:20]]}
io.open(OUT + 'blog/index.html', 'w', encoding='utf-8').write(page(
    'FDAM Blog | Franchise Operations Insights', 'Practical insights for franchisor headquarters on store openings, e-contracts, logistics, unified sales and AI-driven franchise operations, from the FDAM team.',
    '/blog/', lst, EN + '/assets/og/og-blog.png',
    f'<link href="{EN}/blog/" hreflang="en" rel="alternate"/><link href="{KO}/blog" hreflang="ko" rel="alternate"/><link href="{KO}/blog" hreflang="x-default" rel="alternate"/>'
    f'<script type="application/ld+json">{json.dumps(ld_list, ensure_ascii=False)}</script>'))

# ---------- posts ----------
for i, p in enumerate(posts):
    related = [q for q in posts if q is not p][:3] if i > 2 else [q for q in posts if q is not p][3:6]
    body = (f'<article class="eb-article"><div class="container eb-narrow">'
            f'<a class="eb-back" href="/blog/">← All articles</a>'
            f'<time datetime="{p["date"].date()}">{fmt(p["date"])}</time><h1>{html.escape(p["title"])}</h1>'
            f'<div class="eb-content">{fix_links(p["html"])}</div>{CTA}</div></article>'
            f'<section class="eb-related"><div class="container"><h2>More from the FDAM blog</h2><div class="eb-grid">{"".join(card(q) for q in related)}</div></div></section>')
    ld = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['title'], 'description': p['description'],
          'datePublished': p['date'].isoformat(), 'dateModified': p['date'].isoformat(), 'inLanguage': 'en',
          'mainEntityOfPage': f'{EN}/blog/{p["slug"]}/', 'image': p['image'] or None,
          'author': {'@type': 'Organization', 'name': 'FDAM', '@id': KO + '/#fdam'}, 'publisher': {'@id': KO + '/#org'}}
    ko_url = f'{KO}/blog/?idx={p["idx"]}&amp;bmode=view'
    head = (f'<meta content="article" property="og:type"/><meta content="{p["date"].isoformat()}" property="article:published_time"/>'
            f'<link href="{EN}/blog/{p["slug"]}/" hreflang="en" rel="alternate"/><link href="{ko_url}" hreflang="ko" rel="alternate"/>'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
    os.makedirs(OUT + 'blog/' + p['slug'], exist_ok=True)
    io.open(OUT + 'blog/' + p['slug'] + '/index.html', 'w', encoding='utf-8').write(
        page(p['title'] + ' | FDAM Blog', p['description'], f'/blog/{p["slug"]}/', body, p['image'] or EN + '/assets/og/og-blog.png', head))

# ---------- rss + sitemap ----------
items = ''.join(f'<item><title>{html.escape(p["title"])}</title><link>{EN}/blog/{p["slug"]}/</link><guid>{EN}/blog/{p["slug"]}/</guid>'
                f'<pubDate>{p["date"].strftime("%a, %d %b %Y %H:%M:%S %z")}</pubDate><description>{html.escape(p["description"])}</description></item>' for p in posts[:50])
io.open(OUT + 'blog/rss.xml', 'w', encoding='utf-8').write(
    f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>FDAM Blog</title><link>{EN}/blog/</link>'
    f'<description>Franchise operations insights from FDAM</description><language>en</language>{items}</channel></rss>')
sm = io.open(OUT + 'sitemap.xml', encoding='utf-8').read()
add = f'  <url>\n    <loc>{EN}/blog/</loc>\n  </url>\n' + ''.join(
    f'  <url>\n    <loc>{EN}/blog/{p["slug"]}/</loc>\n    <lastmod>{p["date"].date()}</lastmod>\n  </url>\n' for p in posts)
sm = re.sub(r'  <url>\n    <loc>[^<]*/blog/[\s\S]*?</url>\n', '', sm).replace('</urlset>', add + '</urlset>')
io.open(OUT + 'sitemap.xml', 'w', encoding='utf-8').write(sm)

# ---------- css ----------
io.open(OUT + 'assets/blog.css', 'w', encoding='utf-8').write(io.open('blog.css', encoding='utf-8').read())
left = sum(len(re.findall('[가-힣]', io.open(f, encoding='utf-8').read())) for f in glob.glob(OUT + 'blog/**/*.html', recursive=True))
print('posts', len(posts), '| hangul in blog pages', left, '| slugs unique', len({p['slug'] for p in posts}) == len(posts))

# ---------- Korean <-> English post map (read by the Korean site's head code) + GitHub Pages files ----------
io.open(OUT + 'blog/map.json', 'w', encoding='utf-8').write(json.dumps({p['idx']: p['slug'] for p in posts}, separators=(',', ':')))
io.open(OUT + 'CNAME', 'w', encoding='utf-8').write('en.fdam.co.kr\n')
io.open(OUT + '.nojekyll', 'w', encoding='utf-8').write('')
