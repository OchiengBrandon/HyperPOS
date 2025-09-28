# pos_app/management/commands/data/household_items.py
# Comprehensive list of household items popular in Kenya

HOUSEHOLD_ITEMS_PRODUCTS = [
    # Detergents & Cleaning
    {
        'name': 'Omo Washing Powder 500g',
        'description': 'Omo Multi-Active Washing Powder',
        'sku': 'OMO500',
        'purchase_price': 165.00,
        'selling_price': 220.00,
        'unit': 'pcs',
        'image': 'product_images/omo_500g.jpg'
    },
    {
        'name': 'Omo Washing Powder 1kg',
        'description': 'Omo Multi-Active Washing Powder 1kg',
        'sku': 'OMO1K',
        'purchase_price': 295.00,
        'selling_price': 380.00,
        'unit': 'pcs',
        'image': 'product_images/omo_1kg.jpg'
    },
    {
        'name': 'Ariel Washing Powder 500g',
        'description': 'Ariel Complete Washing Powder',
        'sku': 'ARL500',
        'purchase_price': 175.00,
        'selling_price': 235.00,
        'unit': 'pcs',
        'image': 'product_images/ariel_500g.jpg'
    },
    {
        'name': 'Persil Washing Powder 1kg',
        'description': 'Persil Bio Washing Powder',
        'sku': 'PER1K',
        'purchase_price': 385.00,
        'selling_price': 480.00,
        'unit': 'pcs',
        'image': 'product_images/persil_1kg.jpg'
    },
    {
        'name': 'Sunlight Bar Soap 250g',
        'description': 'Sunlight Laundry Bar Soap',
        'sku': 'SL250',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/sunlight_bar.jpg'
    },
    {
        'name': 'Jamaa Detergent 2kg',
        'description': 'Jamaa Washing Detergent',
        'sku': 'JAM2K',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/jamaa_2kg.jpg'
    },
    {
        'name': 'Vim Dishwashing Liquid 500ml',
        'description': 'Vim Dishwashing Liquid',
        'sku': 'VIM500',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/vim_liquid.jpg'
    },
    {
        'name': 'Vim Scouring Powder 500g',
        'description': 'Vim Scouring Powder',
        'sku': 'VIMS500',
        'purchase_price': 65.00,
        'selling_price': 90.00,
        'unit': 'pcs',
        'image': 'product_images/vim_powder.jpg'
    },
    {
        'name': 'Harpic Toilet Cleaner 500ml',
        'description': 'Harpic Power Plus Toilet Cleaner',
        'sku': 'HAR500',
        'purchase_price': 145.00,
        'selling_price': 195.00,
        'unit': 'pcs',
        'image': 'product_images/harpic.jpg'
    },
    {
        'name': 'Jik Bleach 500ml',
        'description': 'Jik Original Bleach',
        'sku': 'JIK500',
        'purchase_price': 55.00,
        'selling_price': 75.00,
        'unit': 'pcs',
        'image': 'product_images/jik.jpg'
    },
    
    # Personal Care
    {
        'name': 'Lux Beauty Soap 175g',
        'description': 'Lux Beauty Bar Soap',
        'sku': 'LUX175',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/lux_soap.jpg'
    },
    {
        'name': 'Lifebuoy Soap 175g',
        'description': 'Lifebuoy Antibacterial Soap',
        'sku': 'LB175',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/lifebuoy.jpg'
    },
    {
        'name': 'Geisha Soap 200g',
        'description': 'Geisha Beauty Soap',
        'sku': 'GS200',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/geisha.jpg'
    },
    {
        'name': 'Lido Soap 200g',
        'description': 'Lido Medicated Soap',
        'sku': 'LIDO200',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/lido_soap.jpg'
    },
    {
        'name': 'Colgate Toothpaste 100ml',
        'description': 'Colgate Total Toothpaste',
        'sku': 'COL100',
        'purchase_price': 135.00,
        'selling_price': 180.00,
        'unit': 'pcs',
        'image': 'product_images/colgate.jpg'
    },
    {
        'name': 'Close-Up Toothpaste 100ml',
        'description': 'Close-Up Red Hot Toothpaste',
        'sku': 'CU100',
        'purchase_price': 125.00,
        'selling_price': 165.00,
        'unit': 'pcs',
        'image': 'product_images/closeup.jpg'
    },
    {
        'name': 'Aquafresh Toothpaste 100ml',
        'description': 'Aquafresh Triple Protection',
        'sku': 'AQF100',
        'purchase_price': 145.00,
        'selling_price': 190.00,
        'unit': 'pcs',
        'image': 'product_images/aquafresh.jpg'
    },
    {
        'name': 'Oral-B Toothbrush',
        'description': 'Oral-B Medium Toothbrush',
        'sku': 'OB01',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/oral_b.jpg'
    },
    
    # Shampoo & Hair Care
    {
        'name': 'Sunsilk Shampoo 200ml',
        'description': 'Sunsilk Perfect Straight Shampoo',
        'sku': 'SS200',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/sunsilk.jpg'
    },
    {
        'name': 'TRESemmé Shampoo 185ml',
        'description': 'TRESemmé Keratin Smooth',
        'sku': 'TRE185',
        'purchase_price': 285.00,
        'selling_price': 380.00,
        'unit': 'pcs',
        'image': 'product_images/tresemme.jpg'
    },
    {
        'name': 'Pantene Shampoo 200ml',
        'description': 'Pantene Pro-V Gold Series',
        'sku': 'PAN200',
        'purchase_price': 235.00,
        'selling_price': 315.00,
        'unit': 'pcs',
        'image': 'product_images/pantene.jpg'
    },
    {
        'name': 'Dark & Lovely Relaxer Kit',
        'description': 'Dark & Lovely Hair Relaxer',
        'sku': 'DL01',
        'purchase_price': 385.00,
        'selling_price': 520.00,
        'unit': 'pcs',
        'image': 'product_images/dark_lovely.jpg'
    },
    {
        'name': 'TCB Hair Relaxer Kit',
        'description': 'TCB No Base Relaxer',
        'sku': 'TCB01',
        'purchase_price': 285.00,
        'selling_price': 385.00,
        'unit': 'pcs',
        'image': 'product_images/tcb.jpg'
    },
    
    # Deodorants & Body Care
    {
        'name': 'Nivea Roll-On Men 50ml',
        'description': 'Nivea Men Deodorant Roll-On',
        'sku': 'NM50',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/nivea_men.jpg'
    },
    {
        'name': 'Nivea Roll-On Women 50ml',
        'description': 'Nivea Women Deodorant Roll-On',
        'sku': 'NW50',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/nivea_women.jpg'
    },
    {
        'name': 'Sure Roll-On 50ml',
        'description': 'Sure Anti-Perspirant Roll-On',
        'sku': 'SU50',
        'purchase_price': 165.00,
        'selling_price': 220.00,
        'unit': 'pcs',
        'image': 'product_images/sure.jpg'
    },
    {
        'name': 'Rexona Roll-On 50ml',
        'description': 'Rexona Anti-Perspirant Roll-On',
        'sku': 'REX50',
        'purchase_price': 165.00,
        'selling_price': 220.00,
        'unit': 'pcs',
        'image': 'product_images/rexona.jpg'
    },
    {
        'name': 'Vaseline Petroleum Jelly 100ml',
        'description': 'Vaseline Original Petroleum Jelly',
        'sku': 'VAS100',
        'purchase_price': 95.00,
        'selling_price': 130.00,
        'unit': 'pcs',
        'image': 'product_images/vaseline.jpg'
    },
    
    # Tissue & Paper Products
    {
        'name': 'Tissue Paper (Box)',
        'description': 'Facial Tissue Paper Box',
        'sku': 'TP01',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/tissue_box.jpg'
    },
    {
        'name': 'Toilet Paper 4 Pack',
        'description': 'Soft Toilet Paper 4 Roll Pack',
        'sku': 'TPR04',
        'purchase_price': 285.00,
        'selling_price': 380.00,
        'unit': 'pcs',
        'image': 'product_images/toilet_paper.jpg'
    },
    {
        'name': 'Serviettes (Pack)',
        'description': 'Table Serviettes Pack',
        'sku': 'SER01',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/serviettes.jpg'
    },
    
    # Kitchen Items
    {
        'name': 'Cooking Oil 500ml',
        'description': 'Elianto Cooking Oil',
        'sku': 'CO500',
        'purchase_price': 145.00,
        'selling_price': 190.00,
        'unit': 'pcs',
        'image': 'product_images/cooking_oil.jpg'
    },
    {
        'name': 'Cooking Oil 1L',
        'description': 'Fresh Fri Cooking Oil 1L',
        'sku': 'CO1L',
        'purchase_price': 285.00,
        'selling_price': 350.00,
        'unit': 'pcs',
        'image': 'product_images/cooking_oil_1l.jpg'
    },
    {
        'name': 'Salt 500g',
        'description': 'Kensalt Table Salt',
        'sku': 'SALT500',
        'purchase_price': 25.00,
        'selling_price': 40.00,
        'unit': 'pcs',
        'image': 'product_images/salt.jpg'
    },
    {
        'name': 'Sugar 1kg',
        'description': 'Kabras Sugar',
        'sku': 'SUG1K',
        'purchase_price': 125.00,
        'selling_price': 160.00,
        'unit': 'pcs',
        'image': 'product_images/sugar.jpg'
    },
    {
        'name': 'Wheat Flour 1kg',
        'description': 'Exe Wheat Flour',
        'sku': 'WF1K',
        'purchase_price': 85.00,
        'selling_price': 115.00,
        'unit': 'pcs',
        'image': 'product_images/flour.jpg'
    },
    {
        'name': 'Rice 1kg',
        'description': 'Pishori Rice',
        'sku': 'RICE1K',
        'purchase_price': 165.00,
        'selling_price': 220.00,
        'unit': 'pcs',
        'image': 'product_images/rice.jpg'
    },
    {
        'name': 'Maize Flour 1kg',
        'description': 'Exe Maize Flour (Unga)',
        'sku': 'MF1K',
        'purchase_price': 75.00,
        'selling_price': 105.00,
        'unit': 'pcs',
        'image': 'product_images/maize_flour.jpg'
    },
    {
        'name': 'Royco Cubes (10 pack)',
        'description': 'Royco Beef Cubes',
        'sku': 'ROY10',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/royco.jpg'
    },
    {
        'name': 'Maggi Cubes (10 pack)',
        'description': 'Maggi Chicken Cubes',
        'sku': 'MAG10',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/maggi.jpg'
    },
    
    # Matches & Lighters
    {
        'name': 'Safety Matches (1 box)',
        'description': 'Safety Match Box',
        'sku': 'SM01',
        'purchase_price': 5.00,
        'selling_price': 10.00,
        'unit': 'pcs',
        'image': 'product_images/matches.jpg'
    },
    {
        'name': 'BIC Lighter',
        'description': 'BIC Disposable Lighter',
        'sku': 'BIC01',
        'purchase_price': 65.00,
        'selling_price': 90.00,
        'unit': 'pcs',
        'image': 'product_images/bic_lighter.jpg'
    },
    
    # Candles
    {
        'name': 'Candles (5 pack)',
        'description': 'Household Candles',
        'sku': 'CAN05',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/candles.jpg'
    },
    
    # Batteries
    {
        'name': 'AA Batteries (4 pack)',
        'description': 'Eveready AA Batteries',
        'sku': 'BAT04',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/aa_batteries.jpg'
    },
    {
        'name': 'AAA Batteries (4 pack)',
        'description': 'Eveready AAA Batteries',
        'sku': 'BATAAA04',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/aaa_batteries.jpg'
    },
    
    # Insecticides
    {
        'name': 'Doom Insecticide 300ml',
        'description': 'Doom Multi-Insect Killer',
        'sku': 'DOOM300',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/doom.jpg'
    },
    {
        'name': 'Baygon Spray 400ml',
        'description': 'Baygon Flying Insect Killer',
        'sku': 'BAY400',
        'purchase_price': 285.00,
        'selling_price': 380.00,
        'unit': 'pcs',
        'image': 'product_images/baygon.jpg'
    },
    {
        'name': 'Good Knight Coils (10 pack)',
        'description': 'Good Knight Mosquito Coils',
        'sku': 'GK10',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/good_knight.jpg'
    },
    
    # Shoe Care
    {
        'name': 'Kiwi Shoe Polish Black',
        'description': 'Kiwi Black Shoe Polish',
        'sku': 'KIWI01',
        'purchase_price': 95.00,
        'selling_price': 130.00,
        'unit': 'pcs',
        'image': 'product_images/kiwi.jpg'
    },
    {
        'name': 'Shoe Brush',
        'description': 'Shoe Cleaning Brush',
        'sku': 'SB01',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/shoe_brush.jpg'
    },
    
    # Feminine Hygiene
    {
        'name': 'Always Pads Normal (10 pack)',
        'description': 'Always Ultra Normal Pads',
        'sku': 'AL10',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/always.jpg'
    },
    {
        'name': 'Softcare Pads (8 pack)',
        'description': 'Softcare Sanitary Pads',
        'sku': 'SC08',
        'purchase_price': 125.00,
        'selling_price': 170.00,
        'unit': 'pcs',
        'image': 'product_images/softcare.jpg'
    },
    
    # Baby Products
    {
        'name': 'Pampers Diapers Size 3 (20 pack)',
        'description': 'Pampers Baby Dry Diapers',
        'sku': 'PAM20',
        'purchase_price': 885.00,
        'selling_price': 1200.00,
        'unit': 'pcs',
        'image': 'product_images/pampers.jpg'
    },
    {
        'name': 'Johnson\'s Baby Powder 200g',
        'description': 'Johnson\'s Baby Powder',
        'sku': 'JBP200',
        'purchase_price': 285.00,
        'selling_price': 380.00,
        'unit': 'pcs',
        'image': 'product_images/johnsons.jpg'
    },
    
    # Air Fresheners
    {
        'name': 'Glade Air Freshener',
        'description': 'Glade Automatic Spray Refill',
        'sku': 'GL01',
        'purchase_price': 385.00,
        'selling_price': 520.00,
        'unit': 'pcs',
        'image': 'product_images/glade.jpg'
    },
    {
        'name': 'Air Wick Freshener',
        'description': 'Air Wick Automatic Spray',
        'sku': 'AW01',
        'purchase_price': 385.00,
        'selling_price': 520.00,
        'unit': 'pcs',
        'image': 'product_images/air_wick.jpg'
    },
]