import os
import re
from pathlib import Path

# Find all unique profile image filenames in article comments
profile_images = set()

article_dir = Path("article")

# Pattern to find profile images in src attributes
# Looking for ../img/user*.jpg or ../img/user*.png patterns
pattern = r'src=["\']\.\.\/img\/(user[^"\']*(?:\.jpg|\.png))["\']'

for html_file in sorted(article_dir.glob("*.html")):
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        matches = re.findall(pattern, content)
        for match in matches:
            profile_images.add(match)

# Sort and display results
sorted_images = sorted(profile_images)
print("Profile image filenames used in comments:")
print("=" * 50)
for img in sorted_images:
    print(f"  img/{img}")

print("\n" + "=" * 50)
print(f"Total unique profile images: {len(sorted_images)}")
print("\nYou can rename these files or replace them with:")
print("  img/user1.jpg, img/user2.jpg, img/user3.jpg, etc.")
