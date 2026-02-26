import os
import re
import json
from pathlib import Path

# Load user to image mapping
with open('user_image_mapping.json', 'r', encoding='utf-8') as f:
    user_to_image = json.load(f)

article_dir = Path("../article")

# Female name indicators  
female_indicators = {
    'ira', 'siti', 'ani', 'ina', 'tin', 'sih', 'sri', 'dwi', 'fitri', 'lestari', 'kartika', 
    'permata', 'intan', 'nina', 'rika', 'rina', 'salsa', 'sari', 'sinta', 'yani', 'yuni', 
    'rahmah', 'rahmawati', 'nurhaliza', 'nurhayati', 'nurjanah', 'aisyah', 'aminah', 'nurul',
    'handayani', 'mulyani', 'wahyuni', 'kurniawati', 'anggraini', 'aulia', 'azizah', 'hidayah',
    'anita', 'dewi', 'fitri', 'novi', 'nur', 'endang', 'endih', 'nurma', 'tatik', 'tutik',
    'ibu', 'guru', 'lina', 'ningsih', 'wijaya', 'tini', 'yuni', 'suryani'
}

special_files = [
    'berita1.html', 'berita2.html', 'berita3.html', 
    'bojan-hodak.html', 'longsor-bandung.html', 'masih-ingat-resbob.html',
    'perhutani-majalengka.html'
]

# Extract unique user names from special files
special_users = set()
for filename in special_files:
    html_file = article_dir / filename
    if not html_file.exists():
        continue
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find names in <a> tags
    pattern_a = r'<a class="text-secondary font-weight-bold" href="">([^<]+)</a>'
    matches_a = re.findall(pattern_a, content)
    special_users.update(matches_a)

# Assign images to special users that aren't in mapping
cewe_images = [f'cewe{i}.jpg' for i in range(1, 6)]
cowok_images = [f'cowok{i}.jpg' for i in range(1, 6)]

cewe_counter = 0
cowok_counter = 0

extended_map = user_to_image.copy()

for user in sorted(special_users):
    if user not in extended_map:
        # Determine gender
        first_name = user.split()[0].lower()
        is_female = any(ind in first_name for ind in female_indicators)
        
        if is_female:
            extended_map[user] = cewe_images[cewe_counter % len(cewe_images)]
            cewe_counter += 1
        else:
            extended_map[user] = cowok_images[cowok_counter % len(cowok_images)]
            cowok_counter += 1

print("=" * 70)
print("SPECIAL USERS FOUND:")
print("=" * 70)
for user in sorted(special_users):
    img = extended_map[user]
    status = "NEW" if user not in user_to_image else "existing"
    print(f"  {user:25} -> img/{img:12} [{status}]")

# Now update the special files
updated_files = []

for filename in special_files:
    html_file = article_dir / filename
    if not html_file.exists():
        continue
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # For each user, find and replace their comment image
    for user_name, image_file in extended_map.items():
        # Pattern 1: Handle <a> tag version
        pattern_a = rf'<img\s+src="\.\./img/[^"]*"[^>]*>\s*<div[^>]* class="media-body">\s*<h6><a[^>]*>{re.escape(user_name)}</a>'
        replacement_a = rf'<img src="../img/{image_file}" alt="Image" class="img-fluid mr-3 mt-1" style="width: 45px;"><div class="media-body"><h6><a class="text-secondary font-weight-bold" href="">{user_name}</a>'
        
        content = re.sub(pattern_a, replacement_a, content)
        
        # Pattern 2: Handle <b> tag version
        pattern_b = rf'<img\s+src="\.\./img/[^"]*"[^>]*>\s*<div[^>]*>\s*<h6><b>{re.escape(user_name)}</b>'
        replacement_b = rf'<img src="../img/{image_file}" class="img-fluid mr-3 mt-1" style="width: 45px;"><div class="media-body"><h6><b>{user_name}</b>'
        
        content = re.sub(pattern_b, replacement_b, content)
    
    # Replace reporter
    content = re.sub(
        r'<img class="rounded-circle mr-2" src="\.\./img/[^"]*\.jpg" width="25" height="25" alt="">',
        '<img class="rounded-circle mr-2" src="../img/alfin.jpg" width="25" height="25" alt="">',
        content
    )
    
    if content != original:
        backup_path = html_file.with_suffix('.bak.special')
        if not backup_path.exists():
            backup_path.write_text(original, encoding='utf-8')
        
        html_file.write_text(content, encoding='utf-8')
        updated_files.append(filename)

print("\n" + "=" * 70)
print(f"Files updated: {len(updated_files)}")
for f in updated_files:
    print(f"  ✓ {f}")
print("=" * 70)
