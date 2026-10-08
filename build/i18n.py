# Shared helpers: walk a page and yield translatable units (Korean text) in a stable order.
import re
from bs4 import BeautifulSoup, NavigableString, Comment

HANGUL = re.compile('[가-힣]')
INLINE = {'b', 'strong', 'span', 'em', 'i', 'br', 'mark', 'small', 'a', 'sup', 'sub', 'time', 'u', 'code', 'abbr'}
SKIP = {'script', 'style', 'svg', 'noscript'}
ATTRS = ['alt', 'aria-label', 'title', 'placeholder', 'data-title', 'data-copy', 'data-label']
META = {'description', 'og:title', 'og:description', 'twitter:title', 'twitter:description'}


def parse(text):
    return BeautifulSoup(text, 'html.parser')


def inline_only(el):
    return all((not hasattr(d, 'name')) or d.name is None or d.name in INLINE for d in el.descendants if not isinstance(d, (NavigableString,)) or True) and \
        all(getattr(d, 'name', None) in (None,) or d.name in INLINE for d in el.descendants if getattr(d, 'name', None))


def units(soup):
    """Yield (kind, node, key). kind: 'html' (replace inner html), 'text' (replace a text node), 'attr:<name>'."""
    out = []

    def walk(el):
        if getattr(el, 'name', None) in SKIP:
            return
        direct = [c for c in el.children if isinstance(c, NavigableString) and not isinstance(c, Comment) and HANGUL.search(str(c))]
        if direct and el.name not in ('[document]', 'html', 'body', 'head') and inline_only(el):
            out.append(('html', el, el.decode_contents().strip()))
        else:
            for c in list(el.children):
                if isinstance(c, Comment):
                    continue
                if isinstance(c, NavigableString):
                    if HANGUL.search(str(c)):
                        out.append(('text', c, str(c).strip()))
                elif getattr(c, 'name', None):
                    walk(c)
        if getattr(el, 'attrs', None):
            for a in ATTRS:
                v = el.attrs.get(a)
                if isinstance(v, str) and HANGUL.search(v):
                    out.append(('attr:' + a, el, v))
            if el.name == 'meta':
                key = el.attrs.get('name') or el.attrs.get('property')
                v = el.attrs.get('content')
                if key in META and isinstance(v, str) and HANGUL.search(v):
                    out.append(('attr:content', el, v))

    walk(soup)
    return out
