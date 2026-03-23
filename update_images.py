import csv
import urllib.parse
import os
import shutil

input_file = "d:/project dialysis/data/food_dataset.csv"
temp_file = "d:/project dialysis/data/food_dataset_temp.csv"

# High-quality direct Unsplash image links for specific foods to create a beautiful UI
food_images = {
    "Pear": "https://images.unsplash.com/photo-1615486171448-4cbab5ea71bd?w=500&q=80",
    "Grapes": "https://images.unsplash.com/photo-1596364721221-306ba2b0284b?w=500&q=80",
    "Guava": "https://images.unsplash.com/photo-1536553255140-5fb3426e95b0?w=500&q=80",
    "Strawberry": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=500&q=80",
    "Peach": "https://images.unsplash.com/photo-1522204523234-8229ec61d904?w=500&q=80",
    "Plum": "https://images.unsplash.com/photo-1599819162354-99882ee0a716?w=500&q=80",
    "Cherry": "https://images.unsplash.com/photo-1528821128474-27f9e7765859?w=500&q=80",
    "Pomegranate": "https://images.unsplash.com/photo-1615484477778-ca3b77942253?w=500&q=80",
    "Kiwi": "https://images.unsplash.com/photo-1585059895316-2495b46e3845?w=500&q=80",
    "Dragon fruit": "https://images.unsplash.com/photo-1596701062351-8c0c1459c594?w=500&q=80",
    "Muskmelon": "https://images.unsplash.com/photo-1571575173700-afb9492e6a50?w=500&q=80",
    "Fig": "https://images.unsplash.com/photo-1583063548981-d19124be3af6?w=500&q=80",
    "Banana": "https://images.unsplash.com/photo-1571771894821-ad99024177c6?w=500&q=80",
    "Orange": "https://images.unsplash.com/photo-1582284540020-8acaf01f344a?w=500&q=80",
    "Jackfruit": "https://loremflickr.com/500/500/jackfruit,food",
    "Custard apple": "https://loremflickr.com/500/500/custardapple,fruit",
    "Capsicum": "https://images.unsplash.com/photo-1563599175592-c58dc214deff?w=500&q=80",
    "Brinjal": "https://images.unsplash.com/photo-1528143431327-1f200ca25895?w=500&q=80",
    "Bottle gourd": "https://loremflickr.com/500/500/bottlegourd,vegetable",
    "Snake gourd": "https://loremflickr.com/500/500/snakegourd,vegetable",
    "Pumpkin": "https://images.unsplash.com/photo-1506543730435-e2c1d4553a84?w=500&q=80",
    "Radish": "https://images.unsplash.com/photo-1582515073490-39981397c445?w=500&q=80",
    "Beetroot": "https://images.unsplash.com/photo-1585559604169-236f01da0e69?w=500&q=80",
    "Green peas": "https://images.unsplash.com/photo-1592394933696-1200ae3ec6a7?w=500&q=80",
    "Mushroom": "https://images.unsplash.com/photo-1504675099198-7023dd85f5a3?w=500&q=80",
    "Tomato": "https://images.unsplash.com/photo-1518977822534-7049a6feec68?w=500&q=80",
    "Drumstick leaves": "https://loremflickr.com/500/500/moringa,leaves",
    "Chapati": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&q=80",
    "Dosa": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&q=80",
    "White Bread": "https://images.unsplash.com/photo-1598373182133-52452f7691ef?w=500&q=80",
    "Brown rice": "https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?w=500&q=80",
    "Oats": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=500&q=80",
    "Millet": "https://loremflickr.com/500/500/millet,grain",
    "Ragi": "https://loremflickr.com/500/500/ragi,grain",
    "Water": "https://images.unsplash.com/photo-1548919973-5dea58b88ad6?w=500&q=80",
    "Apple juice": "https://images.unsplash.com/photo-1568909344668-6f14a019c697?w=500&q=80",
    "Cranberry juice": "https://images.unsplash.com/photo-1584347585093-61fcfaec4eb6?w=500&q=80",
    "Lemon juice": "https://images.unsplash.com/photo-1513361529188-7e10850c99f9?w=500&q=80",
    "Milk": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&q=80",
    "Coffee": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=500&q=80",
    "Tea": "https://images.unsplash.com/photo-1544787210-2213d8439ac2?w=500&q=80",
    "Coconut water": "https://images.unsplash.com/photo-1522856402283-4a001a1db158?w=500&q=80",
    "Orange juice": "https://images.unsplash.com/photo-1600271886399-ca8474d2b27a?w=500&q=80",
    "Paneer": "https://images.unsplash.com/photo-1588166524941-3bf61a0b5f63?w=500&q=80",
    "Tofu": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&q=80",
    "Processed cheese": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=500&q=80",
    "Egg white": "https://images.unsplash.com/photo-1582722872445-44ad5c78a9dd?w=500&q=80",
    "Egg yolk": "https://images.unsplash.com/photo-1582722872445-44ad5c78a9dd?w=500&q=80",
    "Mutton": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?w=500&q=80",
    "Organ meat": "https://images.unsplash.com/photo-1634676527559-001d2932eaf7?w=500&q=80",
    "Pineapple": "https://images.unsplash.com/photo-1550259114-ad7188f0a96ea?w=500&q=80",
    "Watermelon": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=500&q=80",
    "Apple": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?w=500&q=80",
    "Papaya": "https://images.unsplash.com/photo-1517282009859-f000ec3b26fe?w=500&q=80"
}

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for row in rows:
    name = row['food_name']
    if name in food_images:
        row['image_url'] = food_images[name]
    elif row['image_url'].startswith('/static/images/'):
        safe_name = urllib.parse.quote(name.lower().replace(" ", ""))
        row['image_url'] = f"https://loremflickr.com/500/500/{safe_name},food/all"

with open(temp_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)

shutil.move(temp_file, input_file)
print("Updated all image URLs successfully.")
