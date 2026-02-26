import os
import re
from pathlib import Path

article_dir = Path("../article")

# Pattern untuk find img di trending news
# <img class="img-fluid" src="../img/...">
# Kita tambahkan style untuk fix size dan maintain aspect ratio

updated_files = []

for html_file in sorted(article_dir.glob("*.html")):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Find trending news section (between "Trending News" heading and next section)
    # Pattern: <h4...>Trending News</h4> ... <img class="img-fluid" ...>
    
    # More specific: match img tags within trending news that don't have style attribute with width/height
    pattern = r'(<div class="section-title mb-0">\s*<h4[^>]*>Trending News</h4>\s*</div>.*?<img class="img-fluid"\s+src="([^"]*)")'
    
    # Find all trending news sections and update their images
    def replace_trending_img(match):
        full_match = match.group(1)
        img_src = match.group(2)
        
        # Replace with styled version
        return full_match.replace(
            '<img class="img-fluid" src="',
            '<img class="img-fluid" style="width: 110px; height: 110px; object-fit: cover;" src="'
        )
    
    # Find and replace all img tags in trending news sections
    # Simpler approach: find all img with class="img-fluid" that come right after trending news items
    pattern_simple = r'<a href="[^"]+\.html">\s*<img class="img-fluid" src="'
    
    def replace_simple(match):
        return match.group(0).replace(
            '<img class="img-fluid" src="',
            '<img class="img-fluid" style="width: 110px; height: 110px; object-fit: cover;" src="'
        )
    
    content = re.sub(pattern_simple, replace_simple, content)
    
    if content != original:
        # Backup
        backup_path = html_file.with_suffix('.bak.imgresize')
        if not backup_path.exists():
            backup_path.write_text(original, encoding='utf-8')
        
        html_file.write_text(content, encoding='utf-8')
        updated_files.append(html_file.name)

print("=" * 70)
print("TRENDING NEWS IMAGE SIZE ADJUSTMENT")
print("=" * 70)
print(f"\nFiles updated: {len(updated_files)}")
for f in sorted(updated_files)[:20]:
    print(f"  ✓ {f}")
if len(updated_files) > 20:
    print(f"  ... and {len(updated_files) - 20} more")

print("\n" + "=" * 70)
print("Changes made:")
print("  - Added style to trending news images")
print("  - Fixed size: 110x110px")
print("  - object-fit: cover (maintain aspect ratio)")
print("=" * 70)
