import os
import re
import json
from pathlib import Path

# Load user to image mapping
with open('user_image_mapping.json', 'r', encoding='utf-8') as f:
    user_to_image = json.load(f)

article_dir = Path("../article")

updated_files = []
errors = []

for html_file in sorted(article_dir.glob("*.html")):
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Step 1: Replace all old user images in comments with placeholder
        # Find each <h6><b>UserName</b> and replace the img src before it
        
        for user_name, image_file in user_to_image.items():
            # Create a pattern that matches img tags followed (with flexible whitespace) by the user name
            # We'll search for img src attributes followed eventually by the user name
            
            # Pattern: <img ... src="../img/[anything]" ... > ... <h6><b>UserName</b>
            pattern = rf'(<img\s+[^>]*src=")[^"]*\.jpg"(\s+[^>]*?)><\s*div\s+class="media-body">\s*<h6><b>{re.escape(user_name)}</b>'
            replacement = rf'\1../img/{image_file}"\2><div class="media-body"><h6><b>{user_name}</b>'
            
            content = re.sub(pattern, replacement, content)
        
        # Step 2: Replace reporter/author alfin.jpg
        content = re.sub(
            r'<img class="rounded-circle mr-2" src="\.\./img/[^"]*"',
            '<img class="rounded-circle mr-2" src="../img/alfin.jpg"',
            content
        )
        
        # Write back if changed
        if content != original:
            # Create backup
            backup_path = html_file.with_suffix('.bak.newprofile')
            if not backup_path.exists():
                backup_path.write_text(original, encoding='utf-8')
            
            html_file.write_text(content, encoding='utf-8')
            updated_files.append(html_file.name)
    
    except Exception as e:
        errors.append(f"{html_file.name}: {str(e)}")

print("=" * 70)
print("PROFILE IMAGE UPDATE SUMMARY (ATTEMPT 2)")
print("=" * 70)
print(f"\nFiles updated: {len(updated_files)}")
if updated_files:
    for f in updated_files[:20]:
        print(f"  ✓ {f}")
    if len(updated_files) > 20:
        print(f"  ... and {len(updated_files) - 20} more")

if errors:
    print(f"\nErrors: {len(errors)}")
    for e in errors:
        print(f"  ✗ {e}")
else:
    print("\nNo errors!")

print("\n" + "=" * 70)
print("Changes made:")
print("  - Reporter/Author image -> ../img/alfin.jpg")
print("  - Comment images -> cewe1-5.jpg, cowok1-5.jpg (based on user gender)")
print("=" * 70)
