import csv
import os
from pathlib import Path

# Map food names to existing local image files
FOOD_TO_IMAGE = {
    "Custard apple": "custard_apple.jpg",
    "Kiwi": "pear.png",  # Using available image as substitute
    "Dragon fruit": "dragon_fruit.jpg",
    "Muskmelon": "muskmelon.jpg",
    "Orange": "orange.jpg",
    "Sweet lime": "sweet_lime.jpg",
    "Beans": "beans.jpg",
    "Ridge gourd": "ridge_gourd.jpg",
    "Tapioca": "tapioca.jpg",
    "Yam": "yam.jpg",
    "Mutton": "mutton.jpg",
    "Egg yolk": "egg_yolk.jpeg",
    "Sausage": "sausage.jpg",
    "Organ meat": "organ_meat.jpg",
    "Dosa": "dosa.jpg",
    "Pasta": "pasta.jpg",
    "White Bread": "white_bread.jpg",
    "Noodles": "noodles.jpg",
    "Oats": "oats.jpg",
    "Ragi": "ragi.jpg",
    "Chips": "chips.jpg",
    "Water": "water.jpg",
    "Lemon juice": "lemon_juice.jpg",
    "Soft drinks": "soft_drinks.jpg",
}

IMAGE_DIR = "static/images"
CSV_FILE = "data/food_dataset.csv"

print("Validating and updating food images...\n")
print(f"Checking for images in: {IMAGE_DIR}\n")

# Check which images exist
existing_images = {}
if os.path.exists(IMAGE_DIR):
    files = os.listdir(IMAGE_DIR)
    existing_images = {f.lower() for f in files}
    print(f"Found {len(existing_images)} image files in directory\n")
else:
    print(f"ERROR: {IMAGE_DIR} directory does not exist!\n")
    exit(1)

# Read CSV and update with local paths
print("Processing CSV file...\n")
updated_count = 0
missing_count = 0

with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for row in rows:
    food_name = row['food_name']
    if food_name in FOOD_TO_IMAGE:
        image_filename = FOOD_TO_IMAGE[food_name]

        # Check if image exists
        if image_filename.lower() in existing_images:
            local_url = f"/static/images/{image_filename}"
            row['image_url'] = local_url
            updated_count += 1
            print(f"[OK] {food_name:20} -> {image_filename}")
        else:
            missing_count += 1
            print(f"[MISSING] {food_name:20} -> {image_filename} (NOT FOUND)")

# Write back to CSV
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n[SUCCESS] CSV updated:")
print(f"  - Updated: {updated_count} foods")
print(f"  - Missing: {missing_count} images")
print(f"  - Total processed: {updated_count + missing_count}")
print(f"\nFile: {CSV_FILE}")
print("Done!")
