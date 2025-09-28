# pos_app/management/commands/data/drinks.py
# Comprehensive list of drinks popular in Kenya

DRINKS_PRODUCTS = [
    # Soft Drinks - Coca Cola Products
    {
        'name': 'Coca Cola 300ml',
        'description': 'Classic Coca Cola soft drink',
        'sku': 'CC300',
        'purchase_price': 45.00,
        'selling_price': 60.00,
        'unit': 'pcs',
        'image': 'product_images/Cocacola.jpg'
    },
    {
        'name': 'Coca Cola 500ml',
        'description': 'Coca Cola 500ml bottle',
        'sku': 'CC500',
        'purchase_price': 65.00,
        'selling_price': 80.00,
        'unit': 'pcs',
        'image': 'product_images/coca_cola_500ml.jpg'
    },
    {
        'name': 'Coca Cola 1L',
        'description': 'Coca Cola 1 liter bottle',
        'sku': 'CC1L',
        'purchase_price': 95.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/coca_cola_1l.jpg'
    },
    {
        'name': 'Coca Cola 2L',
        'description': 'Coca Cola 2 liter bottle',
        'sku': 'CC2L',
        'purchase_price': 145.00,
        'selling_price': 180.00,
        'unit': 'pcs',
        'image': 'product_images/coca_cola_2l.jpg'
    },
    {
        'name': 'Sprite 300ml',
        'description': 'Sprite lemon-lime soda',
        'sku': 'SP300',
        'purchase_price': 45.00,
        'selling_price': 60.00,
        'unit': 'pcs',
        'image': 'product_images/sprite_300ml.jpg'
    },
    {
        'name': 'Sprite 500ml',
        'description': 'Sprite 500ml bottle',
        'sku': 'SP500',
        'purchase_price': 65.00,
        'selling_price': 80.00,
        'unit': 'pcs',
        'image': 'product_images/sprite_500ml.jpg'
    },
    {
        'name': 'Fanta Orange 300ml',
        'description': 'Fanta Orange flavored soda',
        'sku': 'FO300',
        'purchase_price': 45.00,
        'selling_price': 60.00,
        'unit': 'pcs',
        'image': 'product_images/fanta_orange_300ml.jpg'
    },
    {
        'name': 'Fanta Orange 500ml',
        'description': 'Fanta Orange 500ml bottle',
        'sku': 'FO500',
        'purchase_price': 65.00,
        'selling_price': 80.00,
        'unit': 'pcs',
        'image': 'product_images/fanta_orange_500ml.jpg'
    },
    {
        'name': 'Fanta Blackcurrant 300ml',
        'description': 'Fanta Blackcurrant flavored soda',
        'sku': 'FB300',
        'purchase_price': 45.00,
        'selling_price': 60.00,
        'unit': 'pcs',
        'image': 'product_images/fanta_blackcurrant.jpg'
    },
    {
        'name': 'Fanta Passion 300ml',
        'description': 'Fanta Passion fruit flavored soda',
        'sku': 'FP300',
        'purchase_price': 45.00,
        'selling_price': 60.00,
        'unit': 'pcs',
        'image': 'product_images/fanta_passion.jpg'
    },
    
    # Pepsi Products
    {
        'name': 'Pepsi 300ml',
        'description': 'Pepsi Cola soft drink',
        'sku': 'PS300',
        'purchase_price': 45.00,
        'selling_price': 60.00,
        'unit': 'pcs',
        'image': 'product_images/pepsi_300ml.jpg'
    },
    {
        'name': 'Pepsi 500ml',
        'description': 'Pepsi Cola 500ml bottle',
        'sku': 'PS500',
        'purchase_price': 65.00,
        'selling_price': 80.00,
        'unit': 'pcs',
        'image': 'product_images/pepsi_500ml.jpg'
    },
    {
        'name': '7UP 300ml',
        'description': '7UP lemon-lime soda',
        'sku': '7UP300',
        'purchase_price': 45.00,
        'selling_price': 60.00,
        'unit': 'pcs',
        'image': 'product_images/7up_300ml.jpg'
    },
    {
        'name': 'Mirinda Orange 300ml',
        'description': 'Mirinda Orange flavored soda',
        'sku': 'MO300',
        'purchase_price': 45.00,
        'selling_price': 60.00,
        'unit': 'pcs',
        'image': 'product_images/mirinda_orange.jpg'
    },
    
    # Local Kenyan Sodas
    {
        'name': 'Stoney Tangawizi 300ml',
        'description': 'Stoney Ginger flavored soda',
        'sku': 'ST300',
        'purchase_price': 45.00,
        'selling_price': 60.00,
        'unit': 'pcs',
        'image': 'product_images/stoney_tangawizi.jpg'
    },
    {
        'name': 'Novida Orange 300ml',
        'description': 'Novida Orange soda',
        'sku': 'NO300',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/novida_orange.jpg'
    },
    {
        'name': 'Alvaro Cola 300ml',
        'description': 'Local Alvaro Cola drink',
        'sku': 'AC300',
        'purchase_price': 30.00,
        'selling_price': 45.00,
        'unit': 'pcs',
        'image': 'product_images/alvaro_cola.jpg'
    },
    
    # Energy Drinks
    {
        'name': 'Red Bull 250ml',
        'description': 'Red Bull Energy Drink',
        'sku': 'RB250',
        'purchase_price': 180.00,
        'selling_price': 220.00,
        'unit': 'pcs',
        'image': 'product_images/redbull.jpg'
    },
    {
        'name': 'Monster Energy 500ml',
        'description': 'Monster Energy Drink',
        'sku': 'ME500',
        'purchase_price': 220.00,
        'selling_price': 280.00,
        'unit': 'pcs',
        'image': 'product_images/monster_energy.jpg'
    },
    {
        'name': 'Power Play Energy 250ml',
        'description': 'Local Power Play Energy Drink',
        'sku': 'PP250',
        'purchase_price': 80.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/power_play.jpg'
    },
    {
        'name': 'Burn Energy 250ml',
        'description': 'Burn Energy Drink',
        'sku': 'BE250',
        'purchase_price': 120.00,
        'selling_price': 150.00,
        'unit': 'pcs',
        'image': 'product_images/burn_energy.jpg'
    },
    
    # Juices
    {
        'name': 'Minute Maid Orange 300ml',
        'description': 'Minute Maid Orange Juice',
        'sku': 'MMO300',
        'purchase_price': 55.00,
        'selling_price': 75.00,
        'unit': 'pcs',
        'image': 'product_images/minute_maid_orange.jpg'
    },
    {
        'name': 'Minute Maid Apple 300ml',
        'description': 'Minute Maid Apple Juice',
        'sku': 'MMA300',
        'purchase_price': 55.00,
        'selling_price': 75.00,
        'unit': 'pcs',
        'image': 'product_images/minute_maid_apple.jpg'
    },
    {
        'name': 'Minute Maid Tropical 300ml',
        'description': 'Minute Maid Tropical Mix Juice',
        'sku': 'MMT300',
        'purchase_price': 55.00,
        'selling_price': 75.00,
        'unit': 'pcs',
        'image': 'product_images/minute_maid_tropical.jpg'
    },
    {
        'name': 'Delmonte Pineapple 1L',
        'description': 'Delmonte Pineapple Juice 1L',
        'sku': 'DP1L',
        'purchase_price': 185.00,
        'selling_price': 230.00,
        'unit': 'pcs',
        'image': 'product_images/delmonte_pineapple.jpg'
    },
    {
        'name': 'Delmonte Orange 1L',
        'description': 'Delmonte Orange Juice 1L',
        'sku': 'DO1L',
        'purchase_price': 185.00,
        'selling_price': 230.00,
        'unit': 'pcs',
        'image': 'product_images/delmonte_orange.jpg'
    },
    {
        'name': 'Delmonte Mango 1L',
        'description': 'Delmonte Mango Juice 1L',
        'sku': 'DM1L',
        'purchase_price': 185.00,
        'selling_price': 230.00,
        'unit': 'pcs',
        'image': 'product_images/delmonte_mango.jpg'
    },
    {
        'name': 'Quencher Orange 500ml',
        'description': 'Quencher Orange Juice drink',
        'sku': 'QO500',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/quencher_orange.jpg'
    },
    {
        'name': 'Quencher Apple 500ml',
        'description': 'Quencher Apple Juice drink',
        'sku': 'QA500',
        'purchase_price': 45.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/quencher_apple.jpg'
    },
    {
        'name': 'Ribena Blackcurrant 330ml',
        'description': 'Ribena Blackcurrant drink',
        'sku': 'RB330',
        'purchase_price': 65.00,
        'selling_price': 85.00,
        'unit': 'pcs',
        'image': 'product_images/ribena.jpg'
    },
    
    # Water
    {
        'name': 'Dasani Water 500ml',
        'description': 'Dasani Purified Water',
        'sku': 'DW500',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/dasani_500ml.jpg'
    },
    {
        'name': 'Dasani Water 1L',
        'description': 'Dasani Purified Water 1L',
        'sku': 'DW1L',
        'purchase_price': 55.00,
        'selling_price': 70.00,
        'unit': 'pcs',
        'image': 'product_images/dasani_1l.jpg'
    },
    {
        'name': 'Keringet Water 500ml',
        'description': 'Keringet Natural Spring Water',
        'sku': 'KW500',
        'purchase_price': 40.00,
        'selling_price': 55.00,
        'unit': 'pcs',
        'image': 'product_images/keringet_500ml.jpg'
    },
    {
        'name': 'Keringet Water 1L',
        'description': 'Keringet Natural Spring Water 1L',
        'sku': 'KW1L',
        'purchase_price': 65.00,
        'selling_price': 80.00,
        'unit': 'pcs',
        'image': 'product_images/keringet_1l.jpg'
    },
    {
        'name': 'Aquafina Water 500ml',
        'description': 'Aquafina Purified Water',
        'sku': 'AW500',
        'purchase_price': 35.00,
        'selling_price': 50.00,
        'unit': 'pcs',
        'image': 'product_images/aquafina_500ml.jpg'
    },
    
    # Tea and Coffee
    {
        'name': 'Kenya Tea Masala Chai Ready to Drink 500ml',
        'description': 'Ready to drink Masala Chai',
        'sku': 'MC500',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/masala_chai.jpg'
    },
    {
        'name': 'Brookside Iced Tea Lemon 500ml',
        'description': 'Brookside Lemon Iced Tea',
        'sku': 'BIT500',
        'purchase_price': 75.00,
        'selling_price': 100.00,
        'unit': 'pcs',
        'image': 'product_images/brookside_iced_tea.jpg'
    },
    {
        'name': 'Nescafe Ready to Drink 240ml',
        'description': 'Nescafe Ready to Drink Coffee',
        'sku': 'NRD240',
        'purchase_price': 95.00,
        'selling_price': 130.00,
        'unit': 'pcs',
        'image': 'product_images/nescafe_rtd.jpg'
    },
    
    # Alcoholic Beverages (for licensed establishments)
    {
        'name': 'Tusker Lager 500ml',
        'description': 'Tusker Premium Lager Beer',
        'sku': 'TL500',
        'purchase_price': 180.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/tusker_lager.jpg'
    },
    {
        'name': 'White Cap Lager 500ml',
        'description': 'White Cap Premium Lager',
        'sku': 'WCL500',
        'purchase_price': 170.00,
        'selling_price': 240.00,
        'unit': 'pcs',
        'image': 'product_images/whitecap.jpg'
    },
    {
        'name': 'Pilsner Lager 500ml',
        'description': 'Pilsner Ice Premium Lager',
        'sku': 'PL500',
        'purchase_price': 170.00,
        'selling_price': 240.00,
        'unit': 'pcs',
        'image': 'product_images/pilsner.jpg'
    },
    {
        'name': 'Guinness 500ml',
        'description': 'Guinness Stout',
        'sku': 'GS500',
        'purchase_price': 200.00,
        'selling_price': 280.00,
        'unit': 'pcs',
        'image': 'product_images/guinness.jpg'
    },
    {
        'name': 'Senator Keg 300ml',
        'description': 'Senator Premium Lager',
        'sku': 'SK300',
        'purchase_price': 120.00,
        'selling_price': 170.00,
        'unit': 'pcs',
        'image': 'product_images/senator.jpg'
    },
    
    # Wine
    {
        'name': 'Drostdy Hof Red Wine 750ml',
        'description': 'Drostdy Hof Red Wine',
        'sku': 'DHR750',
        'purchase_price': 850.00,
        'selling_price': 1200.00,
        'unit': 'pcs',
        'image': 'product_images/drostdy_hof_red.jpg'
    },
    {
        'name': 'Drostdy Hof White Wine 750ml',
        'description': 'Drostdy Hof White Wine',
        'sku': 'DHW750',
        'purchase_price': 850.00,
        'selling_price': 1200.00,
        'unit': 'pcs',
        'image': 'product_images/drostdy_hof_white.jpg'
    },
    {
        'name': '4th Street Wine 750ml',
        'description': '4th Street Natural Sweet Wine',
        'sku': 'FSW750',
        'purchase_price': 650.00,
        'selling_price': 900.00,
        'unit': 'pcs',
        'image': 'product_images/4th_street.jpg'
    },
    
    # Spirits
    {
        'name': 'Kenya Cane 250ml',
        'description': 'Kenya Cane Pure Cane Spirit',
        'sku': 'KC250',
        'purchase_price': 320.00,
        'selling_price': 450.00,
        'unit': 'pcs',
        'image': 'product_images/kenya_cane.jpg'
    },
    {
        'name': 'Chrome Gin 250ml',
        'description': 'Chrome Premium Gin',
        'sku': 'CG250',
        'purchase_price': 350.00,
        'selling_price': 500.00,
        'unit': 'pcs',
        'image': 'product_images/chrome_gin.jpg'
    },
    {
        'name': 'Smirnoff Vodka 350ml',
        'description': 'Smirnoff Premium Vodka',
        'sku': 'SV350',
        'purchase_price': 1200.00,
        'selling_price': 1600.00,
        'unit': 'pcs',
        'image': 'product_images/smirnoff.jpg'
    },
    
    # Traditional/Local Drinks
    {
        'name': 'Muratina 500ml',
        'description': 'Traditional Kenyan Honey Wine',
        'sku': 'MRT500',
        'purchase_price': 250.00,
        'selling_price': 350.00,
        'unit': 'pcs',
        'image': 'product_images/muratina.jpg'
    },
    {
        'name': 'Changaa 250ml',
        'description': 'Traditional Kenyan Spirit',
        'sku': 'CHA250',
        'purchase_price': 150.00,
        'selling_price': 250.00,
        'unit': 'pcs',
        'image': 'product_images/changaa.jpg'
    },
    
    # Dairy Drinks
    {
        'name': 'Brookside Milk 500ml',
        'description': 'Brookside Fresh Milk',
        'sku': 'BM500',
        'purchase_price': 55.00,
        'selling_price': 70.00,
        'unit': 'pcs',
        'image': 'product_images/brookside_milk.jpg'
    },
    {
        'name': 'Brookside Yoghurt Strawberry 500ml',
        'description': 'Brookside Strawberry Drinking Yoghurt',
        'sku': 'BYS500',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/brookside_yoghurt.jpg'
    },
    {
        'name': 'KCC Milk 500ml',
        'description': 'Kenya Co-operative Creameries Milk',
        'sku': 'KCC500',
        'purchase_price': 50.00,
        'selling_price': 65.00,
        'unit': 'pcs',
        'image': 'product_images/kcc_milk.jpg'
    },
    
    # Sports Drinks
    {
        'name': 'Powerade Orange 500ml',
        'description': 'Powerade Sports Drink Orange',
        'sku': 'PO500',
        'purchase_price': 75.00,
        'selling_price': 100.00,
        'unit': 'pcs',
        'image': 'product_images/powerade_orange.jpg'
    },
    {
        'name': 'Powerade Blue 500ml',
        'description': 'Powerade Sports Drink Blue',
        'sku': 'PB500',
        'purchase_price': 75.00,
        'selling_price': 100.00,
        'unit': 'pcs',
        'image': 'product_images/powerade_blue.jpg'
    },
    {
        'name': 'Gatorade Lemon Lime 500ml',
        'description': 'Gatorade Sports Drink',
        'sku': 'GLL500',
        'purchase_price': 85.00,
        'selling_price': 120.00,
        'unit': 'pcs',
        'image': 'product_images/gatorade.jpg'
    },
]