# pos/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'pos'  # Add this line for namespace

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Business setup
    path('business/setup/', views.business_setup, name='business_setup'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='home'),
    
    # POS
    path('sale/', views.pos, name='pos'),
    path('process-sale/', views.process_sale, name='process_sale'),
    path('receipt/<int:sale_id>/', views.get_receipt, name='get_receipt'),
    
    # API endpoints
    path('api/products/', views.api_products, name='api_products'),
    path('api/customer/<int:customer_id>/', views.api_customer, name='api_customer'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/toggle-status/', views.employee_toggle_status, name='employee_toggle_status'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # Sales
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/void/', views.sale_void, name='sale_void'),
    path('sales/<int:pk>/refund/', views.sale_refund, name='sale_refund'),
    
    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/adjust/', views.inventory_adjust, name='inventory_adjust'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Purchases
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/create/', views.purchase_create, name='purchase_create'),
    path('purchases/<int:pk>/add-items/', views.purchase_add_items, name='purchase_add_items'),
    path('purchases/<int:item_id>/edit/', views.purchase_item_edit, name='purchase_item_edit'),
    path('purchases/items/<int:item_id>/delete/', views.purchase_item_delete, name='purchase_item_delete'),
    path('purchases/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('purchases/<int:pk>/receive/', views.purchase_receive, name='purchase_receive'),
    path('purchases/<int:pk>/cancel/', views.purchase_cancel, name='purchase_cancel'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/export-sales/', views.export_sales_report, name='export_sales_report'),
    path('reports/export-inventory/', views.export_inventory_report, name='export_inventory_report'),
    path('reports/vat/', views.vat_report, name='vat_report'),
    path('reports/vat/export/', views.export_vat_report, name='export_vat_report'),
    
    # VAT Management
    path('vat-management/', views.vat_management, name='vat_management'),
    path('vat-management/add-category/', views.add_vat_category, name='add_vat_category'),
    path('vat-management/edit-category/<int:pk>/', views.edit_vat_category, name='edit_vat_category'),
    path('vat-management/delete-category/<int:pk>/', views.delete_vat_category, name='delete_vat_category'),
    
    # Credit Management
    path('credit-management/', views.credit_management, name='credit_management'),
    path('receive-payment/', views.receive_payment, name='receive_payment'),
    
    # Credit Reports
    path('reports/credit/', views.credit_report_overall, name='credit_report_overall'),
    path('reports/credit/customer/<int:customer_id>/', views.credit_report_customer, name='credit_report_customer'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
]