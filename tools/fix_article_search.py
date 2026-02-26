import os
import re
from pathlib import Path

article_dir = Path("../article")

# Pattern untuk find search form di artikel
# <div class="input-group d-none d-lg-flex" style="width: 260px;">
#     <input type="text" class="form-control" placeholder="Cari berita...">
#     <div class="input-group-append">
#         <button class="btn btn-primary">
#             <i class="fa fa-search"></i>
#         </button>
#     </div>
# </div>

# Kita perlu wrapping ini dengan <form> dan add attributes yang diperlukan

updated_files = []

for html_file in sorted(article_dir.glob("*.html")):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace search input form
    # Add action, method, dan name attribute
    
    # Pattern 1: Replace form structure dengan menambah form wrapper
    pattern = r'<!-- SEARCH KANAN -->\s*<div class="input-group d-none d-lg-flex" style="width: 260px;">\s*<input type="text" class="form-control" placeholder="Cari berita\.\.\.">\s*<div class="input-group-append">\s*<button class="btn btn-primary">\s*<i class="fa fa-search"></i>\s*</button>\s*</div>\s*</div>'
    
    replacement = '''<!-- SEARCH KANAN -->
            <form action="/search.html" method="get" class="input-group d-none d-lg-flex" style="width: 260px;">
                <input type="text" class="form-control" name="q" placeholder="Cari berita..." required>
                <div class="input-group-append">
                    <button class="btn btn-primary" type="submit">
                        <i class="fa fa-search"></i>
                    </button>
                </div>
            </form>'''
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if content != original:
        # Backup
        backup_path = html_file.with_suffix('.bak.search')
        if not backup_path.exists():
            backup_path.write_text(original, encoding='utf-8')
        
        html_file.write_text(content, encoding='utf-8')
        updated_files.append(html_file.name)

print("=" * 70)
print("SEARCH FORM FIX IN ARTICLES")
print("=" * 70)
print(f"\nFiles updated: {len(updated_files)}")
for f in sorted(updated_files)[:20]:
    print(f"  ✓ {f}")
if len(updated_files) > 20:
    print(f"  ... and {len(updated_files) - 20} more")

print("\n" + "=" * 70)
print("Changes made:")
print("  - Added <form action='/search.html' method='get'> wrapper")
print("  - Added name='q' to input field")
print("  - Added type='submit' to button")
print("  - Added required attribute to input")
print("=" * 70)
