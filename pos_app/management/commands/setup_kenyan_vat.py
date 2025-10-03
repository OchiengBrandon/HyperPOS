from django.core.management.base import BaseCommand
from pos_app.models import Business, VATCategory

class Command(BaseCommand):
    help = 'Setup default VAT categories for Kenyan businesses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--business-id',
            type=int,
            help='Business ID to setup VAT for (optional, will setup for all if not provided)'
        )

    def handle(self, *args, **options):
        business_id = options.get('business_id')
        
        if business_id:
            try:
                businesses = [Business.objects.get(id=business_id)]
            except Business.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Business with ID {business_id} does not exist')
                )
                return
        else:
            businesses = Business.objects.all()

        # Kenyan VAT categories based on KRA guidelines
        vat_categories = [
            {
                'name': 'Standard Rated Items',
                'code': 'STD',
                'vat_type': 'standard',
                'rate': 16.00,
                'description': 'Standard VAT rate of 16% applies to most goods and services'
            },
            {
                'name': 'Zero Rated Items',
                'code': 'ZERO',
                'vat_type': 'zero',
                'rate': 0.00,
                'description': 'Zero-rated items like basic food items, medical supplies, books, etc.'
            },
            {
                'name': 'Exempt Items',
                'code': 'EXP',
                'vat_type': 'exempt',
                'rate': 0.00,
                'description': 'VAT exempt items like financial services, insurance, education, etc.'
            },
            {
                'name': 'Basic Food Items',
                'code': 'FOOD',
                'vat_type': 'zero',
                'rate': 0.00,
                'description': 'Basic food items (maize flour, wheat flour, rice, sugar, cooking oil, etc.)'
            },
            {
                'name': 'Medical Supplies',
                'code': 'MED',
                'vat_type': 'zero',
                'rate': 0.00,
                'description': 'Medical supplies and pharmaceutical products'
            },
            {
                'name': 'Educational Materials',
                'code': 'EDU',
                'vat_type': 'zero',
                'rate': 0.00,
                'description': 'Books, newspapers, educational materials'
            },
            {
                'name': 'Agricultural Inputs',
                'code': 'AGR',
                'vat_type': 'zero',
                'rate': 0.00,
                'description': 'Agricultural inputs like fertilizers, seeds, pesticides'
            }
        ]

        for business in businesses:
            self.stdout.write(f'Setting up VAT categories for {business.name}...')
            
            created_count = 0
            for cat_data in vat_categories:
                vat_cat, created = VATCategory.objects.get_or_create(
                    business=business,
                    code=cat_data['code'],
                    defaults={
                        'name': cat_data['name'],
                        'vat_type': cat_data['vat_type'],
                        'rate': cat_data['rate'],
                        'description': cat_data['description']
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  Created: {vat_cat.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  Already exists: {vat_cat.name}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} VAT categories for {business.name}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS('VAT setup completed!')
        )