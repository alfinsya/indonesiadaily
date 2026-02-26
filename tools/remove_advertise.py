import io
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def read_file(path):
    with io.open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


def remove_advertise_from_content(content):
    changed = False
    search = 'Advertise'
    idx = content.find(search)
    while idx != -1:
        # try to remove surrounding <li ...>...</li>
        li_start = content.rfind('<li', 0, idx)
        li_end = content.find('</li>', idx)
        if li_start != -1 and li_end != -1:
            li_end += len('</li>')
            content = content[:li_start] + content[li_end:]
            changed = True
        else:
            # fallback: remove the <a ...>Advertise</a>
            a_start = content.rfind('<a', 0, idx)
            a_end = content.find('</a>', idx)
            if a_start != -1 and a_end != -1:
                a_end += len('</a>')
                content = content[:a_start] + content[a_end:]
                changed = True
            else:
                # cannot find surrounding tags; remove the word only
                content = content[:idx] + content[idx+len(search):]
                changed = True
        idx = content.find(search, idx)
    return content, changed


def process_all_html():
    updated = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for name in filenames:
            if not name.lower().endswith('.html'):
                continue
            path = os.path.join(dirpath, name)
            content = read_file(path)
            new_content, changed = remove_advertise_from_content(content)
            if changed:
                write_file(path, new_content)
                updated.append(path)
    return updated


def main():
    updated = process_all_html()
    print(f"Removed 'Advertise' from {len(updated)} files")
    for p in updated:
        print(p)


if __name__ == '__main__':
    main()
