import io
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def read_file(path):
    with io.open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

def extract_footer_from_index(index_path):
    content = read_file(index_path)
    start_marker = '<!-- Footer Start -->'
    end_marker = '<!-- Footer End -->'
    si = content.find(start_marker)
    ei = content.find(end_marker, si)
    if si == -1 or ei == -1:
        raise RuntimeError('Footer markers not found in index.html')
    ei += len(end_marker)
    footer = content[si:ei]
    # update the email to open Gmail compose explicitly
    # Replace only the email paragraph (avoid replacing inside attributes)
    email_icon_pos = footer.find('fa-envelope')
    if email_icon_pos != -1:
        # find start of <p before icon
        p_start = footer.rfind('<p', 0, email_icon_pos)
        p_end = footer.find('</p>', email_icon_pos)
        if p_start != -1 and p_end != -1:
            p_end += len('</p>')
            new_email_p = '<p class="font-weight-medium text-white"><i class="fa fa-envelope mr-2"></i><a href="https://mail.google.com/mail/?view=cm&fs=1&to=IndonesiaDaily33@gmail.com" target="_blank" class="text-white">IndonesiaDaily33@gmail.com</a></p>'
            footer = footer[:p_start] + new_email_p + footer[p_end:]
    # Make internal links root-relative so they work from any folder
    import re
    def repl(m):
        url = m.group(1)
        # skip empty
        if url.startswith('#') or url.startswith('javascript:'):
            return f'href="{url}"'
        return f'href="/{url.lstrip("/")}"'

    footer = re.sub(r'href="(?!https?:|/|mailto:)([^"]+)"', repl, footer)
    return footer

def update_html_files(footer_html):
    updated_files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for name in filenames:
            if not name.lower().endswith('.html'):
                continue
            path = os.path.join(dirpath, name)
            # skip index.html (already source)
            if os.path.abspath(path) == os.path.abspath(os.path.join(ROOT, 'index.html')):
                # ensure index.html has the updated footer too
                content = read_file(path)
                start_marker = '<!-- Footer Start -->'
                end_marker = '<!-- Footer End -->'
                si = content.find(start_marker)
                ei = content.find(end_marker, si)
                if si != -1 and ei != -1:
                    ei += len(end_marker)
                    new_content = content[:si] + footer_html + content[ei:]
                    if new_content != content:
                        write_file(path, new_content)
                        updated_files.append(path)
                continue

            content = read_file(path)
            start_marker = '<!-- Footer Start -->'
            end_marker = '<!-- Footer End -->'
            si = content.find(start_marker)
            ei = content.find(end_marker, si)
            if si == -1 or ei == -1:
                continue
            ei += len(end_marker)
            new_content = content[:si] + footer_html + content[ei:]
            if new_content != content:
                write_file(path, new_content)
                updated_files.append(path)
    return updated_files

def main():
    index_path = os.path.join(ROOT, 'index.html')
    footer_html = extract_footer_from_index(index_path)
    updated = update_html_files(footer_html)
    print('Updated {} files'.format(len(updated)))
    for p in updated:
        print(p)

if __name__ == '__main__':
    main()
