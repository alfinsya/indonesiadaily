import os
import re
import json
from pathlib import Path

# Load user to image mapping
with open('user_image_mapping.json', 'r', encoding='utf-8') as f:
    user_to_image = json.load(f)

article_dir = Path("../article")

updated_files = []

for html_file in sorted(article_dir.glob("*.html")):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # For each user, find their comment and update the img src
    # Pattern: find img tag, then look ahead for the user name
    for user_name, image_file in user_to_image.items():
        # Find all occurrences of this user in comments
        # Pattern: <img src="../img/XXX" ... > ... <h6><b>UserName</b>
        
        # More flexible pattern - find img followed eventually by user name
        pattern = rf'<img\s+src="\.\./img/[^"]*"([^>]*?)>\s*<div class="media-body">\s*<h6><b>{re.escape(user_name)}</b>'
        replacement = rf'<img src="../img/{image_file}"\1><div class="media-body"><h6><b>{user_name}</b>'
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            content = new_content
    
    # Replace reporter - any rounded-circle img at top of article
    content = re.sub(
        r'<img class="rounded-circle mr-2" src="\.\./img/[^"]*\.jpg" width="25" height="25" alt="">',
        '<img class="rounded-circle mr-2" src="../img/alfin.jpg" width="25" height="25" alt="">',
        content
    )
    
    # If content changed, save it
    if content != original:
        # Backup
        backup_path = html_file.with_suffix('.bak.final')
        if not backup_path.exists():
            backup_path.write_text(original, encoding='utf-8')
        
        html_file.write_text(content, encoding='utf-8')
        updated_files.append(html_file.name)

print("=" * 70)
print("PROFILE IMAGE UPDATE - FINAL")
print("=" * 70)
print(f"\nFiles updated: {len(updated_files)}")
for f in sorted(updated_files):
    print(f"  ✓ {f}")

print("\n" + "=" * 70)
if len(updated_files) > 0:
    print("SUCCESS! All files updated with correct profile images.")
else:
    print("WARNING: No files were updated. Check patterns.")
print("=" * 70)
