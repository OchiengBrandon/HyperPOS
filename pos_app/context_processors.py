# pos_app/context_processors.py
from .models import Business

def business_settings(request):
    """Add business settings to context for all templates"""
    if request.user.is_authenticated:
        try:
            # If user is a business owner
            business = Business.objects.filter(owner=request.user).first()
            if not business:
                # If user is an employee
                from .models import Employee
                employee = Employee.objects.filter(user=request.user, is_active=True).first()
                if employee:
                    business = employee.business
            
            if business:
                return {
                    'business_settings': business.settings,
                }
        except:
            pass
    
    return {}