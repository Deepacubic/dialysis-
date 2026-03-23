import csv
import urllib.request
import urllib.error
import os
import time
from pathlib import Path

# Wikimedia Commons real image URLs (verified real photographs, not AI)
FOOD_IMAGES = {
    "Custard apple": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Custard_Apple.jpg/640px-Custard_Apple.jpg",
    "Kiwi": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Kiwi_Fruit.jpg/640px-Kiwi_Fruit.jpg",
    "Dragon fruit": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Pitaya_cross_section_ed2.jpg/640px-Pitaya_cross_section_ed2.jpg",
    "Muskmelon": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Musk_melon_-_Cucumis_melo.jpg/640px-Musk_melon_-_Cucumis_melo.jpg",
    "Orange": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Oranges_and_orange_juice.jpg/640px-Oranges_and_orange_juice.jpg",
    "Sweet lime": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Citrus_x_limetta.jpg/640px-Citrus_x_limetta.jpg",
    "Beans": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/GreenBeans.jpg/640px-GreenBeans.jpg",
    "Ridge gourd": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Ridge_gourd_%28Luffa_acutangula%29.jpg/640px-Ridge_gourd_%28Luffa_acutangula%29.jpg",
    "Tapioca": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Manihot_esculenta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-090.jpg/640px-Manihot_esculenta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-090.jpg",
    "Yam": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Dioscorea_alata_-_Manila.jpg/640px-Dioscorea_alata_-_Manila.jpg",
    "Mutton": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Flickr_-_cyclonebill_-_Lammekrone.jpg/640px-Flickr_-_cyclonebill_-_Lammekrone.jpg",
    "Egg yolk": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Egg_yolk_in_a_small_white_bowl.jpeg/640px-Egg_yolk_in_a_small_white_bowl.jpeg",
    "Sausage": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_Sausage_%28Weisswurst%29.jpg/640px-White_Sausage_%28Weisswurst%29.jpg",
    "Organ meat": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Chicken_giblets.jpg/640px-Chicken_giblets.jpg",
    "Dosa": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Plain_dosa_from_Sri_Krishna_Cafe.jpg/640px-Plain_dosa_from_Sri_Krishna_Cafe.jpg",
    "Pasta": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Orecchiette_con_cime_di_rapa.jpg/640px-Orecchiette_con_cime_di_rapa.jpg",
    "White Bread": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Fresh_made_bread_05.jpg/640px-Fresh_made_bread_05.jpg",
    "Noodles": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Chinesische_Nudeln.jpg/640px-Chinesische_Nudeln.jpg",
    "Oats": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Avena_sativa_-_Hafer_-_oat_-_Flughafer_1.jpg/640px-Avena_sativa_-_Hafer_-_oat_-_Flughafer_1.jpg",
    "Ragi": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/FingerMillet.jpg/640px-FingerMillet.jpg",
    "Chips": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Potato-Chips.jpg/640px-Potato-Chips.jpg",
    "Water": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Water_drop_impact_on_a_water-surface_-_%281%29.jpg/640px-Water_drop_impact_on_a_water-surface_-_%281%29.jpg",
    "Lemon juice": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Lemon_juice_glasses.jpg/640px-Lemon_juice_glasses.jpg",
    "Soft drinks": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Soft_drink_servings.jpg/640px-Soft_drink_servings.jpg",
}

IMAGE_DIR = "static/images"
CSV_FILE = "data/food_dataset.csv"

# Create images directory if it doesn't exist
Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)

def download_image(food_name, url):
    """Download image and save locally"""
    try:
        # Create safe filename
        safe_name = food_name.lower().replace(" ", "_").replace("(", "").replace(")", "")

        # Determine file extension
        if url.endswith('.png'):
            filename = f"{safe_name}.png"
        elif url.endswith('.jpeg') or url.endswith('.jpg'):
            filename = f"{safe_name}.jpg"
        else:
            filename = f"{safe_name}.jpg"

        filepath = os.path.join(IMAGE_DIR, filename)

        # Don't re-download if already exists
        if os.path.exists(filepath):
            print(f"✓ {food_name}: Already exists")
            return f"/static/images/{filename}"

        # Download the image
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            image_data = response.read()

        # Save the image
        with open(filepath, 'wb') as f:
            f.write(image_data)

        print(f"✓ {food_name}: Downloaded ({len(image_data) / 1024:.1f} KB)")
        return f"/static/images/{filename}"

    except urllib.error.URLError as e:
        print(f"✗ {food_name}: Download failed - {e}")
        return None
    except Exception as e:
        print(f"✗ {food_name}: Error - {e}")
        return None

def update_csv():
    """Update CSV with local image paths"""

    # Read CSV
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Update image URLs for specified foods
    for row in rows:
        food_name = row['food_name']
        if food_name in FOOD_IMAGES:
            local_url = download_image(food_name, FOOD_IMAGES[food_name])
            if local_url:
                row['image_url'] = local_url
            time.sleep(0.5)  # Be respectful to servers

    # Write back to CSV
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n✓ CSV updated successfully")

if __name__ == "__main__":
    print("Downloading food images...\n")
    update_csv()
    print("\nDone! All images have been processed.")
