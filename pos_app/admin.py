from django.contrib import admin
from .models import Business

class BusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'business_type', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username')  # Allows searching by business name and owner's username

admin.site.register(Business, BusinessAdmin)