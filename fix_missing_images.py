import csv
import shutil

input_file = "d:/project dialysis/data/food_dataset.csv"
temp_file = "d:/project dialysis/data/food_dataset_temp.csv"

fixes = {
    "Chicken (boiled)": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=500&q=80",
    "Fish (grilled)": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500&q=80",
    "Tuna fish": "https://images.unsplash.com/photo-1574484284002-952d92456975?w=500&q=80",
    "Mutton": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?w=500&q=80",
    "Egg yolk": "https://images.unsplash.com/photo-1582722872445-44ad5c78a9dd?w=500&q=80",
    "Dosa": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&q=80",
    "Ragi": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/FingerMillet_%28Eleusine_coracana%29.JPG/500px-FingerMillet_%28Eleusine_coracana%29.JPG",
    "Chips": "https://images.unsplash.com/photo-1566478431375-7033fff8799c?w=500&q=80",
    "Lemon juice": "https://images.unsplash.com/photo-1513361529188-7e10850c99f9?w=500&q=80",
    "Soft drinks": "https://images.unsplash.com/photo-1622483767028-3f66f3445078?w=500&q=80",
    "Alcohol": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=500&q=80",
    "Organ meat": "https://images.unsplash.com/photo-1634676527559-001d2932eaf7?w=500&q=80",
    "Yam": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Yam_tubers.jpg/500px-Yam_tubers.jpg",
    "Brown rice": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?w=500&q=80"
}

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for row in rows:
    name = row['food_name']
    if name in fixes:
        row['image_url'] = fixes[name]
        print(f"Fixed image for {name}")

with open(temp_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)

shutil.move(temp_file, input_file)
print("Finished fixing missing.")
