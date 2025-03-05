# pos_app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.core.validators import MinValueValidator

from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

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
    
    def __str__(self):
        return f"Settings for {self.business.name}"

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



class Product(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('ltr', 'Liters'),
        ('box', 'Boxes'),
        # Add more units as needed
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')  # New unit field
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

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    loyalty_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

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

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sale_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
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