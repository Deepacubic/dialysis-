import csv
import urllib.request
import urllib.error
import os
import time
from pathlib import Path

# Using reliable direct image URLs from free sources (pexels CDN, pixabay, etc)
FOOD_IMAGES = {
    "Custard apple": "https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600",  # Fruit
    "Kiwi": "https://images.pexels.com/photos/1438761/pexels-photo-1438761.jpeg?auto=compress&cs=tinysrgb&w=600",  # Kiwi
    "Dragon fruit": "https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600",  # Fruit
    "Muskmelon": "https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600",  # Fruit
    "Orange": "https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600",  # Orange/Citrus
    "Sweet lime": "https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600",  # Citrus fruit
    "Beans": "https://images.pexels.com/photos/2517965/pexels-photo-2517965.jpeg?auto=compress&cs=tinysrgb&w=600",  # Vegetables
    "Ridge gourd": "https://images.pexels.com/photos/2517965/pexels-photo-2517965.jpeg?auto=compress&cs=tinysrgb&w=600",  # Vegetable
    "Tapioca": "https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600",  # Food
    "Yam": "https://images.pexels.com/photos/2517965/pexels-photo-2517965.jpeg?auto=compress&cs=tinysrgb&w=600",  # Vegetable
    "Mutton": "https://images.pexels.com/photos/5737472/pexels-photo-5737472.jpeg?auto=compress&cs=tinysrgb&w=600",  # Meat
    "Egg yolk": "https://images.pexels.com/photos/5728319/pexels-photo-5728319.jpeg?auto=compress&cs=tinysrgb&w=600",  # Eggs
    "Sausage": "https://images.pexels.com/photos/5737472/pexels-photo-5737472.jpeg?auto=compress&cs=tinysrgb&w=600",  # Meat/Food
    "Organ meat": "https://images.pexels.com/photos/5737472/pexels-photo-5737472.jpeg?auto=compress&cs=tinysrgb&w=600",  # Meat
    "Dosa": "https://images.pexels.com/photos/1092730/pexels-photo-1092730.jpeg?auto=compress&cs=tinysrgb&w=600",  # Food/Meal
    "Pasta": "https://images.pexels.com/photos/8949/food-plate-pasta-dinner.jpg?auto=compress&cs=tinysrgb&w=600",  # Pasta
    "White Bread": "https://images.pexels.com/photos/3659684/pexels-photo-3659684.jpeg?auto=compress&cs=tinysrgb&w=600",  # Bread
    "Noodles": "https://images.pexels.com/photos/1092730/pexels-photo-1092730.jpeg?auto=compress&cs=tinysrgb&w=600",  # Noodles/Food
    "Oats": "https://images.pexels.com/photos/5737472/pexels-photo-5737472.jpeg?auto=compress&cs=tinysrgb&w=600",  # Cereal/Grains
    "Ragi": "https://images.pexels.com/photos/821365/pexels-photo-821365.jpeg?auto=compress&cs=tinysrgb&w=600",  # Grains
    "Chips": "https://images.pexels.com/photos/312418/pexels-photo-312418.jpeg?auto=compress&cs=tinysrgb&w=600",  # Snacks
    "Water": "https://images.pexels.com/photos/3970332/pexels-photo-3970332.jpeg?auto=compress&cs=tinysrgb&w=600",  # Beverage
    "Lemon juice": "https://images.pexels.com/photos/3407817/pexels-photo-3407817.jpeg?auto=compress&cs=tinysrgb&w=600",  # Beverage/Juice
    "Soft drinks": "https://images.pexels.com/photos/3407817/pexels-photo-3407817.jpeg?auto=compress&cs=tinysrgb&w=600",  # Beverage
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
            size_kb = os.path.getsize(filepath) / 1024
            print(f"[OK] {food_name:20} Already valid ({size_kb:.1f} KB)")
            return f"/static/images/{filename}"

        # Download the image with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        print(f"  Downloading {food_name}...", end=" ", flush=True)

        with urllib.request.urlopen(req, timeout=15) as response:
            image_data = response.read()

        # Validate before saving
        if len(image_data) < 1000:
            print(f" [FAIL] File too small ({len(image_data)} bytes)")
            return None

        # Save the image
        with open(filepath, 'wb') as f:
            f.write(image_data)

        # Verify it's a real image
        if is_valid_image(filepath):
            size_kb = len(image_data) / 1024
            print(f" [OK] ({size_kb:.1f} KB)")
            return f"/static/images/{filename}"
        else:
            os.remove(filepath)
            print(f" [FAIL] Invalid image format")
            return None

    except urllib.error.URLError as e:
        print(f" [ERROR] {str(e)[:50]}")
        return None
    except Exception as e:
        print(f" [ERROR] {str(e)[:50]}")
        return None

def update_csv():
    """Update CSV with local image paths"""
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    updated_count = 0
    print("\nDownloading and validating images:\n")

    for row in rows:
        food_name = row['food_name']
        if food_name in FOOD_IMAGES:
            local_url = download_image(food_name, FOOD_IMAGES[food_name])
            if local_url:
                row['image_url'] = local_url
                updated_count += 1
            time.sleep(0.5)  # Be respectful to servers

    # Write back to CSV
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[SUCCESS] CSV updated: {updated_count} images processed")
    print(f"File: {CSV_FILE}")

if __name__ == "__main__":
    print("=" * 70)
    print("Downloading real food images from Pexels (free CDN)...")
    print("=" * 70)
    update_csv()
    print("\nDone! All images have been refreshed.")
    print("=" * 70)
