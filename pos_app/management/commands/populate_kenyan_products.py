"""
Enhanced Django management command to populate comprehensive Kenyan categories and products.
This command creates hundreds of popular products commonly found in Kenyan businesses.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from pos_app.models import Business, Category, Product
from .data.drinks import DRINKS_PRODUCTS
from .data.snacks_confectionery import SNACKS_CONFECTIONERY_PRODUCTS
from .data.household_items import HOUSEHOLD_ITEMS_PRODUCTS
from .data.groceries import GROCERIES_PRODUCTS
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Populate comprehensive Kenyan categories and products for all businesses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--business-id',
            type=int,
            help='Populate products for a specific business ID only'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing categories and products before populating'
        )
        parser.add_argument(
            '--categories',
            nargs='+',
            choices=['drinks', 'snacks', 'household', 'groceries', 'all'],
            default=['all'],
            help='Specify which categories to populate'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating anything'
        )

    def handle(self, *args, **options):
        # Get businesses to populate
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

        # Determine which categories to populate
        categories_to_populate = options['categories']
        if 'all' in categories_to_populate:
            categories_to_populate = ['drinks', 'snacks', 'household', 'groceries']

        # Get product data
        all_product_data = self.get_all_product_data(categories_to_populate)
        
        if options['dry_run']:
            self.show_dry_run_summary(all_product_data, businesses)
            return

        # Clear existing data if requested
        if options['clear_existing']:
            for business in businesses:
                business.categories.all().delete()  # This will cascade delete products
            self.stdout.write(self.style.WARNING("Cleared existing categories and products"))

        # Populate data
        with transaction.atomic():
            total_categories = 0
            total_products = 0

            for business in businesses:
                self.stdout.write(f"\n{'-' * 50}")
                self.stdout.write(f"Populating products for: {business.name}")
                self.stdout.write(f"{'-' * 50}")
                
                business_categories = 0
                business_products = 0
                
                for category_name, products_list in all_product_data.items():
                    # Create or get category
                    category, created = Category.objects.get_or_create(
                        name=category_name,
                        business=business,
                        defaults={'description': f'{category_name} items popular in Kenya'}
                    )
                    
                    if created:
                        business_categories += 1
                        self.stdout.write(f"  ✓ Created category: {category_name}")
                    
                    # Create products
                    category_product_count = 0
                    for product_data in products_list:
                        # Check if product already exists
                        if not Product.objects.filter(
                            name=product_data['name'],
                            business=business
                        ).exists():
                            Product.objects.create(
                                name=product_data['name'],
                                description=product_data.get('description', ''),
                                sku=product_data.get('sku', ''),
                                category=category,
                                purchase_price=Decimal(str(product_data['purchase_price'])),
                                selling_price=Decimal(str(product_data['selling_price'])),
                                stock_quantity=random.randint(10, 100),
                                unit=product_data.get('unit', 'pcs'),
                                image=product_data.get('image', ''),
                                business=business,
                                is_active=True
                            )
                            business_products += 1
                            category_product_count += 1
                    
                    if category_product_count > 0:
                        self.stdout.write(f"    → Added {category_product_count} products")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Business Summary: {business_categories} categories, {business_products} products"
                    )
                )
                
                total_categories += business_categories
                total_products += business_products

        # Final summary
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(
            self.style.SUCCESS(
                f"SUCCESS: Created {total_categories} categories and {total_products} products"
            )
        )
        self.stdout.write(f"{'=' * 60}")

    def get_all_product_data(self, categories_to_populate):
        """Get product data based on selected categories"""
        product_data = {}
        
        if 'drinks' in categories_to_populate:
            product_data['Drinks & Beverages'] = DRINKS_PRODUCTS
            
        if 'snacks' in categories_to_populate:
            product_data['Snacks & Confectionery'] = SNACKS_CONFECTIONERY_PRODUCTS
            
        if 'household' in categories_to_populate:
            product_data['Household Items'] = HOUSEHOLD_ITEMS_PRODUCTS
            
        if 'groceries' in categories_to_populate:
            product_data['Groceries & Food'] = GROCERIES_PRODUCTS
            
        return product_data

    def show_dry_run_summary(self, product_data, businesses):
        """Show what would be created without actually creating anything"""
        self.stdout.write(self.style.WARNING("DRY RUN - No data will be created"))
        self.stdout.write(f"{'=' * 60}")
        
        total_products = 0
        for category_name, products_list in product_data.items():
            product_count = len(products_list)
            total_products += product_count
            self.stdout.write(f"Category: {category_name} → {product_count} products")
            
            # Show first 5 products as examples
            for i, product in enumerate(products_list[:5]):
                price_range = f"KSh {product['purchase_price']:.0f} - KSh {product['selling_price']:.0f}"
                self.stdout.write(f"  • {product['name']} ({price_range})")
            
            if len(products_list) > 5:
                self.stdout.write(f"  ... and {len(products_list) - 5} more products")
            self.stdout.write("")
        
        self.stdout.write(f"Total: {len(product_data)} categories, {total_products} products")
        self.stdout.write(f"Would be applied to: {businesses.count()} business(es)")
        self.stdout.write(f"{'=' * 60}")
        self.stdout.write("Run without --dry-run to actually create the products")