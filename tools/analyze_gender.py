import os
import re
from pathlib import Path
from collections import defaultdict

# Indonesian female name indicators
female_names = {
    'ira', 'siti', 'ani', 'ina', 'tin', 'sih', 'sri', 'dwi', 'fitri', 'lestari', 'kartika', 
    'permata', 'intan', 'nina', 'rika', 'rina', 'salsa', 'sari', 'sinta', 'yani', 'yuni', 
    'rahmah', 'rahmawati', 'nurhaliza', 'nurhayati', 'nurjanah', 'aisyah', 'aminah', 'nurul',
    'handayani', 'mulyani', 'wahyuni', 'kurniawati', 'anggraini', 'aulia', 'azizah', 'hidayah',
    'anita', 'dewi', 'fitri', 'novi', 'nur', 'nurhayati', 'rahma', 'sulastri', 'andayani',
    'hayati', 'uyung', 'endang', 'endang', 'endih', 'nurma', 'rohma', 'tatik', 'tutik'
}

article_dir = Path("article")

# Pattern to find user names in comments
user_pattern = r'<h6><b>([^<]+)</b>\s*<small><i>.*?</i></small></h6>'

users_by_gender = {
    'female': set(),
    'male': set()
}

for html_file in sorted(article_dir.glob("*.html")):
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        matches = re.findall(user_pattern, content)
        for user in matches:
            # Simple gender detection - check first name
            first_name = user.split()[0].lower()
            
            # Check if female name
            if any(female_indicator in first_name for female_indicator in female_names):
                users_by_gender['female'].add(user)
            else:
                users_by_gender['male'].add(user)

print("=" * 70)
print("FEMALE USERS:")
print("=" * 70)
for i, user in enumerate(sorted(users_by_gender['female']), 1):
    print(f"{i:2d}. {user}")

print(f"\nTotal: {len(users_by_gender['female'])}")

print("\n" + "=" * 70)
print("MALE USERS:")
print("=" * 70)
for i, user in enumerate(sorted(users_by_gender['male']), 1):
    print(f"{i:2d}. {user}")

print(f"\nTotal: {len(users_by_gender['male'])}")

print("\n" + "=" * 70)
print(f"Grand Total: {len(users_by_gender['female']) + len(users_by_gender['male'])}")
