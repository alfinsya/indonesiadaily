#!/usr/bin/env python3
import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ARTICLE_DIR = os.path.join(BASE_DIR, 'article')
OUT_FILE = os.path.join(BASE_DIR, 'articles.json')

def text_between(pattern, text, flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ''

def clean_path(src):
    if not src:
        return ''
    # normalize ../img/... -> img/...
    src = src.strip()
    src = re.sub(r'^\.\./', '', src)
    src = re.sub(r'^/', '', src)
    return src

def parse_file(path, rel_url):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        s = f.read()

    title = text_between(r'<title>(.*?)</title>', s, re.S|re.I)
    # remove site suffix if present
    title = re.sub(r'\s*-\s*Indonesia Daily$', '', title).strip()

    # Find the main article image: look for "img-fluid w-100" (main article image with width 100%)
    img = ''
    m = re.search(r'<img[^>]*class="[^"]*img-fluid\s+w-100[^"]*"[^>]*src=["\']([^"\']+)["\']', s, re.I)
    if m:
        img = clean_path(m.group(1))
    
    # If not found, try img-fluid w-100 with reversed attribute order
    if not img:
        m = re.search(r'<img[^>]*class="[^"]*w-100\s+[^"]*img-fluid[^"]*"[^>]*src=["\']([^"\']+)["\']', s, re.I)
        if m:
            img = clean_path(m.group(1))
    
    # If still not found, try any non-ad image with img-fluid class as fallback
    if not img:
        for m in re.finditer(r'<img[^>]*class="[^"]*img-fluid[^"]*"[^>]*src=["\']([^"\']+)["\']', s, re.I):
            candidate = clean_path(m.group(1))
            if 'ads' not in candidate.lower() and 'user.jpg' not in candidate.lower() and candidate:
                img = candidate
                break
    
    # category: look for first badge
    category = text_between(r'<(?:a|span)[^>]*class="[^"]*badge[^"]*"[^>]*>(.*?)</(?:a|span)>', s, re.S|re.I)

    # first date-like substring (e.g., Jan 1, 2026)
    date = ''
    m = re.search(r'([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})', s)
    if m:
        date = m.group(1).strip()

    # first paragraph as excerpt
    excerpt = text_between(r'<p>(.*?)</p>', s, re.S|re.I)
    excerpt = re.sub(r'<[^>]+>', '', excerpt)
    excerpt = ' '.join(excerpt.split())[:280]

    return {
        'title': title,
        'excerpt': excerpt,
        'category': category,
        'date': date,
        'image': img,
        'url': rel_url.replace('\\\\', '/'),
    }

def build_index():
    items = []
    if not os.path.isdir(ARTICLE_DIR):
        print('Article directory not found:', ARTICLE_DIR)
        return

    for fn in sorted(os.listdir(ARTICLE_DIR)):
        if not fn.lower().endswith('.html'):
            continue
        path = os.path.join(ARTICLE_DIR, fn)
        rel = 'article/' + fn
        item = parse_file(path, rel)
        # Set default placeholder image if not found
        if not item['image']:
            item['image'] = 'img/placeholder-article.png'
        items.append(item)

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print('Wrote', OUT_FILE, 'with', len(items), 'items')

if __name__ == '__main__':
    build_index()
