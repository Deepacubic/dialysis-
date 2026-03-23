#!/bin/bash

CSV_FILE="d:/project dialysis/data/food_dataset.csv"
TEMP_FILE="d:/project dialysis/data/food_dataset_temp.csv"

echo "=================================================="
echo "Updating food_dataset.csv with local image paths"
echo "=================================================="

# Create a temporary file with updated paths
cat "$CSV_FILE" | sed \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Custard_Apple.jpg/500px-Custard_Apple.jpg|/static/images/custard_apple.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Kiwi_aka.jpg/500px-Kiwi_aka.jpg|/static/images/kiwi.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Kiwi_Fruit.jpg/640px-Kiwi_Fruit.jpg|/static/images/kiwi.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Pitaya_cross_section_ed2.jpg/500px-Pitaya_cross_section_ed2.jpg|/static/images/dragon_fruit.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Musk_melon_-_Cucumis_melo.jpg/500px-Musk_melon_-_Cucumis_melo.jpg|/static/images/muskmelon.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Oranges_and_orange_juice.jpg/500px-Oranges_and_orange_juice.jpg|/static/images/orange.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Citrus_x_limetta.jpg/500px-Citrus_x_limetta.jpg|/static/images/sweet_lime.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/GreenBeans.jpg/500px-GreenBeans.jpg|/static/images/beans.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Ridge_gourd_%28Luffa_acutangula%29.jpg/500px-Ridge_gourd_%28Luffa_acutangula%29.jpg|/static/images/ridge_gourd.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Manihot_esculenta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-090.jpg/500px-Manihot_esculenta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-090.jpg|/static/images/tapioca.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Dioscorea_alata_-_Manila.jpg/500px-Dioscorea_alata_-_Manila.jpg|/static/images/yam.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Flickr_-_cyclonebill_-_Lammekrone.jpg/500px-Flickr_-_cyclonebill_-_Lammekrone.jpg|/static/images/mutton.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Egg_yolk_in_a_small_white_bowl.jpeg/500px-Egg_yolk_in_a_small_white_bowl.jpeg|/static/images/egg_yolk.jpeg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_Sausage_%28Weisswurst%29.jpg/500px-White_Sausage_%28Weisswurst%29.jpg|/static/images/sausage.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Chicken_giblets.jpg/500px-Chicken_giblets.jpg|/static/images/organ_meat.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Plain_dosa_from_Sri_Krishna_Cafe.jpg/500px-Plain_dosa_from_Sri_Krishna_Cafe.jpg|/static/images/dosa.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Orecchiette_con_cime_di_rapa.jpg/500px-Orecchiette_con_cime_di_rapa.jpg|/static/images/pasta.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Fresh_made_bread_05.jpg/500px-Fresh_made_bread_05.jpg|/static/images/white_bread.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Chinesische_Nudeln.jpg/500px-Chinesische_Nudeln.jpg|/static/images/noodles.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Avena_sativa_-_Hafer_-_oat_-_Flughafer_1.jpg/500px-Avena_sativa_-_Hafer_-_oat_-_Flughafer_1.jpg|/static/images/oats.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/FingerMillet.jpg/500px-FingerMillet.jpg|/static/images/ragi.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Potato-Chips.jpg/500px-Potato-Chips.jpg|/static/images/chips.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Water_drop_impact_on_a_water-surface_-_%281%29.jpg/500px-Water_drop_impact_on_a_water-surface_-_%281%29.jpg|/static/images/water.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Lemon_juice_glasses.jpg/500px-Lemon_juice_glasses.jpg|/static/images/lemon_juice.jpg|g' \
  -e 's|https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Soft_drink_servings.jpg/500px-Soft_drink_servings.jpg|/static/images/soft_drinks.jpg|g' \
  > "$TEMP_FILE"

# Replace original with updated file
mv "$TEMP_FILE" "$CSV_FILE"

echo ""
echo "CSV file updated successfully!"
echo "Location: $CSV_FILE"
echo "=================================================="
