#!/usr/bin/env python3
import csv
import os

# Mapping of food names to local image filenames
FOOD_TO_IMAGE = {
    'Custard apple': '/static/images/custard_apple.jpg',
    'Kiwi': '/static/images/kiwi.jpg',
    'Dragon fruit': '/static/images/dragon_fruit.jpg',
    'Muskmelon': '/static/images/muskmelon.jpg',
    'Orange': '/static/images/orange.jpg',
    'Sweet lime': '/static/images/sweet_lime.jpg',
    'Beans': '/static/images/beans.jpg',
    'Ridge gourd': '/static/images/ridge_gourd.jpg',
    'Tapioca': '/static/images/tapioca.jpg',
    'Yam': '/static/images/yam.jpg',
    'Mutton': '/static/images/mutton.jpg',
    'Egg yolk': '/static/images/egg_yolk.jpeg',
    'Sausage': '/static/images/sausage.jpg',
    'Organ meat': '/static/images/organ_meat.jpg',
    'Dosa': '/static/images/dosa.jpg',
    'Pasta': '/static/images/pasta.jpg',
    'White Bread': '/static/images/white_bread.jpg',
    'Noodles': '/static/images/noodles.jpg',
    'Oats': '/static/images/oats.jpg',
    'Ragi': '/static/images/ragi.jpg',
    'Chips': '/static/images/chips.jpg',
    'Water': '/static/images/water.jpg',
    'Lemon juice': '/static/images/lemon_juice.jpg',
    'Soft drinks': '/static/images/soft_drinks.jpg',
}

csv_file = r'd:\project dialysis\data\food_dataset.csv'

print("=" * 60)
print("Updating food_dataset.csv with local image paths")
print("=" * 60)

# Read the CSV file
rows = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Update rows with local image paths
updated_count = 0
for row in rows:
    food_name = row['food_name']
    if food_name in FOOD_TO_IMAGE:
        old_url = row['image_url']
        new_url = FOOD_TO_IMAGE[food_name]
        row['image_url'] = new_url
        print(f"Updated: {food_name}")
        print(f"  Old: {old_url[:60]}...")
        print(f"  New: {new_url}")
        updated_count += 1

# Write the updated CSV file
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['food_name', 'category', 'recommendation', 'image_url']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("\n" + "=" * 60)
print(f"SUMMARY")
print("=" * 60)
print(f"Total records updated: {updated_count}")
print(f"CSV file: {csv_file}")
print("=" * 60)
