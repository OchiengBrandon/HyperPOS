"""
Django management command to populate VAT categories for existing products.
This command assigns appropriate Kenyan VAT categories (A, B, E) to products based on their type.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from pos_app.models import Business, Product, VATCategory
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate VAT categories for existing products based on Kenyan VAT rules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--business-id',
            type=int,
            help='Update products for a specific business ID only'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually making changes'
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Update VAT categories even for products that already have one assigned'
        )

    def handle(self, *args, **options):
        # Get businesses to update
        if options['business_id']:
            try:
                businesses = [Business.objects.get(id=options['business_id'])]
                self.stdout.write(f"Target business: {businesses[0].name}")
            except Business.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Business with ID {options['business_id']} does not exist")
                )
                return
        else:
            businesses = Business.objects.all()
            if not businesses.exists():
                self.stdout.write(
                    self.style.ERROR("No businesses found. Please create at least one business first.")
                )
                return
            self.stdout.write(f"Target businesses: {businesses.count()} business(es)")

        # Kenyan VAT category mapping based on product names/categories
        vat_rules = {
            # Standard Rated (A) - 16% VAT - Most goods and services
            'A': {
                'keywords': [
                    'cocacola', 'coca cola', 'pepsi', 'fanta', 'sprite', 'mountain dew',
                    'chocolate', 'biscuits', 'cookies', 'cake', 'candy', 'sweets',
                    'chips', 'crisps', 'pringles', 'doritos', 'snacks',
                    'soap', 'detergent', 'toothpaste', 'shampoo', 'lotion', 'cream',
                    'phone', 'electronics', 'battery', 'charger', 'headphones',
                    'clothing', 'shoes', 'bag', 'watch', 'jewelry',
                    'alcohol', 'beer', 'wine', 'spirits', 'cigarettes',
                    'furniture', 'appliance', 'tv', 'radio', 'fan'
                ],
                'categories': ['drinks', 'snacks', 'confectionery', 'household items', 'electronics']
            },
            # Zero Rated (B) - 0% VAT - Essential goods
            'B': {
                'keywords': [
                    'maize', 'rice', 'wheat', 'flour', 'sugar', 'salt',
                    'beans', 'peas', 'lentils', 'potatoes', 'onions', 'tomatoes',
                    'milk', 'bread', 'eggs', 'cooking oil', 'vegetable oil',
                    'tea', 'coffee', 'water', 'juice', 'fresh fruit',
                    'meat', 'beef', 'chicken', 'fish', 'pork', 'mutton',
                    'medicine', 'drugs', 'pharmaceutical', 'medical',
                    'fertilizer', 'seeds', 'agricultural', 'farming'
                ],
                'categories': ['groceries', 'fresh produce', 'staples', 'medical', 'agricultural']
            },
            # Exempt (E) - VAT Exempt
            'E': {
                'keywords': [
                    'education', 'school', 'books', 'stationery', 'pencils',
                    'insurance', 'banking', 'financial services',
                    'transport', 'matatu', 'taxi', 'bus fare',
                    'rent', 'accommodation', 'hotel', 'lodge'
                ],
                'categories': ['education', 'financial', 'transport', 'accommodation']
            }
        }

        total_updated = 0
        
        for business in businesses:
            self.stdout.write(f"\n{'-' * 50}")
            self.stdout.write(f"Processing business: {business.name}")
            self.stdout.write(f"{'-' * 50}")
            
            # Get VAT categories for this business
            try:
                vat_a = VATCategory.objects.get(business=business, code='A')
                vat_b = VATCategory.objects.get(business=business, code='B')
                vat_e = VATCategory.objects.get(business=business, code='E')
            except VATCategory.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"VAT categories not found for {business.name}. "
                        f"Please run 'python manage.py setup_basic_kenyan_vat' first."
                    )
                )
                continue
            
            # Get products to update
            products_query = Product.objects.filter(business=business, is_active=True)
            if not options['force_update']:
                products_query = products_query.filter(vat_category__isnull=True)
            
            products = products_query.select_related('category')
            
            if not products.exists():
                self.stdout.write("  No products to update")
                continue
            
            self.stdout.write(f"  Found {products.count()} products to process")
            
            business_updated = 0
            vat_stats = {'A': 0, 'B': 0, 'E': 0}
            
            with transaction.atomic():
                for product in products:
                    assigned_vat = self.determine_vat_category(product, vat_rules)
                    
                    if assigned_vat == 'A':
                        new_vat_category = vat_a
                    elif assigned_vat == 'B':
                        new_vat_category = vat_b
                    else:  # Default to 'E' for unknown products
                        new_vat_category = vat_e
                        assigned_vat = 'E'
                    
                    if options['dry_run']:
                        self.stdout.write(
                            f"    [DRY RUN] {product.name} → VAT {assigned_vat} ({new_vat_category.rate}%)"
                        )
                    else:
                        product.vat_category = new_vat_category
                        product.save()
                        self.stdout.write(
                            f"    ✓ {product.name} → VAT {assigned_vat} ({new_vat_category.rate}%)"
                        )
                    
                    business_updated += 1
                    vat_stats[assigned_vat] += 1
            
            if not options['dry_run']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Updated {business_updated} products: "
                        f"VAT A: {vat_stats['A']}, VAT B: {vat_stats['B']}, VAT E: {vat_stats['E']}"
                    )
                )
            
            total_updated += business_updated

        # Final summary
        action_word = "Would update" if options['dry_run'] else "Updated"
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(
            self.style.SUCCESS(f"SUCCESS: {action_word} {total_updated} products with VAT categories")
        )
        self.stdout.write(f"{'=' * 60}")

    def determine_vat_category(self, product, vat_rules):
        """Determine the appropriate VAT category for a product"""
        product_name_lower = product.name.lower()
        category_name_lower = product.category.name.lower() if product.category else ""
        
        # Check for Zero Rated (B) first - essential goods
        for keyword in vat_rules['B']['keywords']:
            if keyword.lower() in product_name_lower:
                return 'B'
        for category in vat_rules['B']['categories']:
            if category.lower() in category_name_lower:
                return 'B'
        
        # Check for Exempt (E) - educational, financial services etc
        for keyword in vat_rules['E']['keywords']:
            if keyword.lower() in product_name_lower:
                return 'E'
        for category in vat_rules['E']['categories']:
            if category.lower() in category_name_lower:
                return 'E'
        
        # Check for Standard Rated (A) - most commercial goods
        for keyword in vat_rules['A']['keywords']:
            if keyword.lower() in product_name_lower:
                return 'A'
        for category in vat_rules['A']['categories']:
            if category.lower() in category_name_lower:
                return 'A'
        
        # Default to Standard Rated (A) for commercial products
        # Most products in a retail business are standard rated
        return 'A'