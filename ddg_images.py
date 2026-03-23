import csv
import shutil
import time
from duckduckgo_search import DDGS

input_file = "d:/project dialysis/data/food_dataset.csv"
temp_file = "d:/project dialysis/data/food_dataset_temp.csv"

def search_image(query):
    try:
        results = DDGS().images(
            keywords=query,
            region="wt-wt",
            safesearch="on",
            size="Medium",
            color="All",
            type_image="photo",
            layout="Square",
            license_image="any",
            max_results=1,
        )
        if results:
            return results[0]['image']
    except Exception as e:
        print(f"Error fetching {query}: {e}")
    return None

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for row in rows:
    name = row['food_name']
    
    # We want to replace anything that has loremflickr or repeating chicken images
    is_loremflickr = 'loremflickr' in row['image_url']
    # Many of my previous hardcoded unsplash links might be the same fallback if they were 404
    # Wait, my previous unsplash links were good, except some that were not actually valid and I may have missed it.
    # Actually, the user says "the fruits are ai images get real images frrom web get the crct image and add"
    # Which means we should fetch everything fresh from duckduckgo to be sure!
    
    query = f"{name} fruit fresh" if row['category'] == 'Fruits' else \
            f"{name} vegetable fresh" if row['category'] == 'Vegetables' else \
            f"{name} food fresh"
    
    if name == 'Water':
        query = "glass of plain water"
    elif name == 'Milk':
        query = "glass of milk"
    
    print(f"Searching image for: {name} (Query: {query})")
    img_url = search_image(query)
    
    if img_url:
        row['image_url'] = img_url
        print(f" -> Found: {img_url}")
    else:
        print(f" -> Failed to find image for {name}")

    time.sleep(1) # Be nice to the API

with open(temp_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)

shutil.move(temp_file, input_file)
print("Updated all image URLs successfully.")
