# pos_app/api.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, Customer, Sale, SaleItem, Inventory
import json

@login_required
@csrf_exempt
def search_products(request):
    """Search products by name, SKU or barcode"""
    if request.method == 'GET':
        query = request.GET.get('query', '')
        business_id = request.GET.get('business_id')
        
        if not query or not business_id:
            return JsonResponse({'products': []})
        
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(sku__icontains=query) | 
            Q(barcode__icontains=query),
            business_id=business_id,
            is_active=True
        )[:10]
        
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'barcode': product.barcode,
                'price': float(product.selling_price),
                'stock': product.stock_quantity,
                'category': product.category.name if product.category else 'Uncategorized',
            })
        
        return JsonResponse({'products': products_data})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
@csrf_exempt
def get_product(request, product_id):
    """Get product details by ID"""
    if request.method == 'GET':
        try:
            product = Product.objects.get(id=product_id)
            
            # Check if user has access to this product
            from .views import get_business_for_user
            business = get_business_for_user(request.user)
            if product.business != business:
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            product_data = {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'barcode': product.barcode,
                'price': float(product.selling_price),
                'stock': product.stock_quantity,
                'category': product.category.name if product.category else 'Uncategorized',
            }
            
            return JsonResponse(product_data)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
@csrf_exempt
def search_customers(request):
    """Search customers by name, email or phone"""
    if request.method == 'GET':
        query = request.GET.get('query', '')
        business_id = request.GET.get('business_id')
        
        if not query or not business_id:
            return JsonResponse({'customers': []})
        
        customers = Customer.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(phone__icontains=query),
            business_id=business_id
        )[:10]
        
        customers_data = []
        for customer in customers:
            customers_data.append({
                'id': customer.id,
                'name': f"{customer.first_name} {customer.last_name}",
                'email': customer.email,
                'phone': customer.phone,
                'loyalty_points': float(customer.loyalty_points),
            })
        
        return JsonResponse({'customers': customers_data})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
@csrf_exempt
def get_customer(request, customer_id):
    """Get customer details by ID"""
    if request.method == 'GET':
        try:
            customer = Customer.objects.get(id=customer_id)
            
            # Check if user has access to this customer
            from .views import get_business_for_user
            business = get_business_for_user(request.user)
            if customer.business != business:
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            customer_data = {
                'id': customer.id,
                'name': f"{customer.first_name} {customer.last_name}",
                'email': customer.email,
                'phone': customer.phone,
                'loyalty_points': float(customer.loyalty_points),
            }
            
            return JsonResponse(customer_data)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Customer not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)