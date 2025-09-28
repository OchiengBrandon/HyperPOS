# Kenyan Products Population System

This Django management command system populates comprehensive product catalogs for Kenyan businesses with over 200+ products across multiple categories.

## Overview

The system consists of:
- **Main Command**: `populate_kenyan_products.py`
- **Product Data Files**: Organized in separate files by category
- **Categories Covered**: 4 major categories with 217+ products

## Product Categories & Count

### 1. Drinks & Beverages (57 products)
- **Soft Drinks**: Coca Cola, Pepsi, Sprite, Fanta varieties
- **Juices**: Minute Maid, Delmonte, Quencher, Ribena
- **Water**: Dasani, Keringet, Aquafina
- **Energy Drinks**: Red Bull, Monster, Power Play
- **Alcoholic Beverages**: Tusker, White Cap, Guinness, wines, spirits
- **Dairy Drinks**: Brookside Milk, Yoghurt
- **Sports Drinks**: Powerade, Gatorade

### 2. Snacks & Confectionery (47 products)
- **Crisps & Chips**: Deepo, Simba, Lays, Pringles
- **Biscuits & Cookies**: Kasuku, Elliot, Marie, Oreo, Digestive
- **Chocolates**: Cadbury, KitKat, Snickers, Mars, Galaxy
- **Sweets & Candies**: Mentos, Tic Tac, Skittles, Haribo
- **Nuts & Seeds**: Peanuts, Cashews, Macadamia, Sunflower seeds
- **Local Snacks**: Mutura, Boiled Eggs, Smokies, Samosa, Mandazi
- **Ice Cream**: Wall's varieties, Cornetto, Magnum

### 3. Household Items (56 products)
- **Detergents**: Omo, Ariel, Persil, Jamaa
- **Cleaning Products**: Vim, Harpic, Jik, Sunlight
- **Personal Care**: Lux, Lifebuoy, Geisha, Lido soaps
- **Oral Care**: Colgate, Close-Up, Aquafresh toothpaste
- **Hair Care**: Sunsilk, TRESemmé, Pantene, Dark & Lovely
- **Deodorants**: Nivea, Sure, Rexona
- **Paper Products**: Tissue, Toilet paper, Serviettes
- **Kitchen Items**: Cooking oil, Salt, Sugar, Flour, Spices
- **Baby Products**: Pampers, Johnson's
- **Insecticides**: Doom, Baygon, Good Knight

### 4. Groceries & Food (57 products)
- **Cereals & Grains**: Wheat flour, Maize flour, Rice, Oats
- **Legumes**: Green grams, Red beans, Lentils, Cowpeas
- **Cooking Oils**: Various sizes of cooking oil, Olive oil, Margarine
- **Spices**: Cumin, Coriander, Turmeric, Curry powder, Garam masala
- **Tea & Coffee**: Kenya Tea, Tangawizi, Lipton, Coffee beans
- **Canned Foods**: Tomatoes, Beans, Tuna, Sardines
- **Pasta & Noodles**: Spaghetti, Macaroni, Indomie, Maggi
- **Dairy**: UHT Milk, Yoghurt, Cheese, Butter
- **Bread & Bakery**: White bread, Brown bread, Chapati
- **Condiments**: Ketchup, Mayonnaise, Soy sauce, Vinegar

## Command Usage

### Basic Usage
```bash
# Populate all categories for all businesses
python manage.py populate_kenyan_products

# Show what would be created (dry run)
python manage.py populate_kenyan_products --dry-run

# Populate specific categories only
python manage.py populate_kenyan_products --categories drinks snacks

# Populate for a specific business
python manage.py populate_kenyan_products --business-id 1

# Clear existing products before populating
python manage.py populate_kenyan_products --clear-existing
```

### Available Options

- `--business-id`: Target a specific business by ID
- `--clear-existing`: Remove existing categories/products first
- `--categories`: Choose specific categories (drinks, snacks, household, groceries, or all)
- `--dry-run`: Preview what will be created without making changes

### Category-Specific Population
```bash
# Just drinks
python manage.py populate_kenyan_products --categories drinks

# Multiple specific categories
python manage.py populate_kenyan_products --categories drinks snacks household

# All categories (default)
python manage.py populate_kenyan_products --categories all
```

## Product Features

Each product includes:
- **Name**: Descriptive product name with size/brand
- **Description**: Additional product details
- **SKU**: Unique stock keeping unit code
- **Purchase Price**: Cost price in KSh (Kenyan Shillings)
- **Selling Price**: Retail price in KSh
- **Unit**: Measurement unit (pieces, kg, liters, etc.)
- **Image Path**: Placeholder for product images
- **Stock Quantity**: Random initial stock (10-100 units)

## Pricing Strategy

All prices are set with realistic Kenyan market rates:
- **Markup**: Typically 30-50% profit margin
- **Currency**: Kenyan Shillings (KSh)
- **Market Research**: Based on actual Kenyan retail prices
- **Range**: From KSh 5 (matches) to KSh 1600+ (premium items)

## Image Management

Product images are referenced with paths like:
- `product_images/coca_cola_500ml.jpg`
- `product_images/omo_500g.jpg`
- `product_images/lido_soap.jpg`

Upload corresponding images to your media folder for full functionality.

## File Structure
```
pos_app/management/commands/
├── populate_kenyan_products.py      # Main command
└── data/
    ├── __init__.py
    ├── drinks.py                    # 57 drink products
    ├── snacks_confectionery.py      # 47 snack products
    ├── household_items.py           # 56 household products
    └── groceries.py                 # 57 grocery products
```

## Business Benefits

1. **Quick Setup**: New businesses get 217+ products instantly
2. **Market-Ready**: All products are popular in Kenya
3. **Realistic Pricing**: Based on actual market rates
4. **Comprehensive Coverage**: Covers most retail business needs
5. **Easy Customization**: Modify prices/products as needed
6. **Professional Catalog**: Well-organized product structure

## Customization

To add more products:
1. Edit the relevant data file (e.g., `drinks.py`)
2. Add products following the existing format
3. Run the command to populate new products

To modify pricing:
1. Update purchase_price and selling_price in data files
2. Re-run with `--clear-existing` to update existing products

## Success Indicators

After running the command successfully, you should see:
- Categories created/updated for each business
- Products added with proper pricing
- Stock quantities assigned randomly
- SKU codes generated for inventory tracking
- Success summary with counts

This system provides a solid foundation for any Kenyan retail business to get started quickly with a comprehensive product catalog.