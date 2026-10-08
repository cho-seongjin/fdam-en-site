# Fetch every Korean blog post (list pages -> post pages) and keep the article body, title, date, cover image.
import io, re, json, os, time, html, urllib.request, ssl
from bs4 import BeautifulSoup

BASE = 'https://fdam.co.kr'
ctx = ssl.create_default_context()


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR'})
    return urllib.request.urlopen(req, context=ctx, timeout=30).read().decode('utf-8', 'ignore')


ids = []
for page in range(1, 12):
    s = get(f'{BASE}/blog/?page={page}')
    found = [i for i in dict.fromkeys(re.findall(r'idx=(\d+)', s)) if i not in ids]
    if not found:
        break
    ids += found
print('post ids', len(ids))

os.makedirs('ko', exist_ok=True)
posts = []
for i, idx in enumerate(ids):
    path = f'ko/{idx}.json'
    if os.path.exists(path):
        posts.append(json.load(io.open(path, encoding='utf-8'))); continue
    s = get(f'{BASE}/blog/?idx={idx}&bmode=view')
    soup = BeautifulSoup(s, 'html.parser')
    title = (soup.find('meta', property='og:title') or {}).get('content') or soup.title.get_text()
    title = re.sub(r'\s*:\s*프랜차이즈 ERP, 프담 블로그\s*$', '', title).strip()
    desc = (soup.find('meta', attrs={'name': 'description'}) or {}).get('content', '')
    img = (soup.find('meta', property='og:image') or {}).get('content', '')
    body = soup.select_one('.board_txt_area')
    date = ''
    d = soup.select_one('.board_view .date, .board_view time, ._post_date, .write-date')
    if d:
        date = d.get_text(' ', strip=True)
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', s) or re.search(r'(20\d\d[-.]\d\d[-.]\d\d)', d.get_text() if d else '')
    if m:
        date = m.group(1)
    if body is None:
        print('NO BODY', idx); continue
    for t in body.select('script,style,iframe[src*="facebook"]'):
        t.decompose()
    post = {'idx': idx, 'title': html.unescape(title), 'description': html.unescape(desc), 'image': img, 'date': date, 'html': body.decode_contents().strip()}
    json.dump(post, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False)
    posts.append(post)
    time.sleep(0.3)
print('saved', len(posts), 'chars', sum(len(BeautifulSoup(p['html'], 'html.parser').get_text()) for p in posts))
