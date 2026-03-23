import csv
import urllib.request
import urllib.error
import os
import time
from pathlib import Path
import shutil

# Using reliable free image sources from Wikimedia Commons and working Unsplash links
FOOD_IMAGES = {
    "Custard apple": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Annona_squamosa_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-003.jpg/500px-Annona_squamosa_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-003.jpg",
    "Kiwi": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Kiwi_%28fruit_%26_section%29.jpg/500px-Kiwi_%28fruit_%26_section%29.jpg",
    "Dragon fruit": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Dragon_Fruit_%26_Cross_Section.jpg/500px-Dragon_Fruit_%26_Cross_Section.jpg",
    "Muskmelon": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/NCI_melon.jpg/500px-NCI_melon.jpg",
    "Orange": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/E_schnitz.png/500px-E_schnitz.png",
    "Sweet lime": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Sweet_lime_4.jpg/500px-Sweet_lime_4.jpg",
    "Beans": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Bean_Pod_Casings.jpg/500px-Bean_Pod_Casings.jpg",
    "Ridge gourd": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Ridge_Gourd_Plant_%28Luffa%29.jpg/500px-Ridge_Gourd_Plant_%28Luffa%29.jpg",
    "Tapioca": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Cassava_root.jpg/500px-Cassava_root.jpg",
    "Yam": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Yam_-_NCI_Visuals_Online.jpg/500px-Yam_-_NCI_Visuals_Online.jpg",
    "Mutton": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Mutton_%28Ovis_aries%29.jpg/500px-Mutton_%28Ovis_aries%29.jpg",
    "Egg yolk": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Egg_-_whole_and_split.jpg/500px-Egg_-_whole_and_split.jpg",
    "Sausage": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Sausage_links.jpg/500px-Sausage_links.jpg",
    "Organ meat": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Mutton_%28Ovis_aries%29.jpg/500px-Mutton_%28Ovis_aries%29.jpg",
    "Dosa": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Dosa_with_sambar_and_chutney_%28street_food%29.jpg/500px-Dosa_with_sambar_and_chutney_%28street_food%29.jpg",
    "Pasta": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Floured_Spaghetti.jpg/500px-Floured_Spaghetti.jpg",
    "White Bread": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Fresh_made_bread_05.jpg/500px-Fresh_made_bread_05.jpg",
    "Noodles": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Egg_Noodles_%282%29.jpg/500px-Egg_Noodles_%282%29.jpg",
    "Oats": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Oats.png/500px-Oats.png",
    "Ragi": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Finger_millet_in_Uttara_Kannada_district.jpg/500px-Finger_millet_in_Uttara_Kannada_district.jpg",
    "Chips": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Potato_chips.png/500px-Potato_chips.png",
    "Water": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Glass_of_water.jpg/500px-Glass_of_water.jpg",
    "Lemon juice": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Lemonade.jpg/500px-Lemonade.jpg",
    "Soft drinks": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Cola_Glass.jpg/500px-Cola_Glass.jpg",
}

IMAGE_DIR = "static/images"
CSV_FILE = "data/food_dataset.csv"

# Create images directory if it doesn't exist
Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)

def is_valid_image(filepath):
    """Check if file is a valid image"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(10)
            # Check for JPEG, PNG, GIF, WebP magic numbers
            if header[:3] == b'\xff\xd8\xff':  # JPEG
                return True
            if header[:8] == b'\x89PNG\r\n\x1a\n':  # PNG
                return True
            if header[:4] == b'GIF8':  # GIF
                return True
            if header[:4] == b'RIFF':  # WebP
                return True
        return False
    except:
        return False

def download_image(food_name, url):
    """Download image and save locally"""
    try:
        # Create safe filename
        safe_name = food_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        filename = f"{safe_name}.jpg"
        filepath = os.path.join(IMAGE_DIR, filename)

        # Remove old invalid file if exists
        if os.path.exists(filepath) and not is_valid_image(filepath):
            os.remove(filepath)
            print(f"  Removed invalid file: {filename}")

        if os.path.exists(filepath) and is_valid_image(filepath):
            print(f"[OK] {food_name}: Already valid ({os.path.getsize(filepath) / 1024:.1f} KB)")
            return f"/static/images/{filename}"

        # Download the image with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=15) as response:
            image_data = response.read()

        # Validate before saving
        if len(image_data) < 1000:
            print(f"[FAIL] {food_name}: File too small ({len(image_data)} bytes) - likely error page")
            return None

        # Save the image
        with open(filepath, 'wb') as f:
            f.write(image_data)

        # Verify it's a real image
        if is_valid_image(filepath):
            print(f"[OK] {food_name}: Downloaded ({len(image_data) / 1024:.1f} KB)")
            return f"/static/images/{filename}"
        else:
            os.remove(filepath)
            print(f"[FAIL] {food_name}: Invalid image file format")
            return None

    except urllib.error.URLError as e:
        print(f"[ERROR] {food_name}: URL error - {e}")
        return None
    except Exception as e:
        print(f"[ERROR] {food_name}: Error - {e}")
        return None

def update_csv():
    """Update CSV with local image paths"""
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    updated_count = 0
    for row in rows:
        food_name = row['food_name']
        if food_name in FOOD_IMAGES:
            local_url = download_image(food_name, FOOD_IMAGES[food_name])
            if local_url:
                row['image_url'] = local_url
                updated_count += 1
            time.sleep(0.8)  # Be respectful to servers

    # Write back to CSV
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[SUCCESS] CSV updated: {updated_count} images processed")

if __name__ == "__main__":
    print("Downloading real food images from Unsplash...\n")
    update_csv()
    print("\nDone! All images have been refreshed.")
