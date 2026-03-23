import requests
import os
import csv
from pathlib import Path
import sys

# Mapping of food names to Wikimedia Commons URLs
FOOD_IMAGES = {
    'Custard apple': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Custard_Apple.jpg/640px-Custard_Apple.jpg',
    'Kiwi': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Kiwi_Fruit.jpg/640px-Kiwi_Fruit.jpg',
    'Dragon fruit': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Pitaya_cross_section_ed2.jpg/640px-Pitaya_cross_section_ed2.jpg',
    'Muskmelon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Musk_melon_-_Cucumis_melo.jpg/640px-Musk_melon_-_Cucumis_melo.jpg',
    'Orange': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Oranges_and_orange_juice.jpg/640px-Oranges_and_orange_juice.jpg',
    'Sweet lime': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Citrus_x_limetta.jpg/640px-Citrus_x_limetta.jpg',
    'Beans': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/GreenBeans.jpg/640px-GreenBeans.jpg',
    'Ridge gourd': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Ridge_gourd_%28Luffa_acutangula%29.jpg/640px-Ridge_gourd_%28Luffa_acutangula%29.jpg',
    'Tapioca': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Manihot_esculenta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-090.jpg/640px-Manihot_esculenta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-090.jpg',
    'Yam': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Dioscorea_alata_-_Manila.jpg/640px-Dioscorea_alata_-_Manila.jpg',
    'Mutton': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Flickr_-_cyclonebill_-_Lammekrone.jpg/640px-Flickr_-_cyclonebill_-_Lammekrone.jpg',
    'Egg yolk': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Egg_yolk_in_a_small_white_bowl.jpeg/640px-Egg_yolk_in_a_small_white_bowl.jpeg',
    'Sausage': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_Sausage_%28Weisswurst%29.jpg/640px-White_Sausage_%28Weisswurst%29.jpg',
    'Organ meat': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Chicken_giblets.jpg/640px-Chicken_giblets.jpg',
    'Dosa': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Plain_dosa_from_Sri_Krishna_Cafe.jpg/640px-Plain_dosa_from_Sri_Krishna_Cafe.jpg',
    'Pasta': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Orecchiette_con_cime_di_rapa.jpg/640px-Orecchiette_con_cime_di_rapa.jpg',
    'White Bread': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Fresh_made_bread_05.jpg/640px-Fresh_made_bread_05.jpg',
    'Noodles': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Chinesische_Nudeln.jpg/640px-Chinesische_Nudeln.jpg',
    'Oats': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Avena_sativa_-_Hafer_-_oat_-_Flughafer_1.jpg/640px-Avena_sativa_-_Hafer_-_oat_-_Flughafer_1.jpg',
    'Ragi': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/FingerMillet.jpg/640px-FingerMillet.jpg',
    'Chips': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Potato-Chips.jpg/640px-Potato-Chips.jpg',
    'Water': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Water_drop_impact_on_a_water-surface_-_%281%29.jpg/640px-Water_drop_impact_on_a_water-surface_-_%281%29.jpg',
    'Lemon juice': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Lemon_juice_glasses.jpg/640px-Lemon_juice_glasses.jpg',
    'Soft drinks': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Soft_drink_servings.jpg/640px-Soft_drink_servings.jpg',
}

def sanitize_filename(name):
    """Convert food name to safe filename"""
    return name.lower().replace(' ', '_').replace('(', '').replace(')', '')

def download_image(url, filename, output_dir):
    """Download image from URL and save to file"""
    try:
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()

        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def main():
    images_dir = r"d:\project dialysis\static\images"
    csv_file = r"d:\project dialysis\data\food_dataset.csv"

    # Ensure directory exists
    os.makedirs(images_dir, exist_ok=True)

    print("=" * 60)
    print("Downloading Wikimedia Commons Food Images")
    print("=" * 60)

    # Download images
    downloaded_files = {}
    for food_name, url in FOOD_IMAGES.items():
        filename = sanitize_filename(food_name)
        # Get file extension from URL
        ext = '.jpg' if 'jpg' in url.lower() else '.jpeg'
        filename = filename + ext

        print(f"\nDownloading {food_name}...", end=" ")

        if download_image(url, filename, images_dir):
            print("OK")
            downloaded_files[food_name] = filename
        else:
            print("FAILED")

    # Update CSV file
    print("\n" + "=" * 60)
    print("Updating food_dataset.csv")
    print("=" * 60)

    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Update rows with local image paths
    updated_count = 0
    for row in rows:
        food_name = row['food_name']
        if food_name in downloaded_files:
            filename = downloaded_files[food_name]
            local_path = f"/static/images/{filename}"
            row['image_url'] = local_path
            print(f"Updated: {food_name} -> {local_path}")
            updated_count += 1

    # Write updated CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['food_name', 'category', 'recommendation', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 60)
    print(f"SUMMARY")
    print("=" * 60)
    print(f"Images downloaded: {len(downloaded_files)}")
    print(f"CSV records updated: {updated_count}")
    print(f"Images saved to: {images_dir}")
    print(f"CSV updated: {csv_file}")
    print("=" * 60)

if __name__ == '__main__':
    main()
