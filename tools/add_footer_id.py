#!/usr/bin/env python3
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(__file__))

pattern_h5 = re.compile(r"<h5[^>]*>\s*Kategori\s*</h5>", re.IGNORECASE)
pattern_div = re.compile(r"<div([^>]*)class=[\'\"]([^\"'>]*)[\'\"]([^>]*)>", re.IGNORECASE)

modified = []

for dirpath, dirs, files in os.walk(ROOT):
    for fn in files:
        if not fn.endswith('.html'): continue
        if fn.endswith('.bak') or fn.endswith('.badgebak'): continue
        path = os.path.join(dirpath, fn)
        try:
            with io.open(path, 'r', encoding='utf-8') as f:
                s = f.read()
        except Exception:
            continue

        m = pattern_h5.search(s)
        if not m:
            continue
        # search for next div after the h5
        start = m.end()
        mdiv = pattern_div.search(s, pos=start)
        if not mdiv:
            continue
        full = mdiv.group(0)
        attrs_before = mdiv.group(1) or ''
        class_val = mdiv.group(2) or ''
        attrs_after = mdiv.group(3) or ''
        # only target footer category container which usually has flex-wrap
        if 'flex-wrap' not in class_val and 'flexwrap' not in class_val:
            # try a bit further (some files have nested structure)
            continue

        # if id already present, skip
        if re.search(r"\sid\s*=\s*[\"']footerCategories[\"']", full):
            continue

        # build replacement: add id="footerCategories" into opening div
        replacement = '<div' + attrs_before + ' id="footerCategories" class="' + class_val + '"' + attrs_after + '>'

        new_s = s[:mdiv.start()] + replacement + s[mdiv.end():]

        # backup
        bak = path + '.bak'
        with io.open(bak, 'w', encoding='utf-8') as f:
            f.write(s)
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(new_s)
        modified.append(path)

print('Files updated:', len(modified))
for p in modified[:200]:
    print(p)
