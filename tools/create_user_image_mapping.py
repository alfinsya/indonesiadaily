import os
import re
import random
from pathlib import Path
from collections import defaultdict

# Female name indicators
female_indicators = {
    'ira', 'siti', 'ani', 'ina', 'tin', 'sih', 'sri', 'dwi', 'fitri', 'lestari', 'kartika', 
    'permata', 'intan', 'nina', 'rika', 'rina', 'salsa', 'sari', 'sinta', 'yani', 'yuni', 
    'rahmah', 'rahmawati', 'nurhaliza', 'nurhayati', 'nurjanah', 'aisyah', 'aminah', 'nurul',
    'handayani', 'mulyani', 'wahyuni', 'kurniawati', 'anggraini', 'aulia', 'azizah', 'hidayah',
    'anita', 'dewi', 'fitri', 'novi', 'nur', 'endang', 'endih', 'nurma', 'tatik', 'tutik'
}

# Create maps for user->image file
cewe_images = [f'cewe{i}.jpg' for i in range(1, 6)]  # cewe1-5.jpg
cowok_images = [f'cowok{i}.jpg' for i in range(1, 6)]  # cowok1-5.jpg

user_to_image = {}

article_dir = Path("../article")

# First pass: identify all users and assign them images
user_pattern = r'<h6><b>([^<]+)</b>\s*<small><i>.*?</i></small></h6>'

all_users = set()

for html_file in sorted(article_dir.glob("*.html")):
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        matches = re.findall(user_pattern, content)
        all_users.update(matches)

# Assign each user to an image
female_users = []
male_users = []

for user in sorted(all_users):
    first_name = user.split()[0].lower()
    is_female = any(ind in first_name for ind in female_indicators)
    
    if is_female:
        female_users.append(user)
    else:
        male_users.append(user)

# Distribute images - cycle through available images
for i, user in enumerate(female_users):
    user_to_image[user] = cewe_images[i % len(cewe_images)]

for i, user in enumerate(male_users):
    user_to_image[user] = cowok_images[i % len(cowok_images)]

print("User -> Image Mapping:")
print("=" * 70)

print("\nFEMALE USERS:")
for user in sorted(female_users):
    print(f"  {user:25} -> img/{user_to_image[user]}")

print("\nMALE USERS:")
for user in sorted(male_users):
    print(f"  {user:25} -> img/{user_to_image[user]}")

# Save mapping to file for use in next script
import json
with open('user_image_mapping.json', 'w') as f:
    json.dump(user_to_image, f, indent=2)

print("\n" + "=" * 70)
print("Mapping saved to user_image_mapping.json")
print(f"Ready to update HTML files!")
