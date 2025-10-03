from django.core.management.base import BaseCommand
from pos_app.models import VATCategory, Business
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up basic Kenyan VAT categories (A, B, E only)'

    def handle(self, *args, **options):
        # Get all businesses
        businesses = Business.objects.all()
        
        if not businesses.exists():
            self.stdout.write(
                self.style.ERROR('No businesses found. Please create a business first.')
            )
            return

        for business in businesses:
            self.stdout.write(f'Setting up VAT categories for business: {business.name}')
            
            # Clear existing VAT categories for this business
            existing_count = VATCategory.objects.filter(business=business).count()
            VATCategory.objects.filter(business=business).delete()
            self.stdout.write(f'  - Removed {existing_count} existing VAT categories')
            
            # Create the 3 basic Kenyan VAT categories
            vat_categories = [
                {
                    'name': 'Standard Rated (A)',
                    'code': 'A',
                    'rate': Decimal('16.00'),
                    'description': 'Standard VAT rate for most goods and services',
                    'vat_type': 'standard'
                },
                {
                    'name': 'Zero Rated (B)',
                    'code': 'B', 
                    'rate': Decimal('0.00'),
                    'description': 'Essential goods with 0% VAT rate',
                    'vat_type': 'zero'
                },
                {
                    'name': 'Exempt (E)',
                    'code': 'E',
                    'rate': Decimal('0.00'),
                    'description': 'VAT exempt goods and services',
                    'vat_type': 'exempt'
                }
            ]
            
            created_categories = []
            for cat_data in vat_categories:
                category = VATCategory.objects.create(
                    business=business,
                    name=cat_data['name'],
                    code=cat_data['code'],
                    rate=cat_data['rate'],
                    description=cat_data['description'],
                    vat_type=cat_data['vat_type'],
                    is_active=True
                )
                created_categories.append(category)
                self.stdout.write(f'  ✓ Created: {category.name} (Code: {category.code}, Rate: {category.rate}%)')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully set up {len(created_categories)} VAT categories for {business.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('VAT category setup completed!')
        )