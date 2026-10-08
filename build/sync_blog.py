# Fetch Korean blog posts from fdam.co.kr and prepare cleaned sources for translation (blog/ko -> blog/clean).
import subprocess, sys, os, glob, io, json, re
from bs4 import BeautifulSoup, Comment

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(ROOT, 'blog'))
subprocess.run([sys.executable, 'fetch_posts.py'], check=True)
os.chdir(ROOT)
KEEP = {'href', 'src', 'alt', 'colspan', 'rowspan'}
for f in glob.glob('blog/ko/*.json'):
    out = 'blog/clean/' + os.path.basename(f)
    if os.path.exists(out):
        continue
    p = json.load(io.open(f, encoding='utf-8'))
    p['title'] = re.sub(r'\s*:\s*프담\(fdam\) 블로그.*$', '', p['title']).strip()
    soup = BeautifulSoup(p['html'], 'html.parser')
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    for t in soup.find_all(True):
        t.attrs = {k: v for k, v in t.attrs.items() if k in KEEP}
    for t in soup.find_all(['span', 'font', 'u']):
        t.unwrap()
    for t in soup.find_all('div'):
        if t.find(['table', 'img', 'h2', 'h3', 'ul', 'ol', 'p']) is None and t.get_text(strip=True):
            t.name = 'p'
        else:
            t.unwrap()
    for t in soup.find_all('p'):
        if not t.get_text(strip=True) and not t.find('img'):
            t.decompose()
    p['html'] = re.sub(r'\n\s*\n+', '\n', str(soup))
    json.dump(p, io.open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    print('new post', p['idx'], p['title'][:60])
done = {os.path.basename(f) for f in glob.glob('blog/en/*.json')}
todo = [f for f in glob.glob('blog/clean/*.json') if os.path.basename(f) not in done]
print('Korean posts:', len(glob.glob('blog/clean/*.json')), '| English posts:', len(done), '| to translate:', len(todo))
