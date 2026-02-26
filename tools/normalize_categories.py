#!/usr/bin/env python3
import json
import shutil
import time
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
ART = os.path.join(ROOT, 'articles.json')

CANONICAL = [
    'Lingkungan',
    'Pangan',
    'Hukum',
    'Keamanan',
    'Ekonomi',
    'Pendidikan',
    'Olahraga',
    'Teknologi',
    'Kesehatan',
    'Budaya'
]

# keywords -> canonical mapping (checked in order)
KEYWORDS = [
    (['environment','lingkungan','env'], 'Lingkungan'),
    (['pangan','food','foods','agriculture','ketahanan pangan'], 'Pangan'),
    (['law','hukum','crime','criminal','law & crime','law&crime'], 'Hukum'),
    (['security','keamanan','pengamanan'], 'Keamanan'),
    (['economy','ekonomi','business','bisnis','ekonom'], 'Ekonomi'),
    (['education','pendidikan','edukasi','school','sekolah','mahasiswa','siswa'], 'Pendidikan'),
    (['sport','sports','olahraga','pertandingan'], 'Olahraga'),
    (['technology','teknologi','tech','digital','digitalisasi'], 'Teknologi'),
    (['health','kesehatan','clinic','rumah sakit','sehat'], 'Kesehatan'),
    (['culture','budaya','kebudayaan'], 'Budaya'),
]

def normalize(cat):
    if not cat:
        return 'Ekonomi'
    s = str(cat).strip().lower()
    for keys, canon in KEYWORDS:
        for k in keys:
            if k in s:
                return canon
    # try splitting by common delimiters
    for part in [p.strip() for p in s.replace('&',' ').replace('/', ' ').split() if p.strip()]:
        for keys, canon in KEYWORDS:
            if part in keys:
                return canon
    # fallback: if the category contains Indonesian words map heuristically
    if any(x in s for x in ['lingkungan','hutan','tanam','longsor']):
        return 'Lingkungan'
    if any(x in s for x in ['ekonomi','koperasi','usaha','umkm','perekonomian']):
        return 'Ekonomi'
    return 'Ekonomi'

def main():
    if not os.path.exists(ART):
        print('articles.json not found at', ART)
        return
    ts = int(time.time())
    bak = ART + f'.bak.{ts}'
    shutil.copy2(ART, bak)
    print('Backup created:', bak)

    with open(ART, 'r', encoding='utf-8') as f:
        data = json.load(f)

    counts = {}
    for a in data:
        old = a.get('category','')
        new = normalize(old)
        a['category'] = new
        counts[new] = counts.get(new, 0) + 1

    with open(ART, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('Normalized categories written to', ART)
    print('Category counts:')
    for c in CANONICAL:
        if c in counts:
            print(f'  {c}: {counts[c]}')

if __name__ == '__main__':
    main()
