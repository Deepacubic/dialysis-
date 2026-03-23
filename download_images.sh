#!/bin/bash

# Download Wikimedia Commons images
IMAGES_DIR="d:/project dialysis/static/images"

echo "=================================================="
echo "Downloading Wikimedia Commons Food Images"
echo "=================================================="
echo ""

# Create images directory
mkdir -p "$IMAGES_DIR"

# Download each image
echo "Downloading Custard apple..."
curl -s -o "$IMAGES_DIR/custard_apple.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Custard_Apple.jpg/640px-Custard_Apple.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Kiwi..."
curl -s -o "$IMAGES_DIR/kiwi.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Kiwi_Fruit.jpg/640px-Kiwi_Fruit.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Dragon fruit..."
curl -s -o "$IMAGES_DIR/dragon_fruit.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Pitaya_cross_section_ed2.jpg/640px-Pitaya_cross_section_ed2.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Muskmelon..."
curl -s -o "$IMAGES_DIR/muskmelon.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Musk_melon_-_Cucumis_melo.jpg/640px-Musk_melon_-_Cucumis_melo.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Orange..."
curl -s -o "$IMAGES_DIR/orange.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Oranges_and_orange_juice.jpg/640px-Oranges_and_orange_juice.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Sweet lime..."
curl -s -o "$IMAGES_DIR/sweet_lime.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Citrus_x_limetta.jpg/640px-Citrus_x_limetta.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Beans..."
curl -s -o "$IMAGES_DIR/beans.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/GreenBeans.jpg/640px-GreenBeans.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Ridge gourd..."
curl -s -o "$IMAGES_DIR/ridge_gourd.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Ridge_gourd_%28Luffa_acutangula%29.jpg/640px-Ridge_gourd_%28Luffa_acutangula%29.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Tapioca..."
curl -s -o "$IMAGES_DIR/tapioca.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Manihot_esculenta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-090.jpg/640px-Manihot_esculenta_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-090.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Yam..."
curl -s -o "$IMAGES_DIR/yam.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Dioscorea_alata_-_Manila.jpg/640px-Dioscorea_alata_-_Manila.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Mutton..."
curl -s -o "$IMAGES_DIR/mutton.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Flickr_-_cyclonebill_-_Lammekrone.jpg/640px-Flickr_-_cyclonebill_-_Lammekrone.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Egg yolk..."
curl -s -o "$IMAGES_DIR/egg_yolk.jpeg" "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Egg_yolk_in_a_small_white_bowl.jpeg/640px-Egg_yolk_in_a_small_white_bowl.jpeg" && echo "OK" || echo "FAILED"

echo "Downloading Sausage..."
curl -s -o "$IMAGES_DIR/sausage.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_Sausage_%28Weisswurst%29.jpg/640px-White_Sausage_%28Weisswurst%29.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Organ meat..."
curl -s -o "$IMAGES_DIR/organ_meat.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Chicken_giblets.jpg/640px-Chicken_giblets.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Dosa..."
curl -s -o "$IMAGES_DIR/dosa.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Plain_dosa_from_Sri_Krishna_Cafe.jpg/640px-Plain_dosa_from_Sri_Krishna_Cafe.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Pasta..."
curl -s -o "$IMAGES_DIR/pasta.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Orecchiette_con_cime_di_rapa.jpg/640px-Orecchiette_con_cime_di_rapa.jpg" && echo "OK" || echo "FAILED"

echo "Downloading White Bread..."
curl -s -o "$IMAGES_DIR/white_bread.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Fresh_made_bread_05.jpg/640px-Fresh_made_bread_05.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Noodles..."
curl -s -o "$IMAGES_DIR/noodles.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Chinesische_Nudeln.jpg/640px-Chinesische_Nudeln.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Oats..."
curl -s -o "$IMAGES_DIR/oats.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Avena_sativa_-_Hafer_-_oat_-_Flughafer_1.jpg/640px-Avena_sativa_-_Hafer_-_oat_-_Flughafer_1.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Ragi..."
curl -s -o "$IMAGES_DIR/ragi.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/FingerMillet.jpg/640px-FingerMillet.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Chips..."
curl -s -o "$IMAGES_DIR/chips.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Potato-Chips.jpg/640px-Potato-Chips.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Water..."
curl -s -o "$IMAGES_DIR/water.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Water_drop_impact_on_a_water-surface_-_%281%29.jpg/640px-Water_drop_impact_on_a_water-surface_-_%281%29.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Lemon juice..."
curl -s -o "$IMAGES_DIR/lemon_juice.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Lemon_juice_glasses.jpg/640px-Lemon_juice_glasses.jpg" && echo "OK" || echo "FAILED"

echo "Downloading Soft drinks..."
curl -s -o "$IMAGES_DIR/soft_drinks.jpg" "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Soft_drink_servings.jpg/640px-Soft_drink_servings.jpg" && echo "OK" || echo "FAILED"

echo ""
echo "=================================================="
echo "Images downloaded to: $IMAGES_DIR"
echo "=================================================="
ls -lah "$IMAGES_DIR" | tail -n +4
