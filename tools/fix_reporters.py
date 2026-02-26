#!/usr/bin/env python3
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(__file__))
ARTICLE_DIR = os.path.join(ROOT, 'article')

pattern = re.compile(r'(?:<img[^>]*src="[^"]*"[^>]*>\s*)?<span>\s*Reporter:\s*[^<]+</span>', re.IGNORECASE)
replacement = '<img class="rounded-circle mr-2" src="../img/alfin.jpg" width="25" height="25" alt=""><span>Reporter: Alfin Syawalan</span>'

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    if not pattern.search(data):
        return False
    new = pattern.sub(replacement, data)
    # backup
    bak_path = f"{path}.bak.{int(time.time())}"
    with open(bak_path, 'w', encoding='utf-8') as bf:
        bf.write(data)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new)
    return True

def main():
    changed = []
    for dirpath, dirs, files in os.walk(ARTICLE_DIR):
        for fn in files:
            if fn.lower().endswith('.html') or fn.lower().endswith('.htm'):
                path = os.path.join(dirpath, fn)
                try:
                    if process_file(path):
                        changed.append(os.path.relpath(path, ROOT))
                except Exception as e:
                    print(f'ERROR processing {path}: {e}')
    print('\nFiles changed:')
    for p in changed:
        print(' -', p)
    print(f'\nTotal: {len(changed)} files updated')

if __name__ == '__main__':
    main()
