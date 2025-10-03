# pos_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Business, BusinessSettings, Category, Product, Customer, 
    Employee, Sale, SaleItem, Inventory, Supplier, Purchase, 
    PurchaseItem, Expense
)

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')



class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            'name',
            'business_type',
            'address',
            'phone',
            'email',
            'website',
            'logo',
            'tax_rate',
            'currency_symbol',
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency_symbol': forms.Select(attrs={'class': 'form-select'}),
        }
        
        labels = {
            'name': 'Business Name',
            'business_type': 'Business Type',
            'address': 'Business Address',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'website': 'Website URL',
            'logo': 'Business Logo',
            'tax_rate': 'Tax Rate (%)',
            'currency_symbol': 'Currency Symbol',
        }

        help_texts = {
            'logo': 'Upload a square logo for best results. Maximum size: 2MB.',
            'tax_rate': 'Enter the tax rate as a percentage.',
        }

        error_messages = {
            'name': {
                'max_length': "This name is too long.",
            },
            'email': {
                'invalid': "Enter a valid email address.",
            },
            'tax_rate': {
                'invalid': "Enter a valid tax rate.",
            },
        }

class BusinessSettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessSettings
        fields = ('theme_color', 'receipt_header', 'receipt_footer', 
                 'enable_low_stock_alerts', 'low_stock_threshold',
                 'enable_customer_loyalty', 'points_per_purchase', 'points_value',
                 'enable_vat', 'vat_inclusive_pricing', 'default_vat_category', 
                 'kra_pin', 'vat_number', 'show_vat_on_receipt', 'vat_rounding')
        widgets = {
            'receipt_header': forms.Textarea(attrs={'rows': 3}),
            'receipt_footer': forms.Textarea(attrs={'rows': 3}),
            'theme_color': forms.TextInput(attrs={'type': 'color'}),
            'kra_pin': forms.TextInput(attrs={'placeholder': 'P051234567X'}),
            'vat_number': forms.TextInput(attrs={'placeholder': 'VAT-123456789'}),
        }
        
        labels = {
            'enable_vat': 'Enable VAT System',
            'vat_inclusive_pricing': 'Prices Include VAT',
            'default_vat_category': 'Default VAT Category',
            'kra_pin': 'KRA PIN',
            'vat_number': 'VAT Registration Number',
            'show_vat_on_receipt': 'Show VAT on Receipts',
            'vat_rounding': 'VAT Rounding Method',
        }
    
    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if business:
            from .models import VATCategory
            self.fields['default_vat_category'].queryset = VATCategory.objects.filter(business=business)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            'name', 
            'description', 
            'sku', 
            'barcode', 
            'category',
            'vat_category', 
            'purchase_price', 
            'selling_price', 
            'stock_quantity', 
            'unit',  # Include the unit field
            'image', 
            'is_active'
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'purchase_price': forms.NumberInput(attrs={'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'min': '0'}),
            'vat_category': forms.Select(attrs={'class': 'form-select'}),
        }
        
        labels = {
            'vat_category': 'VAT Category',
        }
    
    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if business:
            self.fields['category'].queryset = Category.objects.filter(business=business)
            # Filter VAT categories by business
            from .models import VATCategory
            self.fields['vat_category'].queryset = VATCategory.objects.filter(business=business)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = (
            'first_name', 'last_name', 'email', 'phone', 'address', 
            'credit_limit', 'current_debt'
        )
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'credit_limit': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'current_debt': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'readonly': True}),
        }
        
        labels = {
            'credit_limit': 'Credit Limit',
            'current_debt': 'Current Debt (Read Only)',
        }
        
        help_texts = {
            'credit_limit': 'Maximum amount this customer can owe',
            'current_debt': 'Current outstanding debt (automatically calculated)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make current_debt field readonly and not required for new customers
        self.fields['current_debt'].required = False
        if not self.instance.pk:  # New customer
            self.fields['current_debt'].initial = 0

class EmployeeForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = Employee
        fields = ('role', 'phone', 'address', 'is_active')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['first_name'].initial = instance.user.first_name
            self.fields['last_name'].initial = instance.user.last_name
            self.fields['email'].initial = instance.user.email
            self.fields['username'].initial = instance.user.username
            self.fields['username'].widget.attrs['readonly'] = True

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ('customer', 'payment_method', 'payment_reference', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if business:
            self.fields['customer'].queryset = Customer.objects.filter(business=business)

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ('product', 'quantity', 'unit_price')
    
    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if business:
            self.fields['product'].queryset = Product.objects.filter(business=business, is_active=True)

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ('product', 'transaction_type', 'quantity', 'reference', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if business:
            self.fields['product'].queryset = Product.objects.filter(business=business)

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ('name', 'contact_person', 'email', 'phone', 'address')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ('supplier', 'reference_number', 'status', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if business:
            self.fields['supplier'].queryset = Supplier.objects.filter(business=business)

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ('product', 'quantity', 'unit_price', 'received_quantity')
    
    def __init__(self, *args, **kwargs):
        business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if business:
            self.fields['product'].queryset = Product.objects.filter(business=business)

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ('category', 'amount', 'description', 'date', 'receipt')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }