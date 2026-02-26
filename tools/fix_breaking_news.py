import io
import os

NEW_BLOCK = '''<!-- Breaking News Start -->
    <div class="container-fluid bg-dark py-3 mb-3">
        <div class="container">
            <div class="row align-items-center bg-dark">
                <div class="col-12">
                    <div class="d-flex justify-content-between">
                        <div class="bg-primary text-dark text-center font-weight-medium py-2" style="width: 170px;">Breaking News</div>
                        <div class="owl-carousel tranding-carousel position-relative d-inline-flex align-items-center ml-3"
                            style="width: calc(100% - 200px); padding-right: 90px;">
                            <div class="text-truncate"><a class="text-white text-uppercase font-weight-semi-bold" href="article/perhutani-majalengka.html">Perhutani KPH Majalengka Perkuat Sinergi dengan Kodim 0617 Majalengka</a></div>
                            <div class="text-truncate"><a class="text-white text-uppercase font-weight-semi-bold" href="article/longsor-bandung.html">Warga Korban Longsor Cisarua Sempat Lihat 2 Orang Diduga Anggota TNI</a></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Breaking News End -->'''

MARKER_START = '<!-- Breaking News Start -->'
MARKER_END = '<!-- Breaking News End -->'

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def process_file(path):
    with io.open(path, 'r', encoding='utf-8') as f:
        s = f.read()

    if MARKER_START in s and MARKER_END in s:
        start = s.index(MARKER_START)
        end = s.index(MARKER_END, start) + len(MARKER_END)
        new = s[:start] + NEW_BLOCK + s[end:]
        if new != s:
            # backup
            bak = path + '.bak.fixbreaking'
            with io.open(bak, 'w', encoding='utf-8') as f:
                f.write(s)
            with io.open(path, 'w', encoding='utf-8') as f:
                f.write(new)
            return True
    return False

def main():
    updated = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for fn in filenames:
            if fn.lower().endswith('.html'):
                path = os.path.join(dirpath, fn)
                try:
                    if process_file(path):
                        updated.append(os.path.relpath(path, ROOT))
                except Exception as e:
                    print(f'ERROR processing {path}: {e}')

    if updated:
        print('Updated files:')
        for p in updated:
            print(' -', p)
    else:
        print('No files updated.')

if __name__ == '__main__':
    main()
