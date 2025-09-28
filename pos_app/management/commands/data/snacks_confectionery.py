# pos_app/management/commands/data/snacks_confectionery.py
# Comprehensive list of snacks and confectionery popular in Kenya

SNACKS_CONFECTIONERY_PRODUCTS = [
    # Crisps & Chips
    {
        'name': 'Deepo Crisps Tomato 20g',
        'description': 'Deepo Tomato Flavored Crisps',
        'sku': 'DC20T',
        'purchase_price': 8.00,
        'selling_price': 15.00,
        'unit': 'pcs',
        'image': 'product_images/deepo_tomato.jpg'
    },
    {
        'name': 'Deepo Crisps BBQ 20g',
        'description': 'Deepo BBQ Flavored Crisps',
        'sku': 'DC20B',
        'purchase_price': 8.00,
        'selling_price': 15.00,
        'unit': 'pcs',
        'image': 'product_images/deepo_bbq.jpg'
    },
    {
        'name': 'Deepo Crisps Chilli 20g',
        'description': 'Deepo Chilli Flavored Crisps',
        'sku': 'DC20C',
        'purchase_price': 8.00,
        'selling_price': 15.00,
        'unit': 'pcs',
        'image': 'product_images/deepo_chilli.jpg'
    },
    {
        'name': 'Simba Crisps Tomato 45g',
        'description': 'Simba Tomato Flavored Crisps',
        'sku': 'SC45T',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/simba_tomato.jpg'
    },
    {
        'name': 'Simba Crisps Cheese 45g',
        'description': 'Simba Cheese Flavored Crisps',
        'sku': 'SC45CH',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/simba_cheese.jpg'
    },
    {
        'name': 'Simba Crisps BBQ 45g',
        'description': 'Simba BBQ Flavored Crisps',
        'sku': 'SC45B',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/simba_bbq.jpg'
    },
    {
        'name': 'Lays Crisps Original 40g',
        'description': 'Lays Original Flavored Crisps',
        'sku': 'LC40O',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/lays_original.jpg'
    },
    {
        'name': 'Pringles Original 110g',
        'description': 'Pringles Original Potato Crisps',
        'sku': 'PR110',
        'purchase_price': 285.00,
        'selling_price': 380.00,
        'unit': 'pcs',
        'image': 'product_images/pringles.jpg'
    },
    
    # Biscuits & Cookies
    {
        'name': 'Kasuku Biscuits 400g',
        'description': 'Kasuku Sweet Biscuits',
        'sku': 'KB400',
        'purchase_price': 75.00,
        'selling_price': 100.00,
        'unit': 'pcs',
        'image': 'product_images/kasuku_biscuits.jpg'
    },
    {
        'name': 'Elliot Biscuits 400g',
        'description': 'Elliot Sweet Biscuits',
        'sku': 'EB400',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/elliot_biscuits.jpg'
    },
    {
        'name': 'Marie Biscuits 400g',
        'description': 'Marie Plain Biscuits',
        'sku': 'MB400',
        'purchase_price': 65.00,
        'selling_price': 90.00,
        'unit': 'pcs',
        'image': 'product_images/marie_biscuits.jpg'
    },
    {
        'name': 'Oreo Cookies 154g',
        'description': 'Oreo Chocolate Cookies',
        'sku': 'OR154',
        'purchase_price': 135.00,
        'selling_price': 180.00,
        'unit': 'pcs',
        'image': 'product_images/oreo.jpg'
    },
    {
        'name': 'Digestive Biscuits 400g',
        'description': 'Wheat Digestive Biscuits',
        'sku': 'DB400',
        'purchase_price': 95.00,
        'selling_price': 130.00,
        'unit': 'pcs',
        'image': 'product_images/digestive.jpg'
    },
    
    # Chocolates & Sweets
    {
        'name': 'Cadbury Dairy Milk 37g',
        'description': 'Cadbury Dairy Milk Chocolate',
        'sku': 'CDM37',
        'purchase_price': 65.00,
        'selling_price': 90.00,
        'unit': 'pcs',
        'image': 'product_images/dairy_milk.jpg'
    },
    {
        'name': 'KitKat 4 Finger 41g',
        'description': 'KitKat 4 Finger Chocolate Bar',
        'sku': 'KK41',
        'purchase_price': 75.00,
        'selling_price': 105.00,
        'unit': 'pcs',
        'image': 'product_images/kitkat.jpg'
    },
    {
        'name': 'Snickers 50g',
        'description': 'Snickers Peanut Chocolate Bar',
        'sku': 'SN50',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/snickers.jpg'
    },
    {
        'name': 'Mars Bar 51g',
        'description': 'Mars Caramel Chocolate Bar',
        'sku': 'MB51',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/mars.jpg'
    },
    {
        'name': 'Galaxy Smooth Milk 40g',
        'description': 'Galaxy Smooth Milk Chocolate',
        'sku': 'GSM40',
        'purchase_price': 75.00,
        'selling_price': 105.00,
        'unit': 'pcs',
        'image': 'product_images/galaxy.jpg'
    },
    {
        'name': 'Bounty 57g',
        'description': 'Bounty Coconut Chocolate Bar',
        'sku': 'BT57',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/bounty.jpg'
    },
    {
        'name': 'Toblerone 100g',
        'description': 'Toblerone Swiss Chocolate',
        'sku': 'TB100',
        'purchase_price': 385.00,
        'selling_price': 520.00,
        'unit': 'pcs',
        'image': 'product_images/toblerone.jpg'
    },
    
    # Chewing Gum
    {
        'name': 'Trident Mint Gum',
        'description': 'Trident Mint Chewing Gum',
        'sku': 'TG01',
        'purchase_price': 15.00,
        'selling_price': 25.00,
        'unit': 'pcs',
        'image': 'product_images/trident.jpg'
    },
    {
        'name': 'Orbit Spearmint',
        'description': 'Orbit Spearmint Chewing Gum',
        'sku': 'OS01',
        'purchase_price': 15.00,
        'selling_price': 25.00,
        'unit': 'pcs',
        'image': 'product_images/orbit.jpg'
    },
    {
        'name': 'Big G Bubblegum',
        'description': 'Big G Strawberry Bubblegum',
        'sku': 'BG01',
        'purchase_price': 5.00,
        'selling_price': 10.00,
        'unit': 'pcs',
        'image': 'product_images/big_g.jpg'
    },
    
    # Sweets/Candies
    {
        'name': 'Mentos Mint',
        'description': 'Mentos Fresh Mint Sweets',
        'sku': 'MM01',
        'purchase_price': 25.00,
        'selling_price': 40.00,
        'unit': 'pcs',
        'image': 'product_images/mentos.jpg'
    },
    {
        'name': 'Tic Tac Mint',
        'description': 'Tic Tac Fresh Mint',
        'sku': 'TT01',
        'purchase_price': 35.00,
        'selling_price': 55.00,
        'unit': 'pcs',
        'image': 'product_images/tictac.jpg'
    },
    {
        'name': 'Polo Mints',
        'description': 'Polo The Mint with the Hole',
        'sku': 'PM01',
        'purchase_price': 25.00,
        'selling_price': 40.00,
        'unit': 'pcs',
        'image': 'product_images/polo.jpg'
    },
    {
        'name': 'Skittles 45g',
        'description': 'Skittles Fruit Flavored Candies',
        'sku': 'SK45',
        'purchase_price': 65.00,
        'selling_price': 90.00,
        'unit': 'pcs',
        'image': 'product_images/skittles.jpg'
    },
    {
        'name': 'Haribo Goldbears 100g',
        'description': 'Haribo Goldbears Gummy Bears',
        'sku': 'HG100',
        'purchase_price': 145.00,
        'selling_price': 200.00,
        'unit': 'pcs',
        'image': 'product_images/haribo.jpg'
    },
    
    # Nuts & Seeds
    {
        'name': 'Peanuts Roasted 100g',
        'description': 'Roasted Groundnuts',
        'sku': 'PN100',
        'purchase_price': 45.00,
        'selling_price': 70.00,
        'unit': 'pcs',
        'image': 'product_images/peanuts.jpg'
    },
    {
        'name': 'Cashew Nuts 100g',
        'description': 'Roasted Cashew Nuts',
        'sku': 'CN100',
        'purchase_price': 185.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/cashews.jpg'
    },
    {
        'name': 'Macadamia Nuts 100g',
        'description': 'Kenyan Macadamia Nuts',
        'sku': 'MN100',
        'purchase_price': 285.00,
        'selling_price': 400.00,
        'unit': 'pcs',
        'image': 'product_images/macadamia.jpg'
    },
    {
        'name': 'Sunflower Seeds 50g',
        'description': 'Roasted Sunflower Seeds',
        'sku': 'SS50',
        'purchase_price': 35.00,
        'selling_price': 55.00,
        'unit': 'pcs',
        'image': 'product_images/sunflower_seeds.jpg'
    },
    
    # Popcorn
    {
        'name': 'Popcorn Sweet 50g',
        'description': 'Sweet Popcorn Pack',
        'sku': 'PC50S',
        'purchase_price': 25.00,
        'selling_price': 40.00,
        'unit': 'pcs',
        'image': 'product_images/popcorn_sweet.jpg'
    },
    {
        'name': 'Popcorn Salted 50g',
        'description': 'Salted Popcorn Pack',
        'sku': 'PC50SA',
        'purchase_price': 25.00,
        'selling_price': 40.00,
        'unit': 'pcs',
        'image': 'product_images/popcorn_salt.jpg'
    },
    
    # Local Snacks
    {
        'name': 'Mutura (per piece)',
        'description': 'Kenyan Traditional Sausage',
        'sku': 'MUT01',
        'purchase_price': 15.00,
        'selling_price': 30.00,
        'unit': 'pcs',
        'image': 'product_images/mutura.jpg'
    },
    {
        'name': 'Boiled Eggs (2 pieces)',
        'description': 'Hard Boiled Eggs',
        'sku': 'BE02',
        'purchase_price': 20.00,
        'selling_price': 35.00,
        'unit': 'pcs',
        'image': 'product_images/boiled_eggs.jpg'
    },
    {
        'name': 'Smokies (2 pieces)',
        'description': 'Kenyan Cocktail Sausages',
        'sku': 'SM02',
        'purchase_price': 25.00,
        'selling_price': 45.00,
        'unit': 'pcs',
        'image': 'product_images/smokies.jpg'
    },
    {
        'name': 'Samosa (per piece)',
        'description': 'Fried Samosa',
        'sku': 'SAM01',
        'purchase_price': 15.00,
        'selling_price': 30.00,
        'unit': 'pcs',
        'image': 'product_images/samosa.jpg'
    },
    {
        'name': 'Mandazi (per piece)',
        'description': 'Kenyan Sweet Fried Bread',
        'sku': 'MAN01',
        'purchase_price': 8.00,
        'selling_price': 15.00,
        'unit': 'pcs',
        'image': 'product_images/mandazi.jpg'
    },
    
    # Crackers
    {
        'name': 'Jacobs Cream Crackers 200g',
        'description': 'Jacobs Cream Crackers',
        'sku': 'JCC200',
        'purchase_price': 95.00,
        'selling_price': 130.00,
        'unit': 'pcs',
        'image': 'product_images/jacobs_crackers.jpg'
    },
    {
        'name': 'TUC Crackers 100g',
        'description': 'TUC Original Crackers',
        'sku': 'TUC100',
        'purchase_price': 75.00,
        'selling_price': 105.00,
        'unit': 'pcs',
        'image': 'product_images/tuc.jpg'
    },
    
    # Ice Cream (for shops with freezers)
    {
        'name': 'Wall\'s Ice Cream Vanilla',
        'description': 'Wall\'s Vanilla Ice Cream Cup',
        'sku': 'WIC01',
        'purchase_price': 65.00,
        'selling_price': 90.00,
        'unit': 'pcs',
        'image': 'product_images/walls_vanilla.jpg'
    },
    {
        'name': 'Wall\'s Cornetto',
        'description': 'Wall\'s Cornetto Ice Cream Cone',
        'sku': 'WC01',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/cornetto.jpg'
    },
    {
        'name': 'Magnum Ice Cream',
        'description': 'Magnum Premium Ice Cream',
        'sku': 'MAG01',
        'purchase_price': 145.00,
        'selling_price': 200.00,
        'unit': 'pcs',
        'image': 'product_images/magnum.jpg'
    },
    
    # Cake & Pastries
    {
        'name': 'Queen Cakes (4 pack)',
        'description': 'Mini Queen Cakes',
        'sku': 'QC04',
        'purchase_price': 45.00,
        'selling_price': 70.00,
        'unit': 'pcs',
        'image': 'product_images/queen_cakes.jpg'
    },
    {
        'name': 'Doughnuts (per piece)',
        'description': 'Sugar Glazed Doughnut',
        'sku': 'DG01',
        'purchase_price': 25.00,
        'selling_price': 40.00,
        'unit': 'pcs',
        'image': 'product_images/doughnut.jpg'
    },
    {
        'name': 'Muffin Chocolate (per piece)',
        'description': 'Chocolate Chip Muffin',
        'sku': 'MFC01',
        'purchase_price': 55.00,
        'selling_price': 80.00,
        'unit': 'pcs',
        'image': 'product_images/chocolate_muffin.jpg'
    },
]