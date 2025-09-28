# pos_app/management/commands/data/groceries.py
# Comprehensive list of groceries popular in Kenya

GROCERIES_PRODUCTS = [
    # Cereals & Grains
    {
        'name': 'Wheat Flour 2kg',
        'description': 'Pembe Wheat Flour 2kg',
        'sku': 'WF2K',
        'purchase_price': 165.00,
        'selling_price': 220.00,
        'unit': 'pcs',
        'image': 'product_images/wheat_flour_2kg.jpg'
    },
    {
        'name': 'Maize Flour 2kg',
        'description': 'Jogoo Maize Flour 2kg',
        'sku': 'MF2K',
        'purchase_price': 145.00,
        'selling_price': 190.00,
        'unit': 'pcs',
        'image': 'product_images/maize_flour_2kg.jpg'
    },
    {
        'name': 'Rice 2kg Basmati',
        'description': 'Basmati Rice 2kg',
        'sku': 'RB2K',
        'purchase_price': 485.00,
        'selling_price': 650.00,
        'unit': 'pcs',
        'image': 'product_images/basmati_rice.jpg'
    },
    {
        'name': 'Rice 2kg Pishori',
        'description': 'Pishori Rice 2kg',
        'sku': 'RP2K',
        'purchase_price': 325.00,
        'selling_price': 420.00,
        'unit': 'pcs',
        'image': 'product_images/pishori_rice.jpg'
    },
    {
        'name': 'Oats 500g',
        'description': 'Quaker Oats 500g',
        'sku': 'OAT500',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/oats.jpg'
    },
    {
        'name': 'Cornflakes 500g',
        'description': 'Kelloggs Cornflakes',
        'sku': 'CF500',
        'purchase_price': 385.00,
        'selling_price': 520.00,
        'unit': 'pcs',
        'image': 'product_images/cornflakes.jpg'
    },
    {
        'name': 'Weetabix 430g',
        'description': 'Weetabix Cereal',
        'sku': 'WB430',
        'purchase_price': 485.00,
        'selling_price': 650.00,
        'unit': 'pcs',
        'image': 'product_images/weetabix.jpg'
    },
    
    # Legumes & Pulses
    {
        'name': 'Green Grams 1kg',
        'description': 'Ndengu Green Grams',
        'sku': 'GG1K',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/green_grams.jpg'
    },
    {
        'name': 'Red Kidney Beans 1kg',
        'description': 'Maharagwe Red Beans',
        'sku': 'RB1K',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/red_beans.jpg'
    },
    {
        'name': 'Black Beans 1kg',
        'description': 'Maharagwe Black Beans',
        'sku': 'BB1K',
        'purchase_price': 165.00,
        'selling_price': 220.00,
        'unit': 'pcs',
        'image': 'product_images/black_beans.jpg'
    },
    {
        'name': 'Lentils 500g',
        'description': 'Red Lentils (Kamande)',
        'sku': 'LEN500',
        'purchase_price': 95.00,
        'selling_price': 130.00,
        'unit': 'pcs',
        'image': 'product_images/lentils.jpg'
    },
    {
        'name': 'Cowpeas 1kg',
        'description': 'Kunde Cowpeas',
        'sku': 'CP1K',
        'purchase_price': 145.00,
        'selling_price': 190.00,
        'unit': 'pcs',
        'image': 'product_images/cowpeas.jpg'
    },
    
    # Cooking Oils & Fats
    {
        'name': 'Cooking Oil 2L',
        'description': 'Elianto Cooking Oil 2L',
        'sku': 'CO2L',
        'purchase_price': 485.00,
        'selling_price': 650.00,
        'unit': 'pcs',
        'image': 'product_images/cooking_oil_2l.jpg'
    },
    {
        'name': 'Olive Oil 500ml',
        'description': 'Extra Virgin Olive Oil',
        'sku': 'OO500',
        'purchase_price': 885.00,
        'selling_price': 1200.00,
        'unit': 'pcs',
        'image': 'product_images/olive_oil.jpg'
    },
    {
        'name': 'Margarine 500g',
        'description': 'Prestige Margarine',
        'sku': 'MAR500',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/margarine.jpg'
    },
    {
        'name': 'Butter 500g',
        'description': 'KCC Butter',
        'sku': 'BUT500',
        'purchase_price': 485.00,
        'selling_price': 650.00,
        'unit': 'pcs',
        'image': 'product_images/butter.jpg'
    },
    
    # Spices & Seasonings
    {
        'name': 'Cumin Powder 100g',
        'description': 'Ground Cumin (Jira)',
        'sku': 'CUM100',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/cumin.jpg'
    },
    {
        'name': 'Coriander Powder 100g',
        'description': 'Ground Coriander (Dhania)',
        'sku': 'COR100',
        'purchase_price': 75.00,
        'selling_price': 105.00,
        'unit': 'pcs',
        'image': 'product_images/coriander.jpg'
    },
    {
        'name': 'Turmeric Powder 100g',
        'description': 'Ground Turmeric (Manjano)',
        'sku': 'TUR100',
        'purchase_price': 95.00,
        'selling_price': 130.00,
        'unit': 'pcs',
        'image': 'product_images/turmeric.jpg'
    },
    {
        'name': 'Chili Powder 100g',
        'description': 'Ground Chili Powder (Pilipili)',
        'sku': 'CHL100',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/chili_powder.jpg'
    },
    {
        'name': 'Garam Masala 100g',
        'description': 'Garam Masala Spice Mix',
        'sku': 'GM100',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/garam_masala.jpg'
    },
    {
        'name': 'Curry Powder 100g',
        'description': 'Curry Powder Mix',
        'sku': 'CRY100',
        'purchase_price': 95.00,
        'selling_price': 130.00,
        'unit': 'pcs',
        'image': 'product_images/curry_powder.jpg'
    },
    {
        'name': 'Ginger Garlic Paste 300g',
        'description': 'Ready Ginger Garlic Paste',
        'sku': 'GGP300',
        'purchase_price': 145.00,
        'selling_price': 190.00,
        'unit': 'pcs',
        'image': 'product_images/ginger_garlic.jpg'
    },
    {
        'name': 'Black Pepper 50g',
        'description': 'Ground Black Pepper',
        'sku': 'BP50',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/black_pepper.jpg'
    },
    
    # Tea & Coffee
    {
        'name': 'Kenya Tea 100 Bags',
        'description': 'Ketepa Tea Bags',
        'sku': 'KT100',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/tea_leave.jpg'
    },
    {
        'name': 'Tangawizi Tea 25 Bags',
        'description': 'Ginger Tea Bags',
        'sku': 'TT25',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/ginger_tea.jpg'
    },
    {
        'name': 'Lipton Tea 100 Bags',
        'description': 'Lipton Yellow Label Tea',
        'sku': 'LT100',
        'purchase_price': 285.00,
        'selling_price': 380.00,
        'unit': 'pcs',
        'image': 'product_images/lipton.jpg'
    },
    {
        'name': 'Coffee Beans 500g',
        'description': 'Kenyan AA Coffee Beans',
        'sku': 'CB500',
        'purchase_price': 485.00,
        'selling_price': 650.00,
        'unit': 'pcs',
        'image': 'product_images/coffee_beans.jpg'
    },
    {
        'name': 'Instant Coffee 100g',
        'description': 'Nescafe Classic Instant Coffee',
        'sku': 'IC100',
        'purchase_price': 385.00,
        'selling_price': 520.00,
        'unit': 'pcs',
        'image': 'product_images/nescafe.jpg'
    },
    
    # Canned & Preserved Foods
    {
        'name': 'Canned Tomatoes 400g',
        'description': 'Del Monte Canned Tomatoes',
        'sku': 'CT400',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/canned_tomatoes.jpg'
    },
    {
        'name': 'Tomato Paste 70g',
        'description': 'Del Monte Tomato Paste',
        'sku': 'TP70',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/tomato_paste.jpg'
    },
    {
        'name': 'Canned Beans 400g',
        'description': 'Del Monte Baked Beans',
        'sku': 'CB400',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/canned_beans.jpg'
    },
    {
        'name': 'Tuna Fish 185g',
        'description': 'Tuna Fish in Brine',
        'sku': 'TF185',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/tuna.jpg'
    },
    {
        'name': 'Sardines 125g',
        'description': 'Sardines in Tomato Sauce',
        'sku': 'SAR125',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/sardines.jpg'
    },
    
    # Pasta & Noodles
    {
        'name': 'Spaghetti 500g',
        'description': 'Pasta Spaghetti',
        'sku': 'SPA500',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/spaghetti.jpg'
    },
    {
        'name': 'Macaroni 500g',
        'description': 'Pasta Macaroni',
        'sku': 'MAC500',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/macaroni.jpg'
    },
    {
        'name': 'Indomie Noodles',
        'description': 'Indomie Instant Noodles',
        'sku': 'IND01',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/indomie.jpg'
    },
    {
        'name': 'Maggi Noodles',
        'description': 'Maggi 2-Minute Noodles',
        'sku': 'MGN01',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/maggi_noodles.jpg'
    },
    
    # Dairy Products
    {
        'name': 'UHT Milk 500ml',
        'description': 'Brookside UHT Milk',
        'sku': 'UHT500',
        'purchase_price': 65.00,
        'selling_price': 85.00,
        'unit': 'pcs',
        'image': 'product_images/uht_milk.jpg'
    },
    {
        'name': 'UHT Milk 1L',
        'description': 'Brookside UHT Milk 1L',
        'sku': 'UHT1L',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/uht_milk_1l.jpg'
    },
    {
        'name': 'Yoghurt 500ml',
        'description': 'Brookside Natural Yoghurt',
        'sku': 'YOG500',
        'purchase_price': 95.00,
        'selling_price': 130.00,
        'unit': 'pcs',
        'image': 'product_images/yoghurt.jpg'
    },
    {
        'name': 'Cheese 200g',
        'description': 'KCC Cheddar Cheese',
        'sku': 'CHE200',
        'purchase_price': 285.00,
        'selling_price': 380.00,
        'unit': 'pcs',
        'image': 'product_images/cheese.jpg'
    },
    
    # Eggs
    {
        'name': 'Eggs Tray (30 pieces)',
        'description': 'Fresh Chicken Eggs',
        'sku': 'EGG30',
        'purchase_price': 385.00,
        'selling_price': 520.00,
        'unit': 'pcs',
        'image': 'product_images/eggs_tray.jpg'
    },
    {
        'name': 'Eggs (6 pieces)',
        'description': 'Fresh Chicken Eggs Pack',
        'sku': 'EGG06',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/eggs_6.jpg'
    },
    
    # Bread & Bakery
    {
        'name': 'White Bread 400g',
        'description': 'Festive White Bread',
        'sku': 'WB400',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/white_bread.jpg'
    },
    {
        'name': 'Brown Bread 400g',
        'description': 'Festive Brown Bread',
        'sku': 'BB400',
        'purchase_price': 55.00,
        'selling_price': 75.00,
        'unit': 'pcs',
        'image': 'product_images/brown_bread.jpg'
    },
    {
        'name': 'Chapati (Pack of 4)',
        'description': 'Ready Made Chapati',
        'sku': 'CHA04',
        'purchase_price': 65.00,
        'selling_price': 90.00,
        'unit': 'pcs',
        'image': 'product_images/chapati.jpg'
    },
    
    # Condiments & Sauces
    {
        'name': 'Ketchup 340g',
        'description': 'Del Monte Tomato Ketchup',
        'sku': 'KET340',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/ketchup.jpg'
    },
    {
        'name': 'Mayonnaise 473ml',
        'description': 'Heinz Mayonnaise',
        'sku': 'MAY473',
        'purchase_price': 285.00,
        'selling_price': 380.00,
        'unit': 'pcs',
        'image': 'product_images/mayonnaise.jpg'
    },
    {
        'name': 'Soy Sauce 150ml',
        'description': 'Kimbo Soy Sauce',
        'sku': 'SOY150',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/soy_sauce.jpg'
    },
    {
        'name': 'Vinegar 500ml',
        'description': 'White Vinegar',
        'sku': 'VIN500',
        'purchase_price': 65.00,
        'selling_price': 90.00,
        'unit': 'pcs',
        'image': 'product_images/vinegar.jpg'
    },
    {
        'name': 'Cooking Wine 375ml',
        'description': 'Cooking Wine Red',
        'sku': 'CW375',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/cooking_wine.jpg'
    },
    
    # Sweeteners
    {
        'name': 'Honey 500g',
        'description': 'Natural Bee Honey',
        'sku': 'HON500',
        'purchase_price': 485.00,
        'selling_price': 650.00,
        'unit': 'pcs',
        'image': 'product_images/honey.jpg'
    },
    {
        'name': 'Brown Sugar 1kg',
        'description': 'Mumias Brown Sugar',
        'sku': 'BS1K',
        'purchase_price': 145.00,
        'selling_price': 190.00,
        'unit': 'pcs',
        'image': 'product_images/brown_sugar.jpg'
    },
    
    # Frozen Foods
    {
        'name': 'Frozen Chicken 1kg',
        'description': 'Frozen Chicken Pieces',
        'sku': 'FC1K',
        'purchase_price': 385.00,
        'selling_price': 520.00,
        'unit': 'pcs',
        'image': 'product_images/frozen_chicken.jpg'
    },
    {
        'name': 'Frozen Fish 1kg',
        'description': 'Frozen Tilapia Fish',
        'sku': 'FF1K',
        'purchase_price': 485.00,
        'selling_price': 650.00,
        'unit': 'pcs',
        'image': 'product_images/frozen_fish.jpg'
    },
    {
        'name': 'Frozen Vegetables 500g',
        'description': 'Mixed Frozen Vegetables',
        'sku': 'FV500',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/frozen_vegetables.jpg'
    },
]