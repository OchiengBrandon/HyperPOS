# pos_app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.core.validators import MinValueValidator

class Business(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('Type1', 'Type 1'),
        ('Type2', 'Type 2'),
        # Add more types as necessary
    ]

    CURRENCY_SYMBOL_CHOICES = [
        ('$', '$ - US Dollar'),
        ('€', '€ - Euro'),
        ('£', '£ - British Pound'),
        ('¥', '¥ - Japanese Yen'),
        ('₹', '₹ - Indian Rupee'),
        ('₩', '₩ - South Korean Won'),
        ('KSh', 'KSh - Kenyan Shilling'),  # Added Kenyan Shilling
        # Add more currency symbols as necessary
    ]

    name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPE_CHOICES, default='Type1')
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    currency_symbol = models.CharField(max_length=5, choices=CURRENCY_SYMBOL_CHOICES, default='$')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_businesses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class BusinessSettings(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='settings')
    theme_color = models.CharField(max_length=20, default='#3498db')
    receipt_header = models.TextField(blank=True, null=True)
    receipt_footer = models.TextField(blank=True, null=True)
    enable_low_stock_alerts = models.BooleanField(default=True)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    enable_customer_loyalty = models.BooleanField(default=False)
    points_per_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    points_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.01)  # Value of 1 point in currency
    
    # VAT Settings
    enable_vat = models.BooleanField(default=True)
    vat_inclusive_pricing = models.BooleanField(default=True)  # Prices include VAT by default
    default_vat_category = models.ForeignKey('VATCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_for_businesses')
    kra_pin = models.CharField(max_length=20, blank=True, null=True, help_text="KRA PIN for VAT compliance")
    vat_number = models.CharField(max_length=50, blank=True, null=True, help_text="VAT registration number")
    show_vat_on_receipt = models.BooleanField(default=True)
    vat_rounding = models.CharField(max_length=10, choices=[('round', 'Round'), ('floor', 'Floor'), ('ceil', 'Ceiling')], default='round')
    
    def __str__(self):
        return f"Settings for {self.business.name}"

class VATCategory(models.Model):
    """
    VAT Categories based on Kenyan VAT system
    """
    VAT_TYPE_CHOICES = [
        ('standard', 'Standard Rate (16%)'),
        ('zero', 'Zero Rate (0%)'),
        ('exempt', 'Exempt from VAT'),
        ('reduced', 'Reduced Rate'),
    ]
    
    name = models.CharField(max_length=100)  # e.g., "Food Items", "Electronics", "Services"
    code = models.CharField(max_length=10, unique=True)  # e.g., "STD", "ZERO", "EXP"
    vat_type = models.CharField(max_length=20, choices=VAT_TYPE_CHOICES, default='standard')
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=16.00)  # VAT rate percentage
    description = models.TextField(blank=True, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='vat_categories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "VAT Categories"
        unique_together = ('business', 'code')
        
    def __str__(self):
        return f"{self.name} ({self.rate}%)"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

from django.core.validators import MinValueValidator
from django.db import models

class Product(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('ltr', 'Liters'),
        ('box', 'Boxes'),
        ('m', 'Meters'),
        ('pack', 'Packs'),
        ('bottle', 'Bottles'),
        # Add more units as needed
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)  # Enhanced barcode field
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    vat_category = models.ForeignKey(VATCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')  # New VAT category
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def profit_margin(self):
        if self.purchase_price > 0:
            return ((self.selling_price - self.purchase_price) / self.selling_price) * 100
        return 0
    
    @property
    def vat_rate(self):
        """Get the VAT rate for this product"""
        if self.vat_category:
            return self.vat_category.rate
        return 0
    
    def calculate_vat_amount(self, price=None):
        """Calculate VAT amount for given price (defaults to selling price)"""
        if price is None:
            price = self.selling_price
        
        if self.vat_category and self.vat_category.vat_type != 'exempt':
            return (price * self.vat_rate) / 100
        return 0
    
    def calculate_price_excluding_vat(self, price=None):
        """Calculate price excluding VAT"""
        if price is None:
            price = self.selling_price
        
        if self.vat_category and self.vat_category.vat_type != 'exempt':
            return price / (1 + (self.vat_rate / 100))
        return price
    
    def calculate_price_including_vat(self, price=None):
        """Calculate price including VAT"""
        if price is None:
            price = self.selling_price
        
        if self.vat_category and self.vat_category.vat_type != 'exempt':
            return price + self.calculate_vat_amount(price)
        return price

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    loyalty_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Maximum credit allowed for this customer")
    current_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Current outstanding debt")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def available_credit(self):
        """Calculate available credit for the customer"""
        return self.credit_limit - self.current_debt
    
    @property
    def debt_percentage(self):
        """Calculate debt as percentage of credit limit"""
        if self.credit_limit > 0:
            return (self.current_debt / self.credit_limit) * 100
        return 0
    
    def can_make_credit_purchase(self, amount):
        """Check if customer can make a credit purchase of given amount"""
        return (self.current_debt + amount) <= self.credit_limit

class Employee(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('inventory', 'Inventory Manager'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='employees')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_payment', 'Mobile Payment'),
        ('loyalty_points', 'Loyalty Points'),
        ('credit', 'Credit Customer'),
        ('mixed', 'Mixed Payment'),
    ]
    
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='sales')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='sales')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)  # For card/transfer references
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True, null=True)
    loyalty_points_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loyalty_points_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.invoice_number
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def subtotal_excluding_vat(self):
        """Calculate subtotal excluding VAT"""
        total = 0
        for item in self.items.all():
            total += item.total_excluding_vat
        return total
    
    @property
    def total_vat_amount(self):
        """Calculate total VAT amount"""
        total = 0
        for item in self.items.all():
            total += item.total_vat_amount
        return total
    
    @property
    def vat_breakdown(self):
        """Get VAT breakdown by category"""
        from collections import defaultdict
        vat_summary = defaultdict(lambda: {'amount': 0, 'rate': 0, 'category_name': ''})
        
        for item in self.items.all():
            if item.product.vat_category and item.total_vat_amount > 0:
                vat_cat = item.product.vat_category
                key = f"{vat_cat.code}_{vat_cat.rate}"
                vat_summary[key]['amount'] += item.total_vat_amount
                vat_summary[key]['rate'] = vat_cat.rate
                vat_summary[key]['category_name'] = vat_cat.name
        
        return [value for value in vat_summary.values() if value['amount'] > 0]
    
    def process_credit_sale(self):
        """Process a credit sale - update customer debt"""
        if self.payment_method == 'credit' and self.customer and self.status == 'completed':
            self.customer.current_debt += self.total_amount
            self.customer.save()
    
    @property
    def is_credit_sale(self):
        """Check if this is a credit sale"""
        return self.payment_method == 'credit'

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sale_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # New VAT amount field
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def price_excluding_vat(self):
        """Calculate price excluding VAT"""
        return self.product.calculate_price_excluding_vat(self.unit_price)
    
    @property
    def total_excluding_vat(self):
        """Calculate total excluding VAT"""
        return self.price_excluding_vat * self.quantity
    
    @property
    def total_vat_amount(self):
        """Calculate total VAT amount for this line item"""
        return self.vat_amount * self.quantity
    
    def save(self, *args, **kwargs):
        # Calculate subtotal
        self.subtotal = self.quantity * self.unit_price
        
        # Calculate VAT amount per unit
        if self.product and self.product.vat_category:
            self.vat_amount = self.product.calculate_vat_amount(self.unit_price)
        else:
            self.vat_amount = 0
        
        super().save(*args, **kwargs)

class Inventory(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('damaged', 'Damaged/Lost'),
        ('transfer', 'Transfer'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_records')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()  # Can be negative for sales, damaged, etc.
    reference = models.CharField(max_length=100, blank=True, null=True)  # Order number, invoice, etc.
    notes = models.TextField(blank=True, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='inventory_records')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='inventory_records')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Inventory Records"
    
    def __str__(self):
        return f"{self.product.name} - {self.transaction_type} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Update product stock quantity
        is_new = self.pk is None
        if is_new:  # Only update stock on new records to prevent double-counting on updates
            self.product.stock_quantity += self.quantity
            self.product.save()
        super().save(*args, **kwargs)

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='suppliers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('partially_received', 'Partially Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    reference_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='purchases')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"PO-{self.reference_number}"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    received_quantity = models.PositiveIntegerField(default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('salaries', 'Salaries'),
        ('supplies', 'Supplies'),
        ('maintenance', 'Maintenance'),
        ('marketing', 'Marketing'),
        ('insurance', 'Insurance'),
        ('taxes', 'Taxes'),
        ('other', 'Other'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    receipt = models.FileField(upload_to='expense_receipts/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.amount}"


# Credit Note Model for handling refunds and returns
class CreditNote(models.Model):
    CREDIT_TYPE_CHOICES = [
        ('refund', 'Refund'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('discount', 'Discount'),
    ]
    
    credit_note_number = models.CharField(max_length=50, unique=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='credit_notes')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_notes')
    original_sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_notes')
    credit_type = models.CharField(max_length=20, choices=CREDIT_TYPE_CHOICES, default='refund')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    is_applied = models.BooleanField(default=False, help_text="Whether credit has been applied to customer account")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_notes_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.credit_note_number:
            import uuid
            self.credit_note_number = f"CN-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Credit Note {self.credit_note_number} - {self.total_amount}"


# Debt Payment Model for tracking customer payments
class DebtPayment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Cash Payment'),
        ('card', 'Card Payment'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_payment', 'Mobile Payment'),
        ('credit_note', 'Credit Note Applied'),
    ]
    
    payment_reference = models.CharField(max_length=50, unique=True)
    # Link to sale when a debt payment is related to a specific sale
    sale = models.ForeignKey('Sale', on_delete=models.SET_NULL, null=True, blank=True, related_name='debt_payments')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='debt_payments')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='debt_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='cash')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debt_payments_recorded')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.payment_reference:
            import uuid
            self.payment_reference = f"DP-{uuid.uuid4().hex[:8].upper()}"
        
        # Update customer debt when payment is saved
        if self.pk is None:  # Only on creation
            self.customer.current_debt = max(0, self.customer.current_debt - self.amount)
            self.customer.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Payment {self.payment_reference} - {self.customer.full_name} - {self.amount}"