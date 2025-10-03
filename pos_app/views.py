# pos_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, Q, Avg
from decimal import Decimal
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
    PurchaseItem, Expense, VATCategory, DebtPayment
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

def calculate_actual_customer_debt(customer):
    """Calculate the actual outstanding debt for a customer based on sales and payments"""
    # Get all credit sales for this customer
    credit_sales = Sale.objects.filter(
        customer=customer,
        payment_method='credit',
        status='completed'
    )
    
    total_debt = Decimal('0.00')
    for sale in credit_sales:
        # Calculate total payments made for this sale
        paid_amount = sale.debt_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Add remaining amount to total debt
        remaining = sale.total_amount - paid_amount
        if remaining > 0:
            total_debt += remaining
    
    return total_debt

def sync_customer_debt(customer):
    """Synchronize customer's current_debt field with actual outstanding amounts"""
    actual_debt = calculate_actual_customer_debt(customer)
    if customer.current_debt != actual_debt:
        customer.current_debt = actual_debt
        customer.save()
    return actual_debt

# Authentication views
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('pos:business_setup')
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
                return redirect('pos:dashboard')
            else:
                return redirect('pos:business_setup')
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
            return redirect('pos:dashboard')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('pos:login')
    
    # Date ranges for comprehensive metrics
    thirty_days_ago = timezone.now() - timedelta(days=30)
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Sales data for the last 30 days
    sales_30_days = Sale.objects.filter(
        business=business,
        created_at__gte=thirty_days_ago,
        status='completed'
    )
    
    # Current month sales (completed only)
    current_month_sales = Sale.objects.filter(
        business=business,
        created_at__gte=current_month_start,
        status='completed'
    )
    
    # All completed sales for business metrics
    all_completed_sales = Sale.objects.filter(
        business=business,
        status='completed'
    )
    
    # === COMPREHENSIVE REVENUE METRICS ===
    total_revenue = current_month_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_sales_count = current_month_sales.count()
    
    # Calculate expenses for profit calculation
    current_month_expenses = Expense.objects.filter(
        business=business,
        created_at__gte=current_month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Net profit calculation
    net_profit = total_revenue - current_month_expenses
    
    # === CUSTOMER METRICS ===
    total_customers = Customer.objects.filter(business=business).count()
    customers_with_debt = Customer.objects.filter(
        business=business, 
        current_debt__gt=0
    ).count()
    total_debt = Customer.objects.filter(
        business=business
    ).aggregate(Sum('current_debt'))['current_debt__sum'] or 0
    
    # === PRODUCT/INVENTORY METRICS ===
    total_products = Product.objects.filter(business=business, is_active=True).count()
    
    # Low stock calculation - safely get threshold
    try:
        low_stock_threshold = business.settings.low_stock_threshold
    except (AttributeError, business.settings.model.DoesNotExist):
        low_stock_threshold = 5  # Default threshold
    
    low_stock_products = Product.objects.filter(
        business=business,
        stock_quantity__lte=low_stock_threshold,
        is_active=True
    )
    low_stock_count = low_stock_products.count()
    
    # === SALES TREND DATA FOR CHARTS ===
    from django.utils import timezone as django_timezone
    sales_trend_data = []
    today = timezone.now().date()
    start_date = today - timedelta(days=29)  # 30 days including today
    
    current_date = start_date
    while current_date <= today:
        day_start = django_timezone.make_aware(
            datetime.combine(current_date, datetime.min.time())
        )
        day_end = django_timezone.make_aware(
            datetime.combine(current_date, datetime.max.time())
        )
        day_sales = all_completed_sales.filter(
            created_at__gte=day_start,
            created_at__lte=day_end
        )
        
        daily_revenue = day_sales.aggregate(total=Sum('total_amount'))['total'] or 0
        sales_trend_data.append({
            'date': current_date.strftime('%m/%d'),
            'revenue': float(daily_revenue),
            'count': day_sales.count()
        })
        current_date = current_date + timedelta(days=1)
    
    # === PAYMENT METHOD BREAKDOWN ===
    payment_method_data = []
    payment_breakdown = current_month_sales.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-count')
    
    for payment in payment_breakdown:
        payment_method_data.append({
            'method': payment['payment_method'].replace('_', ' ').title(),
            'count': payment['count'],
            'total': float(payment['total'] or 0)
        })
    
    # === RECENT ACTIVITY ===
    recent_sales = current_month_sales.order_by('-created_at')[:10]
    
    # === TOP SELLING PRODUCTS ===
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
    
    # Convert data to JSON for charts
    import json
    
    context = {
        'business': business,
        'role': role,
        # Core Metrics
        'total_revenue': total_revenue,
        'total_sales_count': total_sales_count,
        'net_profit': net_profit,
        'total_customers': total_customers,
        'total_products': total_products,
        'total_debt': total_debt,
        'customers_with_debt': customers_with_debt,
        'low_stock_count': low_stock_count,
        # Data for tables
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products[:5],  # Limit for display
        'top_products': top_products,
        # Chart data - convert to JSON
        'sales_trend_data': json.dumps(sales_trend_data),
        'payment_method_data': json.dumps(payment_method_data),
    }
    
    return render(request, 'pos_app/dashboard.html', context)

# POS (Point of Sale)
@login_required
def pos(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('pos:login')
    
    # Get all categories and products
    categories = Category.objects.filter(business=business)
    products = Product.objects.filter(business=business, is_active=True)
    customers = Customer.objects.filter(business=business)
    
    # Get most purchased products (based on total quantity sold)
    most_purchased = Product.objects.filter(
        business=business, 
        is_active=True,
        sale_items__isnull=False
    ).annotate(
        total_sold=Sum('sale_items__quantity')
    ).order_by('-total_sold')[:20]  # Top 20 most purchased
    
    # If no sales history, show products with highest stock
    if not most_purchased:
        most_purchased = products.order_by('-stock_quantity')[:20]
    
    context = {
        'business': business,
        'role': role,
        'categories': categories,
        'products': products,
        'customers': customers,
        'most_purchased': most_purchased,
    }
    
    return render(request, 'pos_app/pos.html', context)

@csrf_exempt
def process_sale(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    business = get_business_for_user(request.user)
    if not business:
        return JsonResponse({'error': 'No business found'}, status=404)
    
    try:
        print(f"DEBUG: Raw request body: {request.body}")
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        print(f"DEBUG: JSON decode error: {e}")
        return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
    except Exception as e:
        print(f"DEBUG: General error parsing request: {e}")
        return JsonResponse({'error': f'Request parsing error: {str(e)}'}, status=400)
    
    try:
        
        # Debug: Log what we received
        print(f"DEBUG: Received POST data: {data}")
        print(f"DEBUG: User authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: User: {request.user}")
        
        # Debug: Check required fields
        required_fields = ['subtotal', 'tax_amount', 'discount_amount', 'total_amount', 'payment_method', 'items']
        for field in required_fields:
            if field not in data:
                print(f"DEBUG: Missing required field: {field}")
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # Validate items
        if not data['items'] or len(data['items']) == 0:
            return JsonResponse({'error': 'No items in cart'}, status=400)
        
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
        
        # Handle credit sales
        if data['payment_method'] == 'credit':
            print(f"DEBUG: Processing credit sale")
            if not customer:
                print(f"DEBUG: No customer found for credit sale")
                return JsonResponse({'error': 'Customer required for credit sales'}, status=400)
            
            print(f"DEBUG: Customer found: {customer.full_name}")
            # Check credit limit
            total_amount = Decimal(str(data['total_amount']))
            print(f"DEBUG: Total amount: {total_amount}, Current debt: {customer.current_debt}, Credit limit: {customer.credit_limit}")
            
            if customer.current_debt + total_amount > customer.credit_limit:
                exceeded = (customer.current_debt + total_amount) - customer.credit_limit
                print(f"DEBUG: Credit limit exceeded by {exceeded}")
                # Allow override if explicitly confirmed by frontend
                if not data.get('credit_override_confirmed', False):
                    return JsonResponse({
                        'error': f'Credit limit exceeded by {exceeded}',
                        'credit_limit_exceeded': True
                    }, status=400)
                
        print(f"DEBUG: About to create sale object")
        
        # Create sale
        try:
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
                status='completed' if data['payment_method'] != 'credit' else 'completed'  # All sales are completed
            )
            print(f"DEBUG: Sale object created successfully")
        except Exception as e:
            print(f"DEBUG: Error creating sale object: {e}")
            return JsonResponse({'error': f'Error creating sale: {str(e)}'}, status=400)
        
        # Calculate loyalty points if enabled
        if business.settings.enable_customer_loyalty and customer:
            points_earned = data['total_amount'] * business.settings.points_per_purchase
            sale.loyalty_points_earned = points_earned
            sale.loyalty_points_used = data.get('loyalty_points_used', 0)
            
            # Update customer loyalty points
            customer.loyalty_points += points_earned - sale.loyalty_points_used
            customer.save()
        
        try:
            print(f"DEBUG: About to save sale")
            sale.save()
            print(f"DEBUG: Sale saved successfully with ID: {sale.id}")
        except Exception as e:
            print(f"DEBUG: Error saving sale: {e}")
            return JsonResponse({'error': f'Error saving sale: {str(e)}'}, status=400)
        
        # Handle credit debt tracking
        if data['payment_method'] == 'credit' and customer:
            customer.current_debt += Decimal(str(data['total_amount']))
            customer.save()
            
            # Create debt payment record (showing the new debt)
            from .models import DebtPayment
            # Note: DebtPayment model handles debt differently - we don't create a record for debt increase
            # The customer.current_debt is updated directly above
        
        # Create sale items
        print(f"DEBUG: About to create {len(data['items'])} sale items")
        for item_data in data['items']:
            try:
                print(f"DEBUG: Creating sale item for product {item_data['product_id']}")
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
                print(f"DEBUG: Sale item created successfully for product {product.name}")
            except Exception as e:
                print(f"DEBUG: Error creating sale item for product {item_data['product_id']}: {e}")
                return JsonResponse({'error': f'Error creating sale item: {str(e)}'}, status=400)
        
        return JsonResponse({
            'success': True,
            'invoice_number': sale.invoice_number,
            'sale_id': sale.id
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_products(request):
    """API endpoint to get all products for POS search functionality"""
    business = get_business_for_user(request.user)
    if not business:
        return JsonResponse({'error': 'No business found'}, status=404)
    
    products = Product.objects.filter(business=business, is_active=True)
    
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku or '',
            'barcode': product.barcode or '',
            'description': product.description or '',
            'category_name': product.category.name if product.category else 'Uncategorized',
            'vat_rate': product.vat_category.rate if product.vat_category else 0,
            'price': float(product.selling_price),
            'stock_quantity': product.stock_quantity,
            'is_active': product.is_active,
            'reorder_level': business.settings.low_stock_threshold if hasattr(business, 'settings') else 10,
        })
    
    return JsonResponse(products_data, safe=False)

@login_required
def api_customer(request, customer_id):
    """API endpoint to get customer details for credit limit checking"""
    business = get_business_for_user(request.user)
    if not business:
        return JsonResponse({'error': 'No business found'}, status=404)
    
    try:
        customer = Customer.objects.get(id=customer_id, business=business)
        # Get recent sales for activity
        recent_sales = Sale.objects.filter(
            customer=customer, 
            business=business
        ).order_by('-created_at')[:3]
        
        recent_activity = []
        for sale in recent_sales:
            recent_activity.append({
                'date': sale.created_at.strftime('%b %d'),
                'amount': float(sale.total_amount),
                'invoice': sale.invoice_number
            })
        
        customer_data = {
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone or '',
            'email': customer.email or '',
            'current_debt': float(customer.current_debt),
            'credit_limit': float(customer.credit_limit),
            'available_credit': float(customer.credit_limit - customer.current_debt),
            'debt_percentage': float(customer.debt_percentage),
            'recent_activity': recent_activity,
        }
        return JsonResponse(customer_data)
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)

@login_required
def get_receipt(request, sale_id):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('pos:login')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to create products')
        return redirect('pos:product_list')
    
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
            return redirect('pos:product_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to edit products')
        return redirect('pos:product_list')
    
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
            return redirect('pos:product_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete products')
        return redirect('pos:product_list')
    
    product = get_object_or_404(Product, pk=pk, business=business)
    
    if request.method == 'POST':
        product_name = product.name
        product.is_active = False
        product.save()
        messages.success(request, f'Product "{product_name}" has been deactivated')
        return redirect('pos:product_list')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('pos:login')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to create categories')
        return redirect('pos:category_list')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.business = business
            category.save()
            messages.success(request, f'Category "{category.name}" has been created')
            return redirect('pos:category_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to edit categories')
        return redirect('pos:category_list')
    
    category = get_object_or_404(Category, pk=pk, business=business)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" has been updated')
            return redirect('pos:category_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete categories')
        return redirect('pos:category_list')
    
    category = get_object_or_404(Category, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if category has products
        if category.products.exists():
            messages.error(request, f'Cannot delete category "{category.name}" because it has products')
            return redirect('pos:category_list')
        
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" has been deleted')
        return redirect('pos:category_list')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('pos:login')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'cashier']:
        messages.error(request, 'You do not have permission to create customers')
        return redirect('pos:customer_list')
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        print(f"DEBUG: Form data received: {request.POST}")
        print(f"DEBUG: Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"DEBUG: Form errors: {form.errors}")
        if form.is_valid():
            customer = form.save(commit=False)
            customer.business = business
            customer.save()
            messages.success(request, f'Customer "{customer.full_name}" has been created')
            return redirect('pos:customer_list')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = CustomerForm()
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'title': 'Create Customer',
    }
    
    return render(request, 'pos_app/customer_form_new.html', context)

@login_required
def customer_edit(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'cashier']:
        messages.error(request, 'You do not have permission to edit customers')
        return redirect('pos:customer_list')
    
    customer = get_object_or_404(Customer, pk=pk, business=business)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        print(f"DEBUG: Edit form data received: {request.POST}")
        print(f"DEBUG: Edit form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"DEBUG: Edit form errors: {form.errors}")
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.full_name}" has been updated')
            return redirect('pos:customer_list')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'business': business,
        'role': role,
        'form': form,
        'customer': customer,
        'title': 'Edit Customer',
    }
    
    return render(request, 'pos_app/customer_form_new.html', context)

@login_required
def customer_delete(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete customers')
        return redirect('pos:customer_list')
    
    customer = get_object_or_404(Customer, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if customer has sales
        if customer.sales.exists():
            messages.error(request, f'Cannot delete customer "{customer.full_name}" because they have sales records')
            return redirect('pos:customer_list')
        
        customer_name = customer.full_name
        customer.delete()
        messages.success(request, f'Customer "{customer_name}" has been deleted')
        return redirect('pos:customer_list')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to view employees')
        return redirect('pos:dashboard')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to create employees')
        return redirect('pos:employee_list')
    
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
            return redirect('pos:employee_list')
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
        return redirect('pos:business_setup')

    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete employees')
        return redirect('pos:employee_list')

    # Get the employee object
    employee = get_object_or_404(Employee, id=employee_id, business=business)

    # Delete the employee
    employee.delete()
    messages.success(request, f'Employee "{employee.user.get_full_name()}" has been deleted')
    return redirect('pos:employee_list')

@login_required
def employee_edit(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to edit employees')
        return redirect('pos:employee_list')
    
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
            return redirect('pos:employee_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to change employee status')
        return redirect('pos:employee_list')
    
    employee = get_object_or_404(Employee, pk=pk, business=business)
    
    # Toggle active status
    employee.is_active = not employee.is_active
    employee.save()
    
    status = 'activated' if employee.is_active else 'deactivated'
    messages.success(request, f'Employee "{employee.user.get_full_name()}" has been {status}')
    return redirect('pos:employee_list')

# Sales
@login_required
def sales_list(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('pos:login')
    
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

    # Breakdown by payment method and status
    payment_breakdown_qs = sales_list.values('payment_method').annotate(method_total=Sum('total_amount'), count=Count('id'))
    payment_breakdown = {entry['payment_method']: {'total': entry['method_total'], 'count': entry['count']} for entry in payment_breakdown_qs}

    status_breakdown_qs = sales_list.values('status').annotate(status_total=Sum('total_amount'), count=Count('id'))
    status_breakdown = {entry['status']: {'total': entry['status_total'], 'count': entry['count']} for entry in status_breakdown_qs}
    
    paginator = Paginator(sales_list, 10)  # Show 10 sales per page
    page_number = request.GET.get('page')
    sales = paginator.get_page(page_number)
    
    # Get customers and employees for filters
    customers = Customer.objects.filter(business=business).order_by('first_name', 'last_name')
    employees = Employee.objects.filter(business=business).select_related('user')
    
    # For sales on this page, add debt payment info (if linked)
    sales_with_debt_info = []
    for s in sales:
        debt_paid_amount = Decimal('0.00')
        debt_payments = s.debt_payments.all()
        for dp in debt_payments:
            debt_paid_amount += dp.amount
        debt_paid = debt_paid_amount >= s.total_amount if s.is_credit_sale else False
        s.debt_paid_amount = debt_paid_amount
        s.debt_paid = debt_paid
        sales_with_debt_info.append(s)

    context = {
        'business': business,
        'role': role,
        'sales': sales_with_debt_info,
        'totals': totals,
        'payment_breakdown': payment_breakdown,
        'status_breakdown': status_breakdown,
        'customers': customers,
        'employees': employees,
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'payment_method': payment_method,
        'search_query': search_query or '',  # Prevent None
    }
    
    return render(request, 'pos_app/sales.html', context)

@login_required
def sale_detail(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if not role:
        messages.error(request, 'You do not have access to this business')
        return redirect('pos:login')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to void sales')
        return redirect('pos:sales_list')
    
    sale = get_object_or_404(Sale, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if sale can be voided
        if sale.status != 'completed':
            messages.error(request, f'Sale {sale.invoice_number} cannot be voided because it is already {sale.get_status_display()}')
            return redirect('pos:sale_detail', pk=sale.pk)
        
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
        return redirect('pos:sales_list')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to refund sales')
        return redirect('pos:sales_list')
    
    sale = get_object_or_404(Sale, pk=pk, business=business)
    items = sale.items.all()
    
    if request.method == 'POST':
        # Check if sale can be refunded
        if sale.status != 'completed':
            messages.error(request, f'Sale {sale.invoice_number} cannot be refunded because it is already {sale.get_status_display()}')
            return redirect('pos:sale_detail', pk=sale.pk)
        
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
                return redirect('pos:sale_refund', pk=sale.pk)
        
        return redirect('pos:sales_list')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to view inventory')
        return redirect('pos:dashboard')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to adjust inventory')
        return redirect('pos:inventory_list')
    
    if request.method == 'POST':
        form = InventoryForm(request.POST, business=business)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.business = business
            inventory.created_by = request.user
            inventory.save()
            messages.success(request, 'Inventory has been adjusted successfully')
            return redirect('pos:inventory_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to view suppliers')
        return redirect('pos:dashboard')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to create suppliers')
        return redirect('pos:supplier_list')
    
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.business = business
            supplier.save()
            messages.success(request, f'Supplier "{supplier.name}" has been created')
            return redirect('pos:supplier_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to edit suppliers')
        return redirect('pos:supplier_list')
    
    supplier = get_object_or_404(Supplier, pk=pk, business=business)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" has been updated')
            return redirect('pos:supplier_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete suppliers')
        return redirect('pos:supplier_list')
    
    supplier = get_object_or_404(Supplier, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if supplier has purchases
        if supplier.purchases.exists():
            messages.error(request, f'Cannot delete supplier "{supplier.name}" because it has purchase records')
            return redirect('pos:supplier_list')
        
        supplier_name = supplier.name
        supplier.delete()
        messages.success(request, f'Supplier "{supplier_name}" has been deleted')
        return redirect('pos:supplier_list')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to view purchases')
        return redirect('pos:dashboard')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to create purchases')
        return redirect('pos:purchase_list')
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, business=business)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.business = business
            purchase.created_by = request.user
            purchase.save()
            
            # Redirect to add items
            return redirect('pos:purchase_add_items', pk=purchase.pk)
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to add purchase items')
        return redirect('pos:purchase_list')
    
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
            return redirect('pos:purchase_add_items', pk=purchase.pk)
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
        return redirect('pos:business_setup')

    # Retrieve the purchase item for editing
    item = get_object_or_404(PurchaseItem, id=item_id, purchase__business=business)

    if request.method == 'POST':
        form = PurchaseItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Item "{item.product.name}" has been updated successfully.')
            return redirect('pos:purchase_add_items', pk=item.purchase.pk)
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
        return redirect('pos:business_setup')

    # Retrieve the purchase item for deletion
    item = get_object_or_404(PurchaseItem, id=item_id, purchase__business=business)

    if request.method == 'POST':
        # Delete the item
        item.delete()
        messages.success(request, f'Item "{item.product.name}" has been deleted successfully.')
        return redirect('pos:purchase_add_items', pk=item.purchase.pk)

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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to view purchase details')
        return redirect('pos:dashboard')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to receive purchases')
        return redirect('pos:purchase_list')
    
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
        return redirect('pos:purchase_list')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to cancel purchases')
        return redirect('pos:purchase_list')
    
    purchase = get_object_or_404(Purchase, pk=pk, business=business)
    
    if request.method == 'POST':
        # Check if purchase can be cancelled
        if purchase.status == 'received':
            messages.error(request, f'Purchase {purchase.reference_number} cannot be cancelled because it is already received')
            return redirect('pos:purchase_detail', pk=purchase.pk)
        
        if purchase.status == 'partially_received':
            messages.error(request, f'Purchase {purchase.reference_number} cannot be cancelled because it is partially received')
            return redirect('pos:purchase_detail', pk=purchase.pk)
        
        # Cancel purchase
        purchase.status = 'cancelled'
        purchase.save()
        
        messages.success(request, f'Purchase {purchase.reference_number} has been cancelled')
        return redirect('pos:purchase_list')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to view expenses')
        return redirect('pos:dashboard')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to create expenses')
        return redirect('pos:expense_list')
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.business = business
            expense.created_by = request.user
            expense.save()
            messages.success(request, 'Expense has been created successfully')
            return redirect('pos:expense_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to edit expenses')
        return redirect('pos:expense_list')
    
    expense = get_object_or_404(Expense, pk=pk, business=business)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            expense = form.save()
            messages.success(request, 'Expense has been updated successfully')
            return redirect('pos:expense_list')
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete expenses')
        return redirect('pos:expense_list')
    
    expense = get_object_or_404(Expense, pk=pk, business=business)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense has been deleted successfully')
        return redirect('pos:expense_list')
    
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to view reports')
        return redirect('pos:dashboard')
    
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
    
    # Sales summary - convert dates to timezone-aware datetimes
    from django.utils import timezone as django_timezone
    # Convert start_date to start of day in local timezone
    start_datetime = django_timezone.make_aware(
        datetime.combine(start_date, datetime.min.time())
    )
    # Convert end_date to end of day in local timezone  
    end_datetime = django_timezone.make_aware(
        datetime.combine(end_date, datetime.max.time())
    )
    
    sales = Sale.objects.filter(
        business=business,
        created_at__gte=start_datetime,
        created_at__lte=end_datetime,
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
    
    # Sales by day - use a simpler approach without TruncDay to avoid MySQL timezone issues
    sales_by_day = []
    current_date = start_date
    while current_date <= end_date:
        day_start = django_timezone.make_aware(
            datetime.combine(current_date, datetime.min.time())
        )
        day_end = django_timezone.make_aware(
            datetime.combine(current_date, datetime.max.time())
        )
        day_sales = sales.filter(
            created_at__gte=day_start,
            created_at__lte=day_end
        )
        sales_by_day.append({
            'day': current_date,
            'count': day_sales.count(),
            'total': day_sales.aggregate(total=Sum('total_amount'))['total'] or 0
        })
        current_date = current_date + timedelta(days=1)
    
    # Top selling products  
    top_products = SaleItem.objects.filter(
        sale__business=business,
        sale__created_at__gte=start_datetime,
        sale__created_at__lte=end_datetime,
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
        created_at__gte=start_datetime,
        created_at__lte=end_datetime,
        status='completed',
        customer__isnull=False
    ).values(
        'customer__first_name',
        'customer__last_name'
    ).annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-total')[:10]
    
    # Expenses summary - use date filtering for expenses as they use date field, not datetime
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
    
    # VAT summary for quick overview
    vat_categories = VATCategory.objects.filter(business=business, is_active=True)
    vat_summary_quick = []
    
    for vat_cat in vat_categories:
        # Get sales items for this VAT category in the period
        vat_items = SaleItem.objects.filter(
            sale__business=business,
            sale__created_at__gte=start_datetime,
            sale__created_at__lte=end_datetime,
            sale__status='completed',
            product__vat_category=vat_cat
        )
        
        total_excl_vat = Decimal('0.00')
        total_vat = Decimal('0.00')
        total_incl_vat = Decimal('0.00')
        transaction_count = 0
        
        for item in vat_items:
            item_excl_vat = item.product.calculate_price_excluding_vat(item.unit_price)
            item_vat = item.product.calculate_vat_amount(item.unit_price)
            
            total_excl_vat += item_excl_vat * item.quantity
            total_vat += item_vat * item.quantity  
            total_incl_vat += item.unit_price * item.quantity
            transaction_count += 1
        
        if transaction_count > 0:  # Only include categories with actual sales
            vat_summary_quick.append({
                'category': vat_cat,
                'total_excl_vat': total_excl_vat,
                'total_vat': total_vat,
                'total_incl_vat': total_incl_vat,
                'transaction_count': transaction_count
            })
    
    context = {
        'business': business,
        'role': role,
        'start_date': start_date,
        'end_date': end_date,
        'sales_summary': sales_summary,
        'sales_by_payment': sales_by_payment,
        'sales_by_day': sales_by_day,
        'top_products': top_products,
        'top_customers': top_customers,
        'expenses_summary': expenses_summary,
        'expenses_by_category': expenses_by_category,
        'profit': profit,
        'inventory_value': inventory_value,
        'low_stock_products': low_stock_products,
        'vat_categories': vat_categories,
        'vat_summary_quick': vat_summary_quick,
    }
    
    return render(request, 'pos_app/reports.html', context)

@login_required
def export_sales_report(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to export reports')
        return redirect('pos:reports')
    
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Default to current month if no dates provided
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
    except (ValueError, TypeError):
        # Fallback to current month if invalid dates
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    
    # Get sales data - use timezone-aware datetimes for consistent filtering
    from django.utils import timezone as django_timezone
    start_datetime = django_timezone.make_aware(
        datetime.combine(start_date, datetime.min.time())
    )
    end_datetime = django_timezone.make_aware(
        datetime.combine(end_date, datetime.max.time())
    )
    
    sales = Sale.objects.filter(
        business=business,
        created_at__gte=start_datetime,
        created_at__lte=end_datetime,
        status='completed'
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
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager', 'inventory']:
        messages.error(request, 'You do not have permission to export reports')
        return redirect('pos:reports')
    
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

# Configure logging
logger = logging.getLogger(__name__)

# Settings
@login_required
def settings_view(request):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')

    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to access settings')
        return redirect('pos:dashboard')

    if request.method == 'POST':
        business_form = BusinessForm(request.POST, request.FILES, instance=business)
        settings_form = BusinessSettingsForm(request.POST, instance=business.settings, business=business)

        # Validate forms
        if business_form.is_valid() and settings_form.is_valid():
            business_form.save()
            settings_form.save()
            messages.success(request, 'Settings have been updated successfully')
            return redirect('pos:settings')
        else:
            # Log form errors to the terminal
            logger.error("Form validation errors: %s", {
                'business_form_errors': business_form.errors,
                'settings_form_errors': settings_form.errors
            })
            messages.error(request, 'Please correct the errors below.')

    else:
        business_form = BusinessForm(instance=business)
        settings_form = BusinessSettingsForm(instance=business.settings, business=business)

    context = {
        'business': business,
        'role': role,
        'business_form': business_form,
        'settings_form': settings_form,
    }

    return render(request, 'pos_app/settings.html', context)

@login_required
def vat_report(request):
    """Generate comprehensive VAT report for KRA compliance"""
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to view VAT reports')
        return redirect('pos:dashboard')
    
    # Get date range
    today = timezone.now().date()
    start_date = request.GET.get('start_date', today.replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today
    
    # Convert to timezone-aware datetimes
    from django.utils import timezone as django_timezone
    start_datetime = django_timezone.make_aware(
        datetime.combine(start_date, datetime.min.time())
    )
    end_datetime = django_timezone.make_aware(
        datetime.combine(end_date, datetime.max.time())
    )
    
    # Get sales with VAT
    sales = Sale.objects.filter(
        business=business,
        created_at__gte=start_datetime,
        created_at__lte=end_datetime,
        status='completed'
    ).select_related('customer').prefetch_related('items__product__vat_category')
    
    # Group sales by VAT category
    vat_summary = {}
    total_sales_excl_vat = Decimal('0.00')
    total_vat = Decimal('0.00')
    total_sales_incl_vat = Decimal('0.00')
    
    for sale in sales:
        for item in sale.items.all():
            vat_category = item.product.vat_category
            category_name = vat_category.name if vat_category else 'No VAT Category'
            category_code = vat_category.code if vat_category else 'N/A'
            vat_rate = vat_category.rate if vat_category else Decimal('0.00')
            
            # Calculate VAT amounts
            item_excl_vat = item.product.calculate_price_excluding_vat(item.price)
            item_vat = item.product.calculate_vat_amount(item.price)
            item_incl_vat = item.price
            
            # Multiply by quantity
            total_excl_vat = item_excl_vat * item.quantity
            total_vat_amount = item_vat * item.quantity
            total_incl_vat = item_incl_vat * item.quantity
            
            if category_code not in vat_summary:
                vat_summary[category_code] = {
                    'name': category_name,
                    'code': category_code,
                    'rate': vat_rate,
                    'sales_excl_vat': Decimal('0.00'),
                    'vat_amount': Decimal('0.00'),
                    'sales_incl_vat': Decimal('0.00'),
                    'transaction_count': 0
                }
            
            vat_summary[category_code]['sales_excl_vat'] += total_excl_vat
            vat_summary[category_code]['vat_amount'] += total_vat_amount
            vat_summary[category_code]['sales_incl_vat'] += total_incl_vat
            vat_summary[category_code]['transaction_count'] += 1
            
            # Add to totals
            total_sales_excl_vat += total_excl_vat
            total_vat += total_vat_amount
            total_sales_incl_vat += total_incl_vat
    
    # Get VAT categories for the business
    vat_categories = VATCategory.objects.filter(business=business, is_active=True)
    
    context = {
        'business': business,
        'role': role,
        'start_date': start_date,
        'end_date': end_date,
        'vat_summary': vat_summary,
        'vat_categories': vat_categories,
        'total_sales_excl_vat': total_sales_excl_vat,
        'total_vat': total_vat,
        'total_sales_incl_vat': total_sales_incl_vat,
        'sales_count': sales.count(),
    }
    
    return render(request, 'pos_app/vat_report.html', context)

@login_required
def export_vat_report(request):
    """Export VAT report as CSV for KRA submission"""
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to export VAT reports')
        return redirect('pos:vat_report')
    
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            start_date = today.replace(day=1)
            end_date = today
    except (ValueError, TypeError):
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="vat_report_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Business Name', business.name,
        'KRA PIN', business.settings.kra_pin or 'Not Set',
        'VAT Number', business.settings.vat_number or 'Not Set',
        'Period', f'{start_date} to {end_date}'
    ])
    writer.writerow([])  # Empty row
    writer.writerow([
        'VAT Category Code', 'VAT Category Name', 'VAT Rate (%)', 
        'Sales Excl. VAT', 'VAT Amount', 'Sales Incl. VAT', 'Transaction Count'
    ])
    
    # Get sales data (reuse logic from vat_report view)
    from django.utils import timezone as django_timezone
    start_datetime = django_timezone.make_aware(
        datetime.combine(start_date, datetime.min.time())
    )
    end_datetime = django_timezone.make_aware(
        datetime.combine(end_date, datetime.max.time())
    )
    
    sales = Sale.objects.filter(
        business=business,
        created_at__gte=start_datetime,
        created_at__lte=end_datetime,
        status='completed'
    ).select_related('customer').prefetch_related('items__product__vat_category')
    
    # Group sales by VAT category
    vat_summary = {}
    total_sales_excl_vat = Decimal('0.00')
    total_vat = Decimal('0.00')
    total_sales_incl_vat = Decimal('0.00')
    
    for sale in sales:
        for item in sale.items.all():
            vat_category = item.product.vat_category
            category_name = vat_category.name if vat_category else 'No VAT Category'
            category_code = vat_category.code if vat_category else 'N/A'
            vat_rate = vat_category.rate if vat_category else Decimal('0.00')
            
            # Calculate VAT amounts
            item_excl_vat = item.product.calculate_price_excluding_vat(item.price)
            item_vat = item.product.calculate_vat_amount(item.price)
            
            # Multiply by quantity
            total_excl_vat = item_excl_vat * item.quantity
            total_vat_amount = item_vat * item.quantity
            total_incl_vat = item.price * item.quantity
            
            if category_code not in vat_summary:
                vat_summary[category_code] = {
                    'name': category_name,
                    'code': category_code,
                    'rate': vat_rate,
                    'sales_excl_vat': Decimal('0.00'),
                    'vat_amount': Decimal('0.00'),
                    'sales_incl_vat': Decimal('0.00'),
                    'transaction_count': 0
                }
            
            vat_summary[category_code]['sales_excl_vat'] += total_excl_vat
            vat_summary[category_code]['vat_amount'] += total_vat_amount
            vat_summary[category_code]['sales_incl_vat'] += total_incl_vat
            vat_summary[category_code]['transaction_count'] += 1
            
            # Add to totals
            total_sales_excl_vat += total_excl_vat
            total_vat += total_vat_amount
            total_sales_incl_vat += total_incl_vat
    
    # Write data rows
    for code, summary in vat_summary.items():
        writer.writerow([
            summary['code'],
            summary['name'],
            f"{summary['rate']:.2f}",
            f"{summary['sales_excl_vat']:.2f}",
            f"{summary['vat_amount']:.2f}",
            f"{summary['sales_incl_vat']:.2f}",
            summary['transaction_count']
        ])
    
    # Write totals
    writer.writerow([])  # Empty row
    writer.writerow([
        'TOTALS', '', '',
        f"{total_sales_excl_vat:.2f}",
        f"{total_vat:.2f}",
        f"{total_sales_incl_vat:.2f}",
        sales.count()
    ])
    
    return response

@login_required
def vat_management(request):
    """VAT category management interface"""
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to manage VAT settings')
        return redirect('pos:dashboard')
    
    # Get VAT categories
    vat_categories = VATCategory.objects.filter(business=business).order_by('name')
    
    context = {
        'business': business,
        'role': role,
        'vat_categories': vat_categories,
    }
    
    return render(request, 'pos_app/vat_management.html', context)

@login_required
# Removed duplicate add_vat_category function - using the one below that handles both form and JSON data

@login_required
def edit_vat_category(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to edit VAT categories')
        return redirect('pos:vat_management')
    
    from .models import VATCategory
    vat_category = get_object_or_404(VATCategory, pk=pk, business=business)
    
    if request.method == 'POST':
        vat_category.name = request.POST.get('name', vat_category.name)
        vat_category.code = request.POST.get('code', vat_category.code)
        vat_category.rate = Decimal(request.POST.get('rate', vat_category.rate))
        vat_category.description = request.POST.get('description', vat_category.description)
        vat_category.is_active = request.POST.get('is_active') == 'on'
        vat_category.save()
        messages.success(request, f'VAT category "{vat_category.name}" has been updated')
    
    return redirect('pos:vat_management')

@login_required
def delete_vat_category(request, pk):
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        messages.error(request, 'You do not have permission to delete VAT categories')
        return redirect('pos:vat_management')
    
    from .models import VATCategory
    vat_category = get_object_or_404(VATCategory, pk=pk, business=business)
    
    if request.method == 'POST':
        name = vat_category.name
        vat_category.delete()
        messages.success(request, f'VAT category "{name}" has been deleted')
    
    return redirect('pos:vat_management')

@login_required
def credit_management(request):
    """Credit and debt management interface"""
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to manage credit')
        return redirect('pos:dashboard')
    
    # Sync all customer debts to ensure consistency
    all_customers = Customer.objects.filter(business=business)
    for customer in all_customers:
        sync_customer_debt(customer)
    
    # Get all customers for credit management (including those without current debt)
    all_customers_list = Customer.objects.filter(business=business).order_by('-current_debt', 'first_name', 'last_name')
    
    # Separate customers with and without debt for different sections
    customers_with_debt = [c for c in all_customers_list if c.current_debt > 0]
    customers_without_debt = [c for c in all_customers_list if c.current_debt == 0]
    
    # Get all debt payments for reporting
    debt_payments = DebtPayment.objects.filter(
        business=business
    ).order_by('-created_at')[:50]  # Last 50 payments
    
    # Calculate summary statistics
    total_outstanding = sum(c.current_debt for c in customers_with_debt)
    customers_count = len(customers_with_debt)
    
    # Get overdue debts (customers with debt older than 30 days)
    from datetime import timedelta
    overdue_date = timezone.now().date() - timedelta(days=30)
    overdue_debts = Customer.objects.filter(
        business=business,
        current_debt__gt=0
    ).distinct()
    
    context = {
        'business': business,
        'role': role,
        'customers_with_debt': customers_with_debt,
        'customers_without_debt': customers_without_debt,
        'all_customers': all_customers_list,
        'debt_payments': debt_payments,
        'total_outstanding': total_outstanding,
        'customers_count': customers_count,
        'overdue_debts': overdue_debts,
    }
    # Add JSON serializable data for client-side payment modal (include ALL customers)
    context['customers_with_debt_json'] = json.dumps([
        {
            'id': c.id,
            'full_name': c.full_name,
            'email': c.email or '',
            'phone': c.phone or '',
            'current_debt': float(c.current_debt),
            'credit_limit': float(c.credit_limit),
        } for c in all_customers_list  # Include all customers, not just those with debt
    ])
    context['debt_payments_json'] = json.dumps([
        {
            'id': p.id,
            'customer_id': p.customer.id,
            'customer_name': p.customer.full_name,
            'amount': float(p.amount),
            'payment_type': p.payment_type,
            'payment_reference': p.payment_reference,
            'notes': p.notes,
            'created_at': p.created_at.isoformat(),
            'sale_id': p.sale.id if p.sale else None,
        } for p in debt_payments
    ])

    # Build a map of outstanding credit sales per customer so payments can be linked to a sale
    customer_credit_sales = {}
    for c in customers_with_debt:
        sales_qs = Sale.objects.filter(business=business, customer=c, payment_method='credit', status='completed')
        sales_list = []
        for s in sales_qs:
            paid_amount = s.debt_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            remaining = s.total_amount - paid_amount
            if remaining > 0:
                sales_list.append({
                    'id': s.id,
                    'invoice_number': s.invoice_number,
                    'total_amount': float(s.total_amount),
                    'remaining': float(remaining),
                    'created_at': s.created_at.isoformat(),
                })
        customer_credit_sales[c.id] = sales_list

    context['customer_credit_sales_json'] = json.dumps(customer_credit_sales)
    
    return render(request, 'pos_app/credit_management.html', context)

@login_required
def receive_payment(request):
    """Process debt payment from customer"""
    business = get_business_for_user(request.user)
    if not business:
        return JsonResponse({'error': 'No business found'}, status=404)
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer = Customer.objects.get(id=data['customer_id'], business=business)
            payment_amount = Decimal(str(data['amount']))
            
            if payment_amount <= 0:
                return JsonResponse({'error': 'Payment amount must be greater than zero'}, status=400)
            
            # Only check debt limit if customer has existing debt
            if customer.current_debt > 0 and payment_amount > customer.current_debt:
                return JsonResponse({'error': 'Payment amount cannot exceed current debt'}, status=400)
            
            # Update customer debt (only reduce if they have existing debt)
            if customer.current_debt > 0:
                customer.current_debt -= payment_amount
                customer.save()
            
            # Handle payment allocation to sales
            remaining_payment = payment_amount
            payments_created = []
            
            sale_id = data.get('sale_id')
            if sale_id:
                # Payment applied to specific sale
                try:
                    sale_obj = Sale.objects.get(id=sale_id, business=business)
                    payment_record = DebtPayment.objects.create(
                        customer=customer,
                        amount=payment_amount,
                        payment_type=data.get('payment_method', 'cash'),
                        payment_reference=data.get('reference', ''),
                        notes=data.get('notes', ''),
                        business=business,
                        created_by=request.user,
                        sale=sale_obj
                    )
                    payments_created.append(payment_record)
                except Sale.DoesNotExist:
                    # Fall back to auto-allocation if sale not found
                    sale_id = None
            
            if not sale_id:
                # Auto-allocate payment to oldest outstanding sales (FIFO)
                outstanding_sales = Sale.objects.filter(
                    business=business,
                    customer=customer,
                    payment_method='credit',
                    status='completed'
                ).order_by('created_at')
                
                for sale in outstanding_sales:
                    if remaining_payment <= 0:
                        break
                    
                    # Calculate how much is already paid for this sale
                    paid_amount = sale.debt_payments.aggregate(
                        total=Sum('amount')
                    )['total'] or Decimal('0.00')
                    
                    sale_remaining = sale.total_amount - paid_amount
                    
                    if sale_remaining > 0:
                        # Apply payment to this sale
                        payment_to_apply = min(remaining_payment, sale_remaining)
                        
                        payment_record = DebtPayment.objects.create(
                            customer=customer,
                            amount=payment_to_apply,
                            payment_type=data.get('payment_method', 'cash'),
                            payment_reference=data.get('reference', ''),
                            notes=data.get('notes', f'Auto-allocated to {sale.invoice_number}'),
                            business=business,
                            created_by=request.user,
                            sale=sale
                        )
                        payments_created.append(payment_record)
                        remaining_payment -= payment_to_apply
                
                # If there's still remaining payment (shouldn't happen with proper validation)
                if remaining_payment > 0:
                    payment_record = DebtPayment.objects.create(
                        customer=customer,
                        amount=remaining_payment,
                        payment_type=data.get('payment_method', 'cash'),
                        payment_reference=data.get('reference', ''),
                        notes=data.get('notes', 'Unallocated payment'),
                        business=business,
                        created_by=request.user,
                        sale=None
                    )
                    payments_created.append(payment_record)
            
            return JsonResponse({
                'success': True,
                'new_debt': float(customer.current_debt),
                'message': f'Payment of {business.currency_symbol}{payment_amount} received successfully'
            })
            
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def add_vat_category(request):
    """Add new VAT category - handles both form data and JSON data"""
    business = get_business_for_user(request.user)
    if not business:
        # For form submissions, redirect to business setup
        if request.content_type == 'application/json' or request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
            return JsonResponse({'error': 'No business found'}, status=404)
        else:
            return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin']:
        if request.content_type == 'application/json' or request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        else:
            messages.error(request, 'You do not have permission to add VAT categories')
            return redirect('pos:vat_management')
    
    if request.method == 'POST':
        try:
            # Check if this is a JSON request or form request
            is_json_request = request.content_type == 'application/json' or request.META.get('HTTP_ACCEPT', '').startswith('application/json')
            
            if is_json_request:
                # Handle JSON data
                data = json.loads(request.body)
                name = data.get('name', '').strip()
                code = data.get('code', '').strip()
                rate = Decimal(str(data.get('rate', 0)))
                description = data.get('description', '').strip()
                is_active = data.get('is_active', True)
            else:
                # Handle form data
                name = request.POST.get('name', '').strip()
                code = request.POST.get('code', '').strip()
                rate = Decimal(str(request.POST.get('rate', 0)))
                description = request.POST.get('description', '').strip()
                is_active = request.POST.get('is_active') == 'on' or request.POST.get('is_active') == True
            
            # Validation
            if not name:
                error_msg = 'Category name is required'
                if is_json_request:
                    return JsonResponse({'error': error_msg}, status=400)
                else:
                    messages.error(request, error_msg)
                    return redirect('pos:vat_management')
            
            if not code:
                error_msg = 'VAT code is required'
                if is_json_request:
                    return JsonResponse({'error': error_msg}, status=400)
                else:
                    messages.error(request, error_msg)
                    return redirect('pos:vat_management')
            
            if rate < 0:
                error_msg = 'VAT rate cannot be negative'
                if is_json_request:
                    return JsonResponse({'error': error_msg}, status=400)
                else:
                    messages.error(request, error_msg)
                    return redirect('pos:vat_management')
            
            # Check if category already exists (by name or code)
            if VATCategory.objects.filter(business=business, name=name).exists():
                error_msg = 'VAT category with this name already exists'
                if is_json_request:
                    return JsonResponse({'error': error_msg}, status=400)
                else:
                    messages.error(request, error_msg)
                    return redirect('pos:vat_management')
            
            if VATCategory.objects.filter(business=business, code=code).exists():
                error_msg = f'VAT category with code "{code}" already exists'
                if is_json_request:
                    return JsonResponse({'error': error_msg}, status=400)
                else:
                    messages.error(request, error_msg)
                    return redirect('pos:vat_management')
            
            # Create new VAT category
            vat_category = VATCategory.objects.create(
                business=business,
                name=name,
                code=code,
                rate=rate,
                description=description,
                is_active=is_active
            )
            
            success_msg = f'VAT category "{name}" added successfully'
            
            if is_json_request:
                return JsonResponse({
                    'success': True,
                    'message': success_msg,
                    'category': {
                        'id': vat_category.id,
                        'name': vat_category.name,
                        'code': vat_category.code,
                        'rate': float(vat_category.rate),
                        'description': vat_category.description,
                        'is_active': vat_category.is_active
                    }
                })
            else:
                messages.success(request, success_msg)
                return redirect('pos:vat_management')
            
        except json.JSONDecodeError:
            if is_json_request:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            else:
                messages.error(request, 'Invalid form data')
                return redirect('pos:vat_management')
        except Exception as e:
            error_msg = f'Error creating VAT category: {str(e)}'
            if is_json_request:
                return JsonResponse({'error': error_msg}, status=500)
            else:
                messages.error(request, error_msg)
                return redirect('pos:vat_management')
    
    # For non-POST requests
    if request.content_type == 'application/json' or request.META.get('HTTP_ACCEPT', '').startswith('application/json'):
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    else:
        return redirect('pos:vat_management')


@login_required
def edit_vat_category(request, pk):
    """Edit existing VAT category"""
    business = get_business_for_user(request.user)
    if not business:
        return JsonResponse({'error': 'No business found'}, status=404)
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        try:
            # Get data from POST request (form data, not JSON)
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()
            rate = Decimal(str(request.POST.get('rate', 0)))
            description = request.POST.get('description', '').strip()
            is_active = request.POST.get('is_active') == 'on'
            
            if not name:
                return JsonResponse({'error': 'Category name is required'}, status=400)
            
            if rate < 0:
                return JsonResponse({'error': 'VAT rate cannot be negative'}, status=400)
            
            # Get the category using pk from URL
            try:
                vat_category = VATCategory.objects.get(id=pk, business=business)
            except VATCategory.DoesNotExist:
                return JsonResponse({'error': 'VAT category not found'}, status=404)
            
            # Check if another category with the same name exists (excluding current)
            if VATCategory.objects.filter(business=business, name=name).exclude(id=pk).exists():
                return JsonResponse({'error': 'VAT category with this name already exists'}, status=400)
            
            # Update the category
            vat_category.name = name
            vat_category.code = code
            vat_category.rate = rate
            vat_category.description = description
            vat_category.is_active = is_active
            vat_category.save()
            
            # Redirect back to VAT management page
            messages.success(request, f'VAT category "{name}" updated successfully')
            return redirect('pos:vat_management')
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def delete_vat_category(request, pk):
    """Delete VAT category"""
    business = get_business_for_user(request.user)
    if not business:
        return JsonResponse({'error': 'No business found'}, status=404)
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        try:
            # Get the category using pk from URL
            try:
                vat_category = VATCategory.objects.get(id=pk, business=business)
            except VATCategory.DoesNotExist:
                messages.error(request, 'VAT category not found')
                return redirect('pos:vat_management')
            
            # Check if category is in use by any products
            if vat_category.products.exists():
                messages.error(request, 'Cannot delete VAT category that is assigned to products. Please reassign products first.')
                return redirect('pos:vat_management')
            
            category_name = vat_category.name
            vat_category.delete()
            
            messages.success(request, f'VAT category "{category_name}" deleted successfully')
            return redirect('pos:vat_management')
            
        except Exception as e:
            messages.error(request, f'Error deleting VAT category: {str(e)}')
            return redirect('pos:vat_management')
    
    messages.error(request, 'Invalid request method')
    return redirect('pos:vat_management')

@login_required
def credit_report_overall(request):
    """Comprehensive credit report for all customers with debt"""
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to view credit reports')
        return redirect('pos:dashboard')
    
    # Sync all customer debts first
    all_customers = Customer.objects.filter(business=business)
    for customer in all_customers:
        sync_customer_debt(customer)
    
    # Get customers with debt after syncing
    customers_with_debt = Customer.objects.filter(
        business=business, 
        current_debt__gt=0
    ).order_by('-current_debt')
    
    # Get all debt payments for analysis
    debt_payments = DebtPayment.objects.filter(
        business=business
    ).order_by('-created_at')[:100]  # Last 100 payments
    
    # Calculate summary statistics
    total_outstanding = customers_with_debt.aggregate(
        total=Sum('current_debt')
    )['total'] or Decimal('0.00')
    
    customers_count = customers_with_debt.count()
    
    # Get overdue debts (customers with debt older than 30 days)
    from datetime import timedelta
    overdue_date = timezone.now().date() - timedelta(days=30)
    overdue_customers = []
    
    # Build detailed customer data with sales and payment info
    detailed_customers = []
    for customer in customers_with_debt:
        # Get outstanding credit sales
        outstanding_sales = Sale.objects.filter(
            business=business,
            customer=customer,
            payment_method='credit',
            status='completed'
        ).order_by('created_at')
        
        sales_data = []
        for sale in outstanding_sales:
            paid_amount = sale.debt_payments.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            remaining = sale.total_amount - paid_amount
            
            if remaining > 0:
                sales_data.append({
                    'sale': sale,
                    'paid_amount': paid_amount,
                    'remaining': remaining,
                    'is_overdue': sale.created_at.date() < overdue_date
                })
        
        # Get recent payments
        recent_payments = customer.debt_payments.order_by('-created_at')[:5]
        
        # Calculate totals
        total_paid = customer.debt_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        customer_data = {
            'customer': customer,
            'outstanding_sales': sales_data,
            'recent_payments': recent_payments,
            'total_paid': total_paid,
            'credit_utilization': (customer.current_debt / customer.credit_limit * 100) if customer.credit_limit > 0 else 0,
            'is_over_limit': customer.current_debt > customer.credit_limit,
            'has_overdue': any(s['is_overdue'] for s in sales_data)
        }
        detailed_customers.append(customer_data)
        
        if customer_data['has_overdue']:
            overdue_customers.append(customer)
    
    context = {
        'business': business,
        'role': role,
        'detailed_customers': detailed_customers,
        'total_outstanding': total_outstanding,
        'customers_count': customers_count,
        'overdue_count': len(overdue_customers),
        'recent_payments': debt_payments[:20],  # Last 20 payments for sidebar
        'report_generated_at': timezone.now(),
    }
    
    # Check if PDF export is requested
    if request.GET.get('format') == 'pdf':
        return generate_overall_credit_pdf(request, context)
    
    return render(request, 'pos_app/credit_report_overall.html', context)

def generate_overall_credit_pdf(request, context):
    """Generate PDF version of overall credit report"""
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                fontSize=20, spaceAfter=30, alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], 
                                  fontSize=14, spaceAfter=12, alignment=TA_LEFT)
    
    business = context['business']
    
    # Title
    title = Paragraph(f"Credit Report - Overall", title_style)
    elements.append(title)
    
    # Business and date info
    business_info = Paragraph(f"{business.name}<br/>Generated: {context['report_generated_at'].strftime('%B %d, %Y at %I:%M %p')}", styles['Normal'])
    elements.append(business_info)
    elements.append(Spacer(1, 20))
    
    # Summary Statistics
    summary_data = [
        ['Summary Statistics', ''],
        ['Total Outstanding Debt:', f"{business.currency_symbol}{context['total_outstanding']:,.2f}"],
        ['Number of Customers with Debt:', str(context['customers_count'])],
        ['Number of Overdue Accounts:', str(context['overdue_count'])],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Customers with Debt
    if context['detailed_customers']:
        elements.append(Paragraph("Customers with Outstanding Debt", heading_style))
        
        customer_data = [['Customer', 'Phone', 'Outstanding Amount', 'Credit Limit', 'Utilization %']]
        for customer_info in context['detailed_customers']:
            customer = customer_info['customer']
            customer_data.append([
                customer.full_name,
                customer.phone or 'N/A',
                f"{business.currency_symbol}{customer.current_debt:,.2f}",
                f"{business.currency_symbol}{customer.credit_limit:,.2f}",
                f"{customer_info['credit_utilization']:.1f}%"
            ])
        
        customer_table = Table(customer_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(customer_table)
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="credit_report_overall_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    return response

@login_required
def credit_report_customer(request, customer_id):
    """Detailed credit report for a specific customer"""
    business = get_business_for_user(request.user)
    if not business:
        return redirect('pos:business_setup')
    
    # Get user role
    role = get_user_role(request.user, business)
    if role not in ['owner', 'admin', 'manager']:
        messages.error(request, 'You do not have permission to view credit reports')
        return redirect('pos:dashboard')
    
    customer = get_object_or_404(Customer, id=customer_id, business=business)
    
    # Sync customer debt first
    sync_customer_debt(customer)
    
    # Get all credit sales for this customer
    credit_sales = Sale.objects.filter(
        business=business,
        customer=customer,
        payment_method='credit'
    ).order_by('created_at')
    
    # Build sales data with payment details
    sales_data = []
    total_credit_sales = Decimal('0.00')
    total_paid = Decimal('0.00')
    
    for sale in credit_sales:
        payments = sale.debt_payments.order_by('created_at')
        paid_amount = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        remaining = sale.total_amount - paid_amount
        
        sales_data.append({
            'sale': sale,
            'payments': payments,
            'paid_amount': paid_amount,
            'remaining': remaining,
            'is_fully_paid': remaining <= 0,
            'payment_percentage': (paid_amount / sale.total_amount * 100) if sale.total_amount > 0 else 0
        })
        
        total_credit_sales += sale.total_amount
        total_paid += paid_amount
    
    # Get all payments for this customer (including unallocated)
    all_payments = customer.debt_payments.order_by('-created_at')
    
    # Calculate payment method breakdown
    payment_method_breakdown = all_payments.values('payment_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Add percentage calculation to payment methods
    total_payments_amount = all_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    payment_methods = []
    for method in payment_method_breakdown:
        percentage = (method['total'] / total_payments_amount * 100) if total_payments_amount > 0 else 0
        payment_methods.append({
            'payment_type': method['payment_type'],
            'total_amount': method['total'],
            'count': method['count'],
            'percentage': percentage
        })
    
    # Calculate outstanding sales
    outstanding_sales = []
    outstanding_sales_count = 0
    for sale_data in sales_data:
        if sale_data['remaining'] > 0:
            outstanding_sales.append(sale_data)
            outstanding_sales_count += 1
    
    # Calculate averages
    average_sale_amount = total_credit_sales / len(credit_sales) if credit_sales else Decimal('0.00')
    average_payment_amount = total_payments_amount / all_payments.count() if all_payments.count() > 0 else Decimal('0.00')
    
    # Get last payment date
    last_payment = all_payments.first()
    last_payment_date = last_payment.created_at if last_payment else None
    
    # Calculate overdue information
    has_overdue = False
    overdue_days = 0
    if outstanding_sales:
        # Check if any outstanding sales are over 30 days old
        from datetime import timedelta
        cutoff_date = timezone.now().date() - timedelta(days=30)
        for sale_data in outstanding_sales:
            if sale_data['sale'].created_at.date() < cutoff_date:
                has_overdue = True
                days_old = (timezone.now().date() - sale_data['sale'].created_at.date()).days
                overdue_days = max(overdue_days, days_old)
    
    context = {
        'business': business,
        'role': role,
        'customer': customer,
        'outstanding_sales': outstanding_sales,
        'outstanding_sales_count': outstanding_sales_count,
        'recent_payments': all_payments[:20],  # Last 20 payments
        'payment_methods': payment_methods,
        'total_credit_sales': len(credit_sales),
        'total_payments': all_payments.count(),
        'total_paid': total_paid,
        'credit_utilization': (customer.current_debt / customer.credit_limit * 100) if customer.credit_limit > 0 else 0,
        'is_over_limit': customer.current_debt > customer.credit_limit,
        'has_overdue': has_overdue,
        'overdue_days': overdue_days,
        'average_sale_amount': average_sale_amount,
        'average_payment_amount': average_payment_amount,
        'last_payment_date': last_payment_date,
        'report_generated_at': timezone.now(),
    }
    
    # Check if PDF export is requested
    if request.GET.get('format') == 'pdf':
        return generate_customer_credit_pdf(request, customer, context)
    
    return render(request, 'pos_app/credit_report_customer.html', context)

def generate_customer_credit_pdf(request, customer, context):
    """Generate PDF version of customer credit report"""
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                fontSize=18, spaceAfter=30, alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], 
                                  fontSize=14, spaceAfter=12, alignment=TA_LEFT)
    normal_style = styles['Normal']
    
    business = context['business']
    
    # Title
    title = Paragraph(f"Credit Report - {customer.full_name}", title_style)
    elements.append(title)
    
    # Business info
    business_info = Paragraph(f"{business.name}<br/>Generated: {context['report_generated_at'].strftime('%B %d, %Y at %I:%M %p')}", normal_style)
    elements.append(business_info)
    elements.append(Spacer(1, 12))
    
    # Customer Information Table
    customer_data = [
        ['Customer Information', ''],
        ['Name:', customer.full_name],
        ['Phone:', customer.phone or 'N/A'],
        ['Email:', customer.email or 'N/A'],
        ['Address:', customer.address or 'N/A'],
        ['Credit Limit:', f"{business.currency_symbol}{customer.credit_limit:,.2f}"],
        ['Current Outstanding:', f"{business.currency_symbol}{customer.current_debt:,.2f}"],
        ['Credit Utilization:', f"{context['credit_utilization']:.1f}%"],
        ['Account Since:', customer.created_at.strftime('%B %d, %Y')],
    ]
    
    customer_table = Table(customer_data, colWidths=[2*inch, 3*inch])
    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 20))
    
    # Outstanding Sales with Items
    if context['outstanding_sales']:
        elements.append(Paragraph("Outstanding Invoices", heading_style))
        
        for sale_data in context['outstanding_sales']:
            sale = sale_data['sale']
            
            # Invoice header
            invoice_header = Paragraph(f"<b>Invoice #{sale.invoice_number}</b> - {sale.created_at.strftime('%B %d, %Y')}", 
                                     ParagraphStyle('InvoiceHeader', parent=normal_style, fontSize=12, spaceAfter=6))
            elements.append(invoice_header)
            
            # Invoice summary
            summary_data = [
                ['Total Amount:', f"{business.currency_symbol}{sale.total_amount:,.2f}"],
                ['Paid Amount:', f"{business.currency_symbol}{sale_data['paid_amount']:,.2f}"],
                ['Remaining:', f"{business.currency_symbol}{sale_data['remaining']:,.2f}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 6))
            
            # Items in this sale
            sale_items = sale.items.all()
            if sale_items:
                items_data = [['Item', 'Qty', 'Unit Price', 'Total']]
                for item in sale_items:
                    items_data.append([
                        item.product.name[:30] + ('...' if len(item.product.name) > 30 else ''),
                        str(item.quantity),
                        f"{business.currency_symbol}{item.unit_price:,.2f}",
                        f"{business.currency_symbol}{(item.quantity * item.unit_price):,.2f}"
                    ])
                
                items_table = Table(items_data, colWidths=[3*inch, 0.7*inch, 1*inch, 1*inch])
                items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                elements.append(items_table)
            
            elements.append(Spacer(1, 15))
        
        elements.append(Spacer(1, 10))
    
    # Payment History (last 10 payments)
    if context['recent_payments']:
        elements.append(Paragraph("Recent Payment History", heading_style))
        
        payment_data = [['Date', 'Amount', 'Method', 'Reference']]
        for payment in context['recent_payments'][:10]:
            payment_data.append([
                payment.created_at.strftime('%m/%d/%Y %H:%M'),
                f"{business.currency_symbol}{payment.amount:,.2f}",
                payment.payment_type.title(),
                payment.payment_reference or 'N/A'
            ])
        
        payment_table = Table(payment_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 2*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(payment_table)
    
    # Build PDF
    doc.build(elements)
    
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="credit_report_{customer.full_name}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    return response