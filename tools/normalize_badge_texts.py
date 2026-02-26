#!/usr/bin/env python3
import re
import os
from glob import glob

ROOT = os.path.dirname(os.path.dirname(__file__))

MAP = {
    # environment
    r'^(environment|env|lingkungan)$': 'Lingkungan',
    # pangan
    r'^(pangan|foods?|food|agriculture|ketahanan pangan)$': 'Pangan',
    # hukum
    r'^(hukum|law|crime|law & crime|law&crime)$': 'Hukum',
    # keamanan
    r'^(keamanan|security)$': 'Keamanan',
    # ekonomi
    r'^(economy|ekonomi|business|bisnis)$': 'Ekonomi',
    # pendidikan
    r'^(education|pendidikan|edukasi|sekolah|mahasiswa|siswa)$': 'Pendidikan',
    # olahraga
    r'^(sports?|olahraga)$': 'Olahraga',
    # teknologi
    r'^(technology|teknologi|tech|digital|digitalisasi)$': 'Teknologi',
    # kesehatan
    r'^(health|kesehatan)$': 'Kesehatan',
    # budaya
    r'^(culture|budaya|kebudayaan)$': 'Budaya'
}

BADGE_RE = re.compile(r'(<(?:a|span)[^>]*class="[^"]*badge[^"]*"[^>]*>)(.*?)(</(?:a|span)>)', re.I|re.S)

def normalize_text(text):
    s = text.strip().lower()
    for pat, out in MAP.items():
        if re.search(pat, s, re.I):
            return out
    # handle multi-word like 'Law & Crime'
    if 'law' in s or 'crime' in s:
        return 'Hukum'
    if 'lingkungan' in s or 'environment' in s or 'hutan' in s:
        return 'Lingkungan'
    return None

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    changed = False
    def repl(m):
        nonlocal changed
        before, inner, after = m.group(1), m.group(2), m.group(3)
        new = normalize_text(inner)
        if new and new != inner.strip():
            changed = True
            return before + new + after
        return m.group(0)

    new_content = BADGE_RE.sub(repl, content)
    if changed:
        bak = path + '.badgebak'
        if not os.path.exists(bak):
            os.rename(path, bak)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('Updated badges in', path)

def main():
    files = glob(os.path.join(ROOT, '*.html')) + glob(os.path.join(ROOT, 'article', '*.html')) + glob(os.path.join(ROOT, 'js', '*.html'))
    for p in files:
        process_file(p)

if __name__ == '__main__':
    main()
