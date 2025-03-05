# pos_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, Q, Avg
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import json
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from .forms import (
    UserRegistrationForm, BusinessForm, BusinessSettingsForm, CategoryForm,
    ProductForm, CustomerForm, EmployeeForm, SaleForm, SaleItemForm,
    InventoryForm, SupplierForm, PurchaseForm, PurchaseItemForm, ExpenseForm
)
from .models import (
    Business, BusinessSettings, Category, Product, Customer,
    Employee, Sale, SaleItem, Inventory, Supplier, Purchase,
    PurchaseItem, Expense
)

# Helper functions
def get_business_for_user(user):
    """Get the business for the current user (owner or employee)"""
    try:
        # If user is a business owner
        return Business.objects.filter(owner=user).first()
    except:
        # If user is an employee
        try:
            employee = Employee.objects.filter(user=user, is_active=True).first()
            if employee:
                return employee.business
        except:
            pass
    return None

def get_user_role(user, business):
    """Get the role of the user in the business"""
    if business and business.owner == user:
        return 'owner'
    try:
        employee = Employee.objects.get(user=user, business=business, is_active=True)
        return employee.role
    except Employee.DoesNotExist:
        return None

# Authentication views
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('business_setup')
    else:
        form = UserRegistrationForm()
    return render(request, 'pos_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            business = get_business_for_user(user)
            if business:
                return redirect('dashboard')
            else:
                return redirect('business_setup')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'pos_app/login.html')

# Business setup

@login_required
def business_setup(request):
    # Check if the user already has a business
    existing_business = get_business_for_user(request.user)
    if existing_business:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            
            # Create default business settings
            BusinessSettings.objects.create(business=business)
            
            # Create default category
            Category.objects.create(
                name='General',
                description='Default category',
                business=business
            )
            
            messages.success(request, "Your business has been set up successfully!")
            return redirect('dashboard')
        else:
            # Log form errors for debugging
            print(form.errors)  # Optional: Remove in production
            
            messages.error(request, "There were errors in your form. Please correct them and try again.")
    else:
        form = BusinessForm()  # Create a new form instance
    
    return render(request, 'pos_app/business_setup.html', {'form': form})

# Dashboard
@login_required
def dashboard(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('login')
    
    # Get sales data for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    sales = Sale.objects.filter(
        business=business,
        created_at__gte=thirty_days_ago,
        status='completed'
    )
    
    # Daily sales data
    daily_sales = sales.annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('day')
    
    # Calculate total sales, average sale value, and product count
    total_sales = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    avg_sale = total_sales / sales.count() if sales.count() > 0 else 0
    product_count = Product.objects.filter(business=business).count()
    
    # Low stock products
    low_stock_threshold = business.settings.low_stock_threshold
    low_stock_products = Product.objects.filter(
        business=business,
        stock_quantity__lte=low_stock_threshold,
        is_active=True
    )[:5]
    
    # Recent sales
    recent_sales = sales.order_by('-created_at')[:5]
    
    # Top selling products
    top_products = SaleItem.objects.filter(
        sale__business=business,
        sale__created_at__gte=thirty_days_ago,
        sale__status='completed'
    ).values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum('subtotal')
    ).order_by('-total_quantity')[:5]
    
    context = {
        'business': business,
        'role': role,
        'total_sales': total_sales,
        'avg_sale': avg_sale,
        'product_count': product_count,
        'sales_count': sales.count(),
        'daily_sales': list(daily_sales),
        'low_stock_products': low_stock_products,
        'recent_sales': recent_sales,
        'top_products': top_products,
    }
    
    return render(request, 'pos_app/dashboard.html', context)

# POS (Point of Sale)
@login_required
def pos(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('login')
    
    # Get all categories and products
    categories = Category.objects.filter(business=business)
    products = Product.objects.filter(business=business, is_active=True)
    customers = Customer.objects.filter(business=business)
    
    context = {
        'business': business,
        'role': role,
        'categories': categories,
        'products': products,
        'customers': customers,
    }
    
    return render(request, 'pos_app/pos.html', context)

@login_required
@csrf_exempt
def process_sale(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    business = get_business_for_user(request.user)
    if not business:
        return JsonResponse({'error': 'No business found'}, status=404)
    
    try:
        data = json.loads(request.body)
        
        # Get or create customer
        customer = None
        if data.get('customer_id'):
            customer = Customer.objects.get(id=data['customer_id'], business=business)
        
        # Get employee
        employee = None
        try:
            employee = Employee.objects.get(user=request.user, business=business)
        except Employee.DoesNotExist:
            # If the user is the business owner, we'll proceed without an employee record
            if business.owner != request.user:
                return JsonResponse({'error': 'Employee not found'}, status=404)
        
        # Create sale
        sale = Sale(
            business=business,
            customer=customer,
            employee=employee,
            subtotal=data['subtotal'],
            tax_amount=data['tax_amount'],
            discount_amount=data['discount_amount'],
            total_amount=data['total_amount'],
            payment_method=data['payment_method'],
            payment_reference=data.get('payment_reference', ''),
            notes=data.get('notes', ''),
        )
        
        # Calculate loyalty points if enabled
        if business.settings.enable_customer_loyalty and customer:
            points_earned = data['total_amount'] * business.settings.points_per_purchase
            sale.loyalty_points_earned = points_earned
            sale.loyalty_points_used = data.get('loyalty_points_used', 0)
            
            # Update customer loyalty points
            customer.loyalty_points += points_earned - sale.loyalty_points_used
            customer.save()
        
        sale.save()
        
        # Create sale items
        for item_data in data['items']:
            product = Product.objects.get(id=item_data['product_id'], business=business)
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=quantity * unit_price
            )
            
            # Update inventory
            Inventory.objects.create(
                product=product,
                transaction_type='sale',
                quantity=-quantity,
                reference=sale.invoice_number,
                business=business,
                created_by=request.user
            )
        
        return JsonResponse({
            'success': True,
            'invoice_number': sale.invoice_number,
            'sale_id': sale.id
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_receipt(request, sale_id):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    sale = get_object_or_404(Sale, id=sale_id, business=business)
    items = sale.items.all()
    
    context = {
        'business': business,
        'sale': sale,
        'items': items,
    }
    
    return render(request, 'pos_app/receipt.html', context)

# Products
@login_required
def product_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('login')
    
    # Get all products with pagination
    products_list = Product.objects.filter(business=business).order_by('name')
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        products_list = products_list.filter(category_id=category_id)
    
    # Search by name or SKU if provided
    search_query = request.GET.get('search')
    if search_query:
        products_list = products_list.filter(
            models.Q(name__icontains=search_query) | 
            models.Q(sku__icontains=search_query) |
            models.Q(barcode__icontains=search_query)
        )
    
    paginator = Paginator(products_list, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Get all categories for filter dropdown
    categories = Category.objects.filter(business=business)
    
    context = {
        'business': business,
        'role': role,
        'products': products,
        'categories': categories,
        'category_id': category_id,
        'search_query': search_query,
    }
    
    return render(request, 'pos_app/products.html', context)

@login_required
def product_create(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to create products')
        return redirect('product_list')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, business=business)
        if form.is_valid():
            product = form.save(commit=False)
            product.business = business
            product.save()
            
            # Create initial inventory record
            if product.stock_quantity > 0:
                Inventory.objects.create(
                    product=product,
                    transaction_type='adjustment',
                    quantity=product.stock_quantity,
                    reference='Initial Stock',
                    business=business,
                    created_by=request.user
                )
            
            messages.success(request, f'Product "{product.name}" has been created')
            return redirect('product_list')
    else:
        form = ProductForm(business=business)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'title': 'Create Product',
    }
    
    return render(request, 'pos_app/product_form.html', context)

@login_required
def product_edit(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to edit products')
        return redirect('product_list')
    
    product = get_object_or_404(Product, pk=pk, business=business)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, business=business)
        if form.is_valid():
            old_stock = product.stock_quantity
            product = form.save()
            
            # Create inventory adjustment if stock was manually changed
            new_stock = product.stock_quantity
            if new_stock != old_stock:
                adjustment = new_stock - old_stock
                Inventory.objects.create(
                    product=product,
                    transaction_type='adjustment',
                    quantity=adjustment,
                    reference='Manual Adjustment',
                    business=business,
                    created_by=request.user
                )
            
            messages.success(request, f'Product "{product.name}" has been updated')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product, business=business)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'product': product,
        'title': 'Edit Product',
    }
    
    return render(request, 'pos_app/product_form.html', context)

@login_required
def product_delete(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete products')
        return redirect('product_list')
    
    product = get_object_or_404(Product, pk=pk, business=business)
    
    if request.method == 'POST':
        product_name = product.name
        product.is_active = False
        product.save()
        messages.success(request, f'Product "{product_name}" has been deactivated')
        return redirect('product_list')
    
    context = {
        'business': business,
        'role': role,
        'product': product,
    }
    
    return render(request, 'pos_app/product_confirm_delete.html', context)

# Categories
@login_required
def category_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('login')
    
    # Get all categories
    categories = Category.objects.filter(business=business).order_by('name')
    
    context = {
        'business': business,
        'role': role,
        'categories': categories,
    }
    
    return render(request, 'pos_app/categories.html', context)

@login_required
def category_create(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to create categories')
        return redirect('category_list')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.business = business
            category.save()
            messages.success(request, f'Category "{category.name}" has been created')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'title': 'Create Category',
    }
    
    return render(request, 'pos_app/category_form.html', context)

@login_required
def category_edit(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to edit categories')
        return redirect('category_list')
    
    category = get_object_or_404(Category, pk=pk, business=business)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" has been updated')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'category': category,
        'title': 'Edit Category',
    }
    
    return render(request, 'pos_app/category_form.html', context)

@login_required
def category_delete(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete categories')
        return redirect('category_list')
    
    category = get_object_or_404(Category, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if category has products
        if category.products.exists():
            messages.error(request, f'Cannot delete category "{category.name}" because it has products')
            return redirect('category_list')
        
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" has been deleted')
        return redirect('category_list')
    
    context = {
        'business': business,
        'role': role,
        'category': category,
    }
    
    return render(request, 'pos_app/category_confirm_delete.html', context)

# Customers
@login_required
def customer_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('login')
    
    # Get all customers with pagination
    customers_list = Customer.objects.filter(business=business).order_by('first_name', 'last_name')
    
    # Search by name, email or phone if provided
    search_query = request.GET.get('search')
    if search_query:
        customers_list = customers_list.filter(
            models.Q(first_name__icontains=search_query) | 
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(phone__icontains=search_query)
        )
    
    paginator = Paginator(customers_list, 10)  # Show 10 customers per page
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)
    
    context = {
        'business': business,
        'role': role,
        'customers': customers,
        'search_query': search_query,
    }
    
    return render(request, 'pos_app/customers.html', context)

@login_required
def customer_create(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'cashier']:
        messages.error(request, 'You do not have permission to create customers')
        return redirect('customer_list')
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.business = business
            customer.save()
            messages.success(request, f'Customer "{customer.full_name}" has been created')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'title': 'Create Customer',
    }
    
    return render(request, 'pos_app/customer_form.html', context)

@login_required
def customer_edit(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'cashier']:
        messages.error(request, 'You do not have permission to edit customers')
        return redirect('customer_list')
    
    customer = get_object_or_404(Customer, pk=pk, business=business)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.full_name}" has been updated')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'customer': customer,
        'title': 'Edit Customer',
    }
    
    return render(request, 'pos_app/customer_form.html', context)

@login_required
def customer_delete(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete customers')
        return redirect('customer_list')
    
    customer = get_object_or_404(Customer, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if customer has sales
        if customer.sales.exists():
            messages.error(request, f'Cannot delete customer "{customer.full_name}" because they have sales records')
            return redirect('customer_list')
        
        customer_name = customer.full_name
        customer.delete()
        messages.success(request, f'Customer "{customer_name}" has been deleted')
        return redirect('customer_list')
    
    context = {
        'business': business,
        'role': role,
        'customer': customer,
    }
    
    return render(request, 'pos_app/customer_confirm_delete.html', context)

# Employees
@login_required
def employee_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to view employees')
        return redirect('dashboard')
    
    # Get all employees
    employees = Employee.objects.filter(business=business).order_by('-is_active', 'user__first_name', 'user__last_name')
    
    context = {
        'business': business,
        'role': role,
        'employees': employees,
    }
    
    return render(request, 'pos_app/employees.html', context)

@login_required
def employee_create(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to create employees')
        return redirect('employee_list')
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            # Create user first
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            
            # Check if user already exists
            try:
                user = User.objects.get(username=username)
                messages.error(request, f'User with username "{username}" already exists')
                return render(request, 'pos_app/employee_form.html', {'form': form, 'business': business, 'role': role, 'title': 'Create Employee'})
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
            
            # Create employee
            employee = form.save(commit=False)
            employee.user = user
            employee.business = business
            employee.save()
            
            messages.success(request, f'Employee "{user.get_full_name()}" has been created')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'title': 'Create Employee',
    }
    
    return render(request, 'pos_app/employee_form.html', context)


@login_required
def employee_delete(request, employee_id):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')

    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete employees')
        return redirect('employee_list')

    # Get the employee object
    employee = get_object_or_404(Employee, id=employee_id, business=business)

    # Delete the employee
    employee.delete()
    messages.success(request, f'Employee "{employee.user.get_full_name()}" has been deleted')
    return redirect('employee_list')

@login_required
def employee_edit(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to edit employees')
        return redirect('employee_list')
    
    employee = get_object_or_404(Employee, pk=pk, business=business)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            # Update user
            user = employee.user
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            
            # Update password if provided
            password = form.cleaned_data['password']
            if password:
                user.set_password(password)
            
            user.save()
            
            # Update employee
            employee = form.save()
            
            messages.success(request, f'Employee "{user.get_full_name()}" has been updated')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'employee': employee,
        'title': 'Edit Employee',
    }
    
    return render(request, 'pos_app/employee_form.html', context)

@login_required
def employee_toggle_status(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to change employee status')
        return redirect('employee_list')
    
    employee = get_object_or_404(Employee, pk=pk, business=business)
    
    # Toggle active status
    employee.is_active = not employee.is_active
    employee.save()
    
    status = 'activated' if employee.is_active else 'deactivated'
    messages.success(request, f'Employee "{employee.user.get_full_name()}" has been {status}')
    return redirect('employee_list')

# Sales
@login_required
def sales_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('login')
    
    # Get all sales with pagination
    sales_list = Sale.objects.filter(business=business).order_by('-created_at')
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            sales_list = sales_list.filter(created_at__date__gte=start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            sales_list = sales_list.filter(created_at__date__lte=end_date)
        except ValueError:
            pass
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        sales_list = sales_list.filter(status=status)
    
    # Filter by payment method if provided
    payment_method = request.GET.get('payment_method')
    if payment_method:
        sales_list = sales_list.filter(payment_method=payment_method)
    
    # Search by invoice number or customer name if provided
    search_query = request.GET.get('search')
    if search_query:
        sales_list = sales_list.filter(
            models.Q(invoice_number__icontains=search_query) | 
            models.Q(customer__first_name__icontains=search_query) |
            models.Q(customer__last_name__icontains=search_query)
        )
    
    # Calculate totals
    totals = sales_list.aggregate(
        total_sales=Sum('total_amount'),
        total_tax=Sum('tax_amount'),
        total_discount=Sum('discount_amount')
    )
    
    paginator = Paginator(sales_list, 10)  # Show 10 sales per page
    page_number = request.GET.get('page')
    sales = paginator.get_page(page_number)
    
    context = {
        'business': business,
        'role': role,
        'sales': sales,
        'totals': totals,
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'payment_method': payment_method,
        'search_query': search_query,
    }
    
    return render(request, 'pos_app/sales.html', context)

@login_required
def sale_detail(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('login')
    
    sale = get_object_or_404(Sale, pk=pk, business=business)
    items = sale.items.all()
    
    context = {
        'business': business,
        'role': role,
        'sale': sale,
        'items': items,
    }
    
    return render(request, 'pos_app/sale_detail.html', context)

@login_required
def sale_void(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to void sales')
        return redirect('sales_list')
    
    sale = get_object_or_404(Sale, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if sale can be voided
        if sale.status != 'completed':
            messages.error(request, f'Sale {sale.invoice_number} cannot be voided because it is already {sale.get_status_display()}')
            return redirect('sale_detail', pk=sale.pk)
        
        # Void sale
        sale.status = 'cancelled'
        sale.save()
        
        # Return items to inventory
        for item in sale.items.all():
            Inventory.objects.create(
                product=item.product,
                transaction_type='return',
                quantity=item.quantity,
                reference=f'Void: {sale.invoice_number}',
                business=business,
                created_by=request.user
            )
        
        # Return loyalty points if used
        if sale.loyalty_points_used > 0 and sale.customer:
            sale.customer.loyalty_points += sale.loyalty_points_used
            sale.customer.save()
        
        messages.success(request, f'Sale {sale.invoice_number} has been voided')
        return redirect('sales_list')
    
    context = {
        'business': business,
        'role': role,
        'sale': sale,
    }
    
    return render(request, 'pos_app/sale_void.html', context)

@login_required
def sale_refund(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to refund sales')
        return redirect('sales_list')
    
    sale = get_object_or_404(Sale, pk=pk, business=business)
    items = sale.items.all()
    
    if request.method == 'POST':
        # Check if sale can be refunded
        if sale.status != 'completed':
            messages.error(request, f'Sale {sale.invoice_number} cannot be refunded because it is already {sale.get_status_display()}')
            return redirect('sale_detail', pk=sale.pk)
        
        # Process refund
        refund_type = request.POST.get('refund_type')
        
        if refund_type == 'full':
            # Full refund
            sale.status = 'refunded'
            sale.save()
            
            # Return all items to inventory
            for item in items:
                Inventory.objects.create(
                    product=item.product,
                    transaction_type='return',
                    quantity=item.quantity,
                    reference=f'Refund: {sale.invoice_number}',
                    business=business,
                    created_by=request.user
                )
            
            # Return loyalty points if used
            if sale.loyalty_points_used > 0 and sale.customer:
                sale.customer.loyalty_points += sale.loyalty_points_used
                sale.customer.save()
            
            messages.success(request, f'Sale {sale.invoice_number} has been fully refunded')
        
        elif refund_type == 'partial':
            # Partial refund
            refunded_items = []
            
            for item in items:
                refund_qty = int(request.POST.get(f'refund_qty_{item.id}', 0))
                if refund_qty > 0:
                    if refund_qty > item.quantity:
                        refund_qty = item.quantity
                    
                    refunded_items.append({
                        'item': item,
                        'refund_qty': refund_qty
                    })
            
            if refunded_items:
                # Update sale status
                sale.status = 'partially_refunded'
                sale.save()
                
                # Return items to inventory
                for refund_item in refunded_items:
                    Inventory.objects.create(
                        product=refund_item['item'].product,
                        transaction_type='return',
                        quantity=refund_item['refund_qty'],
                        reference=f'Partial Refund: {sale.invoice_number}',
                        business=business,
                        created_by=request.user
                    )
                
                messages.success(request, f'Sale {sale.invoice_number} has been partially refunded')
            else:
                messages.error(request, 'No items selected for refund')
                return redirect('sale_refund', pk=sale.pk)
        
        return redirect('sales_list')
    
    context = {
        'business': business,
        'role': role,
        'sale': sale,
        'items': items,
    }
    
    return render(request, 'pos_app/sale_refund.html', context)

# Inventory
@login_required
def inventory_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to view inventory')
        return redirect('dashboard')
    
    # Get all inventory records with pagination
    inventory_list = Inventory.objects.filter(business=business).order_by('-created_at')
    
    # Filter by product if provided
    product_id = request.GET.get('product')
    if product_id:
        inventory_list = inventory_list.filter(product_id=product_id)
    
    # Filter by transaction type if provided
    transaction_type = request.GET.get('transaction_type')
    if transaction_type:
        inventory_list = inventory_list.filter(transaction_type=transaction_type)
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            inventory_list = inventory_list.filter(created_at__date__gte=start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            inventory_list = inventory_list.filter(created_at__date__lte=end_date)
        except ValueError:
            pass
    
    paginator = Paginator(inventory_list, 10)  # Show 10 inventory records per page
    page_number = request.GET.get('page')
    inventory = paginator.get_page(page_number)
    
    # Get all products for filter dropdown
    products = Product.objects.filter(business=business, is_active=True).order_by('name')
    
    context = {
        'business': business,
        'role': role,
        'inventory': inventory,
        'products': products,
        'product_id': product_id,
        'transaction_type': transaction_type,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'pos_app/inventory.html', context)

@login_required
def inventory_adjust(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to adjust inventory')
        return redirect('inventory_list')
    
    if request.method == 'POST':
        form = InventoryForm(request.POST, business=business)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.business = business
            inventory.created_by = request.user
            inventory.save()
            messages.success(request, 'Inventory has been adjusted successfully')
            return redirect('inventory_list')
    else:
        form = InventoryForm(business=business)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'title': 'Adjust Inventory',
    }
    
    return render(request, 'pos_app/inventory_form.html', context)

# Suppliers
@login_required
def supplier_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to view suppliers')
        return redirect('dashboard')
    
    # Get all suppliers
    suppliers = Supplier.objects.filter(business=business).order_by('name')
    
    context = {
        'business': business,
        'role': role,
        'suppliers': suppliers,
    }
    
    return render(request, 'pos_app/suppliers.html', context)

@login_required
def supplier_create(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to create suppliers')
        return redirect('supplier_list')
    
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.business = business
            supplier.save()
            messages.success(request, f'Supplier "{supplier.name}" has been created')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'title': 'Create Supplier',
    }
    
    return render(request, 'pos_app/supplier_form.html', context)

@login_required
def supplier_edit(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to edit suppliers')
        return redirect('supplier_list')
    
    supplier = get_object_or_404(Supplier, pk=pk, business=business)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" has been updated')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'supplier': supplier,
        'title': 'Edit Supplier',
    }
    
    return render(request, 'pos_app/supplier_form.html', context)

@login_required
def supplier_delete(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete suppliers')
        return redirect('supplier_list')
    
    supplier = get_object_or_404(Supplier, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if supplier has purchases
        if supplier.purchases.exists():
            messages.error(request, f'Cannot delete supplier "{supplier.name}" because it has purchase records')
            return redirect('supplier_list')
        
        supplier_name = supplier.name
        supplier.delete()
        messages.success(request, f'Supplier "{supplier_name}" has been deleted')
        return redirect('supplier_list')
    
    context = {
        'business': business,
        'role': role,
        'supplier': supplier,
    }
    
    return render(request, 'pos_app/supplier_confirm_delete.html', context)

# Purchases
@login_required
def purchase_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to view purchases')
        return redirect('dashboard')
    
    # Get all purchases with pagination
    purchases_list = Purchase.objects.filter(business=business).order_by('-created_at')
    
    # Filter by supplier if provided
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        purchases_list = purchases_list.filter(supplier_id=supplier_id)
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        purchases_list = purchases_list.filter(status=status)
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            purchases_list = purchases_list.filter(created_at__date__gte=start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            purchases_list = purchases_list.filter(created_at__date__lte=end_date)
        except ValueError:
            pass
    
    paginator = Paginator(purchases_list, 10)  # Show 10 purchases per page
    page_number = request.GET.get('page')
    purchases = paginator.get_page(page_number)
    
    # Get all suppliers for filter dropdown
    suppliers = Supplier.objects.filter(business=business).order_by('name')
    
    context = {
        'business': business,
        'role': role,
        'purchases': purchases,
        'suppliers': suppliers,
        'supplier_id': supplier_id,
        'status': status,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'pos_app/purchases.html', context)



@login_required
def purchase_create(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to create purchases')
        return redirect('purchase_list')
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, business=business)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.business = business
            purchase.created_by = request.user
            purchase.save()
            
            # Redirect to add items
            return redirect('purchase_add_items', pk=purchase.pk)
        else:
            # Log form errors to the terminal
            print("Purchase Form Errors:", form.errors)  # Display errors in the terminal
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PurchaseForm(business=business)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'title': 'Create Purchase Order',
    }
    
    return render(request, 'pos_app/purchase_form.html', context)


@login_required
def purchase_add_items(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to add purchase items')
        return redirect('purchase_list')
    
    purchase = get_object_or_404(Purchase, pk=pk, business=business)
    
    if request.method == 'POST':
        form = PurchaseItemForm(request.POST, business=business)
        if form.is_valid():
            item = form.save(commit=False)
            item.purchase = purchase
            item.subtotal = item.quantity * item.unit_price
            item.save()
            
            # Update purchase total
            purchase.total_amount = purchase.items.aggregate(total=Sum('subtotal'))['total'] or 0
            purchase.save()
            
            messages.success(request, f'Item "{item.product.name}" has been added to the purchase')
            return redirect('purchase_add_items', pk=purchase.pk)
        else:
            # Log form errors to the terminal
            print("Purchase Item Form Errors:", form.errors)  # Display errors in the terminal
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PurchaseItemForm(business=business)
    
    # Get existing items
    items = purchase.items.all()
    
    context = {
        'business': business,
        'role': role,
        'purchase': purchase,
        'form': form,
        'items': items,
    }
    
    return render(request, 'pos_app/purchase_add_items.html', context)


@login_required
def purchase_item_edit(request, item_id):
    # Get the business for the logged-in user
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')

    # Retrieve the purchase item for editing
    item = get_object_or_404(PurchaseItem, id=item_id, purchase__business=business)

    if request.method == 'POST':
        form = PurchaseItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Item "{item.product.name}" has been updated successfully.')
            return redirect('purchase_add_items', pk=item.purchase.pk)
        else:
            # Log form errors for debugging
            print("Edit Purchase Item Form Errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PurchaseItemForm(instance=item)

    context = {
        'business': business,
        'form': form,
        'item': item,
        'title': 'Edit Purchase Item',
    }

    return render(request, 'pos_app/purchase_item_form.html', context)


@login_required
def purchase_item_delete(request, item_id):
    # Get the business for the logged-in user
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')

    # Retrieve the purchase item for deletion
    item = get_object_or_404(PurchaseItem, id=item_id, purchase__business=business)

    if request.method == 'POST':
        # Delete the item
        item.delete()
        messages.success(request, f'Item "{item.product.name}" has been deleted successfully.')
        return redirect('purchase_add_items', pk=item.purchase.pk)

    # If GET, render a confirmation page (optional)
    context = {
        'item': item,
        'business': business,
    }
    return render(request, 'pos_app/purchase_item_confirm_delete.html', context)

@login_required
def purchase_detail(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to view purchase details')
        return redirect('dashboard')
    
    purchase = get_object_or_404(Purchase, pk=pk, business=business)
    items = purchase.items.all()
    
    context = {
        'business': business,
        'role': role,
        'purchase': purchase,
        'items': items,
    }
    
    return render(request, 'pos_app/purchase_detail.html', context)

@login_required
def purchase_receive(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to receive purchases')
        return redirect('purchase_list')
    
    purchase = get_object_or_404(Purchase, pk=pk, business=business)
    items = purchase.items.all()
    
    if request.method == 'POST':
        # Process received items
        all_received = True
        
        for item in items:
            received_qty = int(request.POST.get(f'received_qty_{item.id}', 0))
            
            # Update received quantity
            if received_qty > 0:
                remaining_qty = item.quantity - item.received_quantity
                if received_qty > remaining_qty:
                    received_qty = remaining_qty
                
                if received_qty > 0:
                    # Update item
                    item.received_quantity += received_qty
                    item.save()
                    
                    # Add to inventory
                    Inventory.objects.create(
                        product=item.product,
                        transaction_type='purchase',
                        quantity=received_qty,
                        reference=f'PO: {purchase.reference_number}',
                        business=business,
                        created_by=request.user
                    )
            
            # Check if all items are fully received
            if item.received_quantity < item.quantity:
                all_received = False
        
        # Update purchase status
        if all_received:
            purchase.status = 'received'
        else:
            purchase.status = 'partially_received'
        
        purchase.save()
        
        messages.success(request, f'Purchase {purchase.reference_number} has been updated')
        return redirect('purchase_list')
    
    context = {
        'business': business,
        'role': role,
        'purchase': purchase,
        'items': items,
    }
    
    return render(request, 'pos_app/purchase_receive.html', context)

@login_required
def purchase_cancel(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to cancel purchases')
        return redirect('purchase_list')
    
    purchase = get_object_or_404(Purchase, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if purchase can be cancelled
        if purchase.status == 'received':
            messages.error(request, f'Purchase {purchase.reference_number} cannot be cancelled because it is already received')
            return redirect('purchase_detail', pk=purchase.pk)
        
        if purchase.status == 'partially_received':
            messages.error(request, f'Purchase {purchase.reference_number} cannot be cancelled because it is partially received')
            return redirect('purchase_detail', pk=purchase.pk)
        
        # Cancel purchase
        purchase.status = 'cancelled'
        purchase.save()
        
        messages.success(request, f'Purchase {purchase.reference_number} has been cancelled')
        return redirect('purchase_list')
    
    context = {
        'business': business,
        'role': role,
        'purchase': purchase,
    }
    
    return render(request, 'pos_app/purchase_cancel.html', context)

# Expenses
@login_required
def expense_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to view expenses')
        return redirect('dashboard')
    
    # Get all expenses with pagination
    expenses_list = Expense.objects.filter(business=business).order_by('-date')
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        expenses_list = expenses_list.filter(category=category)
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            expenses_list = expenses_list.filter(date__gte=start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            expenses_list = expenses_list.filter(date__lte=end_date)
        except ValueError:
            pass
    
    # Calculate total
    total_expense = expenses_list.aggregate(total=Sum('amount'))['total'] or 0
    
    paginator = Paginator(expenses_list, 10)  # Show 10 expenses per page
    page_number = request.GET.get('page')
    expenses = paginator.get_page(page_number)
    
    context = {
        'business': business,
        'role': role,
        'expenses': expenses,
        'total_expense': total_expense,
        'category': category,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'pos_app/expenses.html', context)

@login_required
def expense_create(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to create expenses')
        return redirect('expense_list')
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.business = business
            expense.created_by = request.user
            expense.save()
            messages.success(request, 'Expense has been created successfully')
            return redirect('expense_list')
    else:
        form = ExpenseForm(initial={'date': timezone.now().date()})
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'title': 'Create Expense',
    }
    
    return render(request, 'pos_app/expense_form.html', context)

@login_required
def expense_edit(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to edit expenses')
        return redirect('expense_list')
    
    expense = get_object_or_404(Expense, pk=pk, business=business)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            expense = form.save()
            messages.success(request, 'Expense has been updated successfully')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'expense': expense,
        'title': 'Edit Expense',
    }
    
    return render(request, 'pos_app/expense_form.html', context)

@login_required
def expense_delete(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete expenses')
        return redirect('expense_list')
    
    expense = get_object_or_404(Expense, pk=pk, business=business)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense has been deleted successfully')
        return redirect('expense_list')
    
    context = {
        'business': business,
        'role': role,
        'expense': expense,
    }
    
    return render(request, 'pos_app/expense_confirm_delete.html', context)

# Reports
@login_required
def reports(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to view reports')
        return redirect('dashboard')
    
    # Default to current month
    today = timezone.now().date()
    start_date = request.GET.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today
    
    # Sales summary
    sales = Sale.objects.filter(
        business=business,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='completed'
    )
    
    sales_summary = {
        'total_sales': sales.count(),
        'total_amount': sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'total_tax': sales.aggregate(total=Sum('tax_amount'))['total'] or 0,
        'total_discount': sales.aggregate(total=Sum('discount_amount'))['total'] or 0,
        'avg_sale': sales.aggregate(avg=Avg('total_amount'))['avg'] or 0,
    }
    
    # Sales by payment method
    sales_by_payment = sales.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-total')
    
    # Sales by day
    sales_by_day = sales.annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('day')
    
    # Top selling products
    top_products = SaleItem.objects.filter(
        sale__business=business,
        sale__created_at__date__gte=start_date,
        sale__created_at__date__lte=end_date,
        sale__status='completed'
    ).values(
        'product__name'
    ).annotate(
        quantity=Sum('quantity'),
        total=Sum('subtotal')
    ).order_by('-quantity')[:10]
    
    # Top customers
    top_customers = Sale.objects.filter(
        business=business,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='completed',
        customer__isnull=False
    ).values(
        'customer__first_name',
        'customer__last_name'
    ).annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-total')[:10]
    
    # Expenses summary
    expenses = Expense.objects.filter(
        business=business,
        date__gte=start_date,
        date__lte=end_date
    )
    
    expenses_summary = {
        'total_expenses': expenses.count(),
        'total_amount': expenses.aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Expenses by category
    expenses_by_category = expenses.values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Profit calculation
    profit = {
        'gross_sales': sales_summary['total_amount'],
        'total_expenses': expenses_summary['total_amount'],
        'net_profit': sales_summary['total_amount'] - expenses_summary['total_amount'],
    }
    
    # Inventory value
    inventory_value = Product.objects.filter(
        business=business,
        is_active=True
    ).aggregate(
        total=Sum(F('stock_quantity') * F('purchase_price'))
    )['total'] or 0
    
    # Low stock products
    low_stock_threshold = business.settings.low_stock_threshold
    low_stock_products = Product.objects.filter(
        business=business,
        stock_quantity__lte=low_stock_threshold,
        is_active=True
    ).order_by('stock_quantity')
    
    context = {
        'business': business,
        'role': role,
        'start_date': start_date,
        'end_date': end_date,
        'sales_summary': sales_summary,
        'sales_by_payment': sales_by_payment,
        'sales_by_day': list(sales_by_day),
        'top_products': top_products,
        'top_customers': top_customers,
        'expenses_summary': expenses_summary,
        'expenses_by_category': expenses_by_category,
        'profit': profit,
        'inventory_value': inventory_value,
        'low_stock_products': low_stock_products,
    }
    
    return render(request, 'pos_app/reports.html', context)

@login_required
def export_sales_report(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to export reports')
        return redirect('reports')
    
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    
    # Get sales data
    sales = Sale.objects.filter(
        business=business,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).order_by('created_at')
    
    # Create CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Invoice', 'Date', 'Customer', 'Payment Method', 'Status', 'Subtotal', 'Tax', 'Discount', 'Total'])
    
    for sale in sales:
        customer_name = sale.customer.full_name if sale.customer else 'Walk-in Customer'
        writer.writerow([
            sale.invoice_number,
            sale.created_at.strftime('%Y-%m-%d %H:%M'),
            customer_name,
            sale.get_payment_method_display(),
            sale.get_status_display(),
            sale.subtotal,
            sale.tax_amount,
            sale.discount_amount,
            sale.total_amount
        ])
    
    return response

@login_required
def export_inventory_report(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to export reports')
        return redirect('reports')
    
    # Get products
    products = Product.objects.filter(business=business).order_by('category__name', 'name')
    
    # Create CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="inventory_report_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Category', 'Product', 'SKU', 'Barcode', 'Purchase Price', 'Selling Price', 'Stock Quantity', 'Value', 'Status'])
    
    for product in products:
        category_name = product.category.name if product.category else 'Uncategorized'
        value = product.purchase_price * product.stock_quantity
        status = 'Active' if product.is_active else 'Inactive'
        writer.writerow([
            category_name,
            product.name,
            product.sku or '',
            product.barcode or '',
            product.purchase_price,
            product.selling_price,
            product.stock_quantity,
            value,
            status
        ])
    
    return response

import logging
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

# Configure logging
logger = logging.getLogger(__name__)

# Settings
@login_required
def settings_view(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('business_setup')

    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to access settings')
        return redirect('dashboard')

    if request.method == 'POST':
        business_form = BusinessForm(request.POST, request.FILES, instance=business)
        settings_form = BusinessSettingsForm(request.POST, instance=business.settings)

        # Validate forms
        if business_form.is_valid() and settings_form.is_valid():
            business_form.save()
            settings_form.save()
            messages.success(request, 'Settings have been updated successfully')
            return redirect('settings')
        else:
            # Log form errors to the terminal
            logger.error("Form validation errors: %s", {
                'business_form_errors': business_form.errors,
                'settings_form_errors': settings_form.errors
            })
            messages.error(request, 'Please correct the errors below.')

    else:
        business_form = BusinessForm(instance=business)
        settings_form = BusinessSettingsForm(instance=business.settings)

    context = {
        'business': business,
        'role': role,
        'business_form': business_form,
        'settings_form': settings_form,
    }

    return render(request, 'pos_app/settings.html', context)