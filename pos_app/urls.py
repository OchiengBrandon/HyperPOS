# pos_app/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

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
    path('pos/', views.pos, name='pos'),
    path('pos/process-sale/', views.process_sale, name='process_sale'),
    path('pos/receipt/<int:sale_id>/', views.get_receipt, name='get_receipt'),
    
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
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),  # Added delete URL

    
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
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
]