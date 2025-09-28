# Kenyan Products Population Command

## Overview
This Django management command populates default Kenyan categories and products for businesses in the POS system. It includes over 100 popular products commonly found in Kenyan retail businesses.

## Usage

### Populate all businesses:
```bash
python manage.py populate_kenyan_products
```

### Populate a specific business:
```bash
python manage.py populate_kenyan_products --business-id 1
```

### Clear existing and repopulate:
```bash
python manage.py populate_kenyan_products --clear-existing
```

## Categories & Products Included

### 1. Food & Beverages (23 products)
- Popular soft drinks (Coca Cola, Fanta, Sprite, Pepsi)
- Water brands (Dasani, Keringet)
- Local beverages and juices
- Snacks and confectionery (chips, chocolates, gums)
- Basic food staples (maize flour, rice, sugar, cooking oil)

### 2. Personal Care & Hygiene (15 products)
- Soap brands (Geisha, Lido, Dettol, Imperial Leather)
- Body care products (Vaseline, Nivea)
- Oral care (Colgate, Aquafresh, toothbrushes)
- Hair care products (Sunsilk, Pantene, hair treatments)
- Feminine hygiene products

### 3. Household Items (11 products)
- Cleaning products (OMO, Surf Excel, Sunlight, Vim, Jik)
- Paper products (toilet paper, tissues)
- Kitchen essentials (matchbox, candles, foil)

### 4. Stationery & Office (10 products)
- Writing materials (Bic pens, pencils, erasers)
- Paper products (exercise books, A4 paper)
- Office supplies (stapler, staples, rulers)

### 5. Electronics & Accessories (10 products)
- Mobile phone accessories (chargers, earphones, cases)
- Electronic items (memory cards, power banks, flashlights)
- Batteries (AA, AAA)

### 6. Pharmaceuticals & Health (8 products)
- Over-the-counter medications (Panadol, Aspirin, Ibuprofen)
- First aid supplies (Band-Aid, cotton wool, antiseptic)
- Vitamins and supplements

### 7. Clothing & Fashion (9 products)
- Basic clothing items (t-shirts, jeans, school uniforms)
- Accessories (belts, caps, socks, underwear)

### 8. Agricultural Products (7 products)
- Seeds (maize, beans, vegetables)
- Fertilizers (DAP, Urea)
- Basic farming tools

## Features

### Realistic Kenyan Pricing
- All prices are set in Kenyan Shilling (KSh) values
- Purchase and selling prices reflect current market rates
- Includes proper profit margins for retail businesses

### Stock Management
- Random stock quantities (10-100 units) assigned to each product
- Appropriate units assigned (pieces, kg, liters, boxes)

### Business-Specific
- Products are created for each business separately
- Prevents conflicts between different businesses
- Categories are business-specific

### Smart Duplication Prevention
- Checks for existing products before creating new ones
- Won't create duplicate products in the same business

## Command Options

| Option | Description |
|--------|-------------|
| `--business-id ID` | Populate products for a specific business only |
| `--clear-existing` | Remove all existing categories and products before populating |
| `--help` | Show help message and command options |

## Examples

```bash
# Populate all businesses with default products
python manage.py populate_kenyan_products

# Populate only business with ID 2
python manage.py populate_kenyan_products --business-id 2

# Clear existing data and repopulate all businesses
python manage.py populate_kenyan_products --clear-existing

# Clear and populate specific business
python manage.py populate_kenyan_products --business-id 1 --clear-existing
```

## Total Products: 93 products across 8 categories

This command provides a comprehensive starting point for any Kenyan retail business, covering the most common products found in:
- General stores/Duka
- Supermarkets
- Pharmacies  
- Stationery shops
- Electronics stores
- Agricultural supply stores

All products include realistic Kenyan market pricing and are categorized appropriately for easy management in the POS system.