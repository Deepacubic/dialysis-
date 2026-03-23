import csv
import urllib.request
import urllib.error
import os
import time
from pathlib import Path

# Use Pexels CDN URLs which don't have rate limiting
FAILOVER_IMAGES = {
    "Mutton": "https://images.pexels.com/photos/4551832/pexels-photo-4551832.jpeg?w=640&h=640&fit=crop",
    "Sausage": "https://images.pexels.com/photos/2544521/pexels-photo-2544521.jpeg?w=640&h=640&fit=crop",
    "Organ meat": "https://images.pexels.com/photos/6551196/pexels-photo-6551196.jpeg?w=640&h=640&fit=crop",
    "Pasta": "https://images.pexels.com/photos/1693619/pexels-photo-1693619.jpeg?w=640&h=640&fit=crop",
    "Oats": "https://images.pexels.com/photos/4551991/pexels-photo-4551991.jpeg?w=640&h=640&fit=crop",
}

IMAGE_DIR = "static/images"
CSV_FILE = "data/food_dataset.csv"

Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)

def is_valid_image(filepath):
    """Check if file is a valid image"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(10)
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
        safe_name = food_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        filename = f"{safe_name}.jpg"
        filepath = os.path.join(IMAGE_DIR, filename)

        if os.path.exists(filepath) and is_valid_image(filepath):
            size = os.path.getsize(filepath) / 1024
            print(f"[OK] {food_name}: Already exists ({size:.1f} KB)")
            return f"/static/images/{filename}"

        print(f"[DOWNLOADING] {food_name}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.pexels.com/',
        }
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=20) as response:
            image_data = response.read()

        if len(image_data) < 1000:
            print(f"[FAIL] {food_name}: File too small ({len(image_data)} bytes)")
            return None

        with open(filepath, 'wb') as f:
            f.write(image_data)

        if is_valid_image(filepath):
            size = len(image_data) / 1024
            print(f"[SUCCESS] {food_name}: Downloaded ({size:.1f} KB)")
            return f"/static/images/{filename}"
        else:
            os.remove(filepath)
            print(f"[FAIL] {food_name}: Invalid image format")
            return None

    except urllib.error.URLError as e:
        print(f"[ERROR] {food_name}: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] {food_name}: {type(e).__name__}: {e}")
        return None

def update_csv():
    """Update CSV with failover image paths"""
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    updated_count = 0
    for food_name, url in FAILOVER_IMAGES.items():
        print(f"\nProcessing: {food_name}")
        local_url = download_image(food_name, url)
        if local_url:
            for row in rows:
                if row['food_name'] == food_name:
                    row['image_url'] = local_url
                    updated_count += 1
                    break
        time.sleep(2)  # 2 second delay between requests

    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[SUCCESS] Updated {updated_count} failover images in CSV")

if __name__ == "__main__":
    print("Downloading failover images from Pexels...\n")
    update_csv()
    print("\nDone!")
