# Translate Korean blog posts that have no English version yet (blog/clean/<id>.json -> blog/en/<id>.json) with the Claude API.
# Usage: python translate_new.py [--max N]      (needs ANTHROPIC_API_KEY)
import io, os, re, sys, json, glob, argparse
from collections import Counter
from html.parser import HTMLParser
import anthropic

MODEL = 'claude-opus-5-5'
HANGUL = re.compile('[가-힣]')
ROOT = os.path.dirname(os.path.abspath(__file__))
GLOSSARY = io.open(os.path.join(ROOT, 'glossary.md'), encoding='utf-8').read()

SYSTEM = f"""You translate Korean B2B blog posts for FDAM (an AI operations platform for franchises, made by MS Venter Co., Ltd.) into polished, natural US English for an international audience of franchisor executives.

Glossary and conventions (follow them exactly):
{GLOSSARY}

Extra conventions used across the English blog:
- Product names: 물류담 → Logidam, 발주닷컴 → Balju.com, 소담 → Sodam, 프담 → FDAM.
- 정보공개서 → franchise disclosure document; 사전제공문서 → pre-contract disclosure documents; 가맹사업법 → Franchise Business Act; 공정위/공정거래위원회 → Korea Fair Trade Commission; 가맹거래사 → certified franchise consultant.
- Korean-script domains such as 프랜차이즈ERP.com in visible text become fdam.co.kr (keep every href/src exactly as given).
- Currency: convert 만원/억원 to KRW millions/billions (e.g., 2억 5,526만 원 → KRW 255.26 million). Add "(Korea)" after the phone number 1544-7120.
- Briefly gloss Korea-specific things on first use only when an international reader would need it (e.g., Chuseok, Korea's autumn harvest holiday).

Output rules:
- html: translate the full article. Keep the HTML structure exactly: the same tags in the same order and the same href/src/alt/colspan/rowspan attributes (translate alt text, keep URLs). Translate every text node, including tables, headings, captions and FAQ. Do not add, drop or summarize content.
- title: English headline, ideally 70 characters or fewer, without any " : 프담(fdam) 블로그" suffix.
- description: a fresh 140-160 character meta description summarizing the post.
- slug: lowercase URL slug from the English title (a-z, 0-9, hyphens, 60 characters or fewer).
- No Korean characters may appear anywhere in the output."""

SCHEMA = {
    'type': 'object',
    'properties': {
        'slug': {'type': 'string'},
        'title': {'type': 'string'},
        'description': {'type': 'string'},
        'html': {'type': 'string'},
    },
    'required': ['slug', 'title', 'description', 'html'],
    'additionalProperties': False,
}


class TagCounter(HTMLParser):
    def __init__(self):
        super().__init__(); self.c = Counter()

    def handle_starttag(self, tag, attrs):
        self.c[tag] += 1


def tags(h):
    t = TagCounter(); t.feed(h); return t.c


def translate(client, post, feedback=''):
    prompt = (f"Translate this blog post. Source title: {post['title']}\n\nSource HTML:\n{post['html']}"
              + (f"\n\nYour previous attempt had problems, fix them: {feedback}" if feedback else ''))
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        system=SYSTEM,
        messages=[{'role': 'user', 'content': prompt}],
        output_config={'effort': 'medium', 'format': {'type': 'json_schema', 'schema': SCHEMA}},
        betas=['server-side-fallback-2026-07-01'],
        fallbacks='default',
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == 'refusal':
        raise RuntimeError(f'refused: {msg.stop_details}')
    if msg.stop_reason == 'max_tokens':
        raise RuntimeError('output hit max_tokens')
    text = next(b.text for b in msg.content if b.type == 'text')
    return json.loads(text), msg.usage


def problems(src, out):
    p = []
    left = sorted(set(HANGUL.findall(json.dumps(out, ensure_ascii=False))))
    if left:
        p.append('Korean characters remain: ' + ''.join(left[:40]))
    a, b = tags(src['html']), tags(out['html'])
    diff = {k: (a[k], b[k]) for k in set(a) | set(b) if a[k] != b[k]}
    if diff:
        p.append('HTML tag counts differ from the source (tag: source, yours): ' + json.dumps(diff))
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max', type=int, default=int(os.environ.get('MAX_POSTS', '5')))
    args = ap.parse_args()
    os.chdir(ROOT)
    done = {os.path.basename(f) for f in glob.glob('blog/en/*.json')}
    todo = sorted((f for f in glob.glob('blog/clean/*.json') if os.path.basename(f) not in done), key=os.path.basename)[: args.max]
    if not todo:
        print('nothing to translate'); return
    slugs = {json.load(io.open(f, encoding='utf-8'))['slug'] for f in glob.glob('blog/en/*.json')}
    client = anthropic.Anthropic()
    failed = 0
    for f in todo:
        src = json.load(io.open(f, encoding='utf-8'))
        try:
            out, usage = translate(client, src)
            p = problems(src, out)
            if p:
                out, usage = translate(client, src, ' '.join(p))
                p = problems(src, out)
            if any(x.startswith('Korean') for x in p):
                raise RuntimeError(p[0])
        except Exception as e:  # keep going with the other posts; the failed one is retried on the next run
            print('FAILED', src['idx'], e); failed += 1; continue
        slug = re.sub(r'[^a-z0-9-]+', '-', out['slug'].lower()).strip('-')[:60] or src['idx']
        while slug in slugs:
            slug = (slug[:52] + '-' + src['idx'][-6:])
        slugs.add(slug)
        rec = {'idx': src['idx'], 'slug': slug, 'title': out['title'], 'description': out['description'], 'html': out['html']}
        json.dump(rec, io.open(f'blog/en/{src["idx"]}.json', 'w', encoding='utf-8'), ensure_ascii=False)
        print('translated', src['idx'], slug, f'in={usage.input_tokens} out={usage.output_tokens}', ('WARN ' + p[0]) if p else '')
    if failed and failed == len(todo):
        sys.exit(1)


if __name__ == '__main__':
    main()
