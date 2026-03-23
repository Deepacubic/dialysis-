import csv
import urllib.request
import json
import urllib.parse
import time
import shutil

input_file = "d:/project dialysis/data/food_dataset.csv"
temp_file = "d:/project dialysis/data/food_dataset_temp.csv"

def get_wikimedia_image(title):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&titles={urllib.parse.quote(title)}&pithumbsize=500&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'DialysisApp/1.0 (test@example.com)'})
        res = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(res)
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "thumbnail" in page_data:
                return page_data["thumbnail"]["source"]
    except Exception as e:
        pass
    return None

def fallback_fallback_unsplash(title):
    # known good direct urls from fallback for basic items
    known = {
        "Pineapple": "https://images.unsplash.com/photo-1550259114-ad7188f0a96ea?w=500&q=80",
        "Watermelon": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=500&q=80",
        "Apple": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?w=500&q=80",
        "Papaya": "https://images.unsplash.com/photo-1517282009859-f000ec3b26fe?w=500&q=80",
        "Pear": "https://images.unsplash.com/photo-1615486171448-4cbab5ea71bd?w=500&q=80",
        "Strawberry": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=500&q=80",
        "Peach": "https://images.unsplash.com/photo-1522204523234-8229ec61d904?w=500&q=80",
        "Plum": "https://images.unsplash.com/photo-1599819162354-99882ee0a716?w=500&q=80",
        "Cherry": "https://images.unsplash.com/photo-1528821128474-27f9e7765859?w=500&q=80",
        "Grapes": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Table_grapes_on_white.jpg/500px-Table_grapes_on_white.jpg",
    }
    return known.get(title)

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for row in rows:
    name = row['food_name']
    
    # Let's search Wikipedia first
    img_url = get_wikimedia_image(name)
    
    # If not found or if it's grapes (which doesn't work perfectly on Wikipedia without specific title), try a fallback
    if not img_url:
        if name == "Grapes":
            img_url = get_wikimedia_image("Grape")
        elif name == "Prawns":
             img_url = get_wikimedia_image("Prawn")
        elif name == "Capsicum":
             img_url = get_wikimedia_image("Bell pepper")
        elif name == "Brinjal":
             img_url = get_wikimedia_image("Eggplant")
        elif name == "Bottle gourd":
             img_url = get_wikimedia_image("Calabash")
        elif name == "Snake gourd":
             img_url = get_wikimedia_image("Trichosanthes cucumerina")
        elif name == "Millet":
             img_url = get_wikimedia_image("Millet")
        elif name == "Ragi":
             img_url = get_wikimedia_image("Eleusine coracana")
        elif name == "Green peas":
             img_url = get_wikimedia_image("Pea")
        elif name == "Drumstick leaves":
             img_url = get_wikimedia_image("Moringa oleifera")
        elif name == "Sweet lime":
             img_url = get_wikimedia_image("Citrus limetta")
        elif name == "Custard apple":
             img_url = get_wikimedia_image("Sugar apple")
        elif name == "Jackfruit":
              img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Jackfruit_in_cut_display.jpg/500px-Jackfruit_in_cut_display.jpg"
              
    if not img_url:
         # Try fallback
         img_url = fallback_fallback_unsplash(name)
         
    if img_url:
        row['image_url'] = img_url
        print(f"Set image for {name}: {img_url}")
    else:
        # Generate a beautiful gradient placeholder via placehold.co instead of loremflickr
        row['image_url'] = f"https://placehold.co/500x500/f0fdf4/16a34a?text={urllib.parse.quote(name)}"
        print(f"Fallback placeholder for {name}")

    time.sleep(0.3)

with open(temp_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)

shutil.move(temp_file, input_file)
print("Updated all image URLs successfully.")
