import os
import re
from pathlib import Path

article_dir = Path("../article")

# Extract featured image dari setiap artikel
# Pattern: <img class="img-fluid w-100" src="../img/..." style="object-fit: cover;">
article_images = {}

for html_file in sorted(article_dir.glob("*.html")):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the featured image (first large image in the article)
    pattern = r'<img class="img-fluid w-100" src="\.\./img/([^"]+\.(?:jpg|png))"'
    match = re.search(pattern, content)
    
    if match:
        image_file = match.group(1)
        article_images[html_file.name] = image_file
        print(f"{html_file.name:30} -> {image_file}")

print("\n" + "=" * 70)
print(f"Total articles with featured images: {len(article_images)}")

# Save this mapping for next script
import json
with open('article_images.json', 'w') as f:
    json.dump(article_images, f, indent=2)

print("Mapping saved to article_images.json")
