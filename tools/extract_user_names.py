import os
import re
from pathlib import Path
from collections import defaultdict

# Find all unique user names in comments
user_names = set()
user_image_map = defaultdict(set)  # Map user name to image files used

article_dir = Path("article")

# Pattern to find user names in comments: <h6><b>UserName</b>
pattern = r'<h6><b>([^<]+)</b>\s*<small><i>.*?</i></small></h6>'

# Pattern to find image used before the comment
image_pattern = r'<img\s+src=["\']([^"\']*\.jpg|[^"\']*\.png)["\']'

for html_file in sorted(article_dir.glob("*.html")):
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        # Find all matches for user names
        matches = re.findall(pattern, content)
        for match in matches:
            user_names.add(match)

# Sort and display results
sorted_users = sorted(user_names)
print("Nama User dalam Komentar:")
print("=" * 70)
for i, user in enumerate(sorted_users, 1):
    print(f"{i:2d}. {user}")

print("\n" + "=" * 70)
print(f"Total unique user names: {len(sorted_users)}")
