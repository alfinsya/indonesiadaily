import os
import re
import json
from pathlib import Path

# Load user to image mapping
with open('user_image_mapping.json', 'r') as f:
    user_to_image = json.load(f)

article_dir = Path("../article")

# Pattern to find reporter image and name
reporter_pattern = r'<img class="rounded-circle mr-2" src="\.\.\/img\/[^"]*\.jpg" width="25" height="25" alt="">\s*<span>Reporter: Ahmad Fauzi</span>'
reporter_replacement = '<img class="rounded-circle mr-2" src="../img/alfin.jpg" width="25" height="25" alt=""><span>Reporter: Alfin</span>'

updated_files = []
errors = []

for html_file in sorted(article_dir.glob("*.html")):
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 1. Replace reporter/author image to alfin.jpg
        # Find reporter line - it should appear early in the file
        reporter_lines = re.finditer(
            r'<img class="rounded-circle mr-2" src="\.\./img/[^"]*\.(?:jpg|png)" width="25" height="25" alt="">\s*<span>Reporter: [^<]+</span>',
            content
        )
        
        for match in reporter_lines:
            old_img = match.group(0)
            # Extract the reporter name
            reporter_name_match = re.search(r'Reporter: ([^<]+)<', old_img)
            if reporter_name_match:
                reporter_name = reporter_name_match.group(1)
                new_img = f'<img class="rounded-circle mr-2" src="../img/alfin.jpg" width="25" height="25" alt=""><span>Reporter: {reporter_name}</span>'
                content = content.replace(old_img, new_img, 1)
        
        # 2. Replace comment user images based on user name
        # Find all comments with user images and names
        comment_pattern = r'<img src="\.\./img/[^"]*\.(?:jpg|png)" alt="Image" class="img-fluid mr-3 mt-1" style="width: 45px;"><div class="media-body">\s*<h6><b>([^<]+)</b>'
        
        for match in re.finditer(comment_pattern, content):
            user_name = match.group(1)
            if user_name in user_to_image:
                old_img_tag = match.group(0).split('<div class="media-body">')[0]
                new_img_tag = f'<img src="../img/{user_to_image[user_name]}" alt="Image" class="img-fluid mr-3 mt-1" style="width: 45px;">'
                content = content.replace(old_img_tag, new_img_tag)
        
        # Write back if changed
        if content != original:
            # Create backup
            backup_path = html_file.with_suffix('.bak.profile')
            if not backup_path.exists():
                backup_path.write_text(original, encoding='utf-8')
            
            html_file.write_text(content, encoding='utf-8')
            updated_files.append(html_file.name)
    
    except Exception as e:
        errors.append(f"{html_file.name}: {str(e)}")

print("=" * 70)
print("PROFILE IMAGE UPDATE SUMMARY")
print("=" * 70)
print(f"\nFiles updated: {len(updated_files)}")
if updated_files:
    for f in updated_files:
        print(f"  ✓ {f}")

if errors:
    print(f"\nErrors: {len(errors)}")
    for e in errors:
        print(f"  ✗ {e}")
else:
    print("\nNo errors!")

print("\n" + "=" * 70)
print("Changes made:")
print("  - Reporter/Author image -> alfin.jpg")
print("  - Comment images -> mapped by user gender (cewe1-5.jpg, cowok1-5.jpg)")
print("  - Backups created with .bak.profile extension")
print("=" * 70)
