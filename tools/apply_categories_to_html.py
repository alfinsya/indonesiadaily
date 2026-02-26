#!/usr/bin/env python3
import os
import json
import re
from glob import glob

ROOT = os.path.dirname(os.path.dirname(__file__))
ART = os.path.join(ROOT, 'articles.json')

def load_mapping():
    with open(ART, 'r', encoding='utf-8') as f:
        data = json.load(f)
    m = {}
    for a in data:
        url = a.get('url','').lstrip('/')
        cat = a.get('category','')
        if url:
            m[url] = cat
    return m

BADGE_RE = re.compile(r'(<(?:a|span)[^>]*class="[^"]*badge[^"]*"[^>]*>)(.*?)(</(?:a|span)>)', re.I|re.S)

def replace_nearest_badge(content, pos, new_text):
    # search backwards from pos for badge tag within 400 chars
    start = max(0, pos-400)
    segment = content[start:pos]
    # find last badge in segment
    matches = list(BADGE_RE.finditer(segment))
    if not matches:
        return content, False
    last = matches[-1]
    span_start = start + last.start(2)
    span_end = start + last.end(2)
    # replace inner text
    new_content = content[:span_start] + new_text + content[span_end:]
    return new_content, True

def process_file(path, mapping):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    changed = False
    for url, cat in mapping.items():
        # look for both relative and absolute hrefs
        for href in (f'href="{url}"', f'href="/{url}"'):
            start = 0
            while True:
                idx = content.find(href, start)
                if idx == -1:
                    break
                # replace nearest preceding badge
                content, ok = replace_nearest_badge(content, idx, cat)
                if ok:
                    changed = True
                start = idx + len(href)
    if changed:
        bak = path + '.bak'
        if not os.path.exists(bak):
            os.rename(path, bak)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
    return changed

def main():
    mapping = load_mapping()
    # process root html files and article/*.html
    files = glob(os.path.join(ROOT, '*.html')) + glob(os.path.join(ROOT, 'article', '*.html'))
    total_changed = 0
    for p in files:
        changed = process_file(p, mapping)
        if changed:
            print('Updated', p)
            total_changed += 1
    print('Done. Files updated:', total_changed)

if __name__ == '__main__':
    main()
