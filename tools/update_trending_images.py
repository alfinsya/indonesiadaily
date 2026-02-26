import os
import re
import json
from pathlib import Path

# Load article to image mapping
with open('article_images.json', 'r') as f:
    article_images = json.load(f)

article_dir = Path("../article")

# Pattern untuk find trending news section 
# Format: <a href="FILENAME.html"> ... <img src="..../img/XXX" ... >

updated_files = []

for html_file in sorted(article_dir.glob("*.html")):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Find all trending news items in this article
    # Pattern: <a href="(filename\.html)"> ... <img ... src="[^"]*" ... > ... </a>
    trending_pattern = r'<a href="([^"]+\.html)">\s*<img[^>]*src="[^"]*"'
    
    for match in re.finditer(trending_pattern, content):
        target_article = match.group(1)
        old_tag = match.group(0)
        
        # Get the image for this article
        if target_article in article_images:
            target_image = article_images[target_article]
            # Replace the img src in the trending news
            new_tag = re.sub(
                r'src="[^"]*"',
                f'src="../img/{target_image}"',
                old_tag
            )
            content = content.replace(old_tag, new_tag)
    
    if content != original:
        # Backup
        backup_path = html_file.with_suffix('.bak.trending')
        if not backup_path.exists():
            backup_path.write_text(original, encoding='utf-8')
        
        html_file.write_text(content, encoding='utf-8')
        updated_files.append(html_file.name)

print("=" * 70)
print("TRENDING NEWS IMAGES UPDATE")
print("=" * 70)
print(f"\nFiles updated: {len(updated_files)}")
for f in sorted(updated_files)[:20]:
    print(f"  ✓ {f}")
if len(updated_files) > 20:
    print(f"  ... and {len(updated_files) - 20} more")

print("\n" + "=" * 70)
print("Changes made:")
print("  - Trending News images now use actual article featured images")
print("  - Template images (news-110x110-X.jpg) replaced with real images")
print("=" * 70)
