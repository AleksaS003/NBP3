from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, ActivityLog, Product, Order, Cart
import json

# Prvo definišemo custom admin class za User model
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('is_admin', 'is_staff', 'is_superuser', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'address', 'is_admin')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'address', 'is_admin')
        }),
    )

# Admin za Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'stock', 'created_at')
    search_fields = ('name', 'description', 'category')
    list_filter = ('category', 'created_at')
    
    def save_model(self, request, obj, form, change):
        # Osiguraj da je specifications JSON string
        if 'specifications' in form.cleaned_data:
            specs = form.cleaned_data['specifications']
            if isinstance(specs, dict):
                obj.specifications = json.dumps(specs)
            elif isinstance(specs, str) and specs:
                try:
                    json.loads(specs)
                    obj.specifications = specs
                except:
                    obj.specifications = json.dumps({})
            else:
                obj.specifications = json.dumps({})
        super().save_model(request, obj, form, change)

# Admin za Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    
    def save_model(self, request, obj, form, change):
        if 'items' in form.cleaned_data:
            items = form.cleaned_data['items']
            if isinstance(items, list):
                obj.items = json.dumps(items)
            elif isinstance(items, str) and items:
                try:
                    json.loads(items)
                    obj.items = items
                except:
                    obj.items = json.dumps([])
            else:
                obj.items = json.dumps([])
        super().save_model(request, obj, form, change)

# Admin za Cart
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    search_fields = ('user__username',)
    
    def save_model(self, request, obj, form, change):
        if 'items' in form.cleaned_data:
            items = form.cleaned_data['items']
            if isinstance(items, list):
                obj.items = json.dumps(items)
            elif isinstance(items, str) and items:
                try:
                    json.loads(items)
                    obj.items = items
                except:
                    obj.items = json.dumps([])
            else:
                obj.items = json.dumps([])
        super().save_model(request, obj, form, change)

# Admin za UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth')
    search_fields = ('user__username', 'user__email', 'bio')
    raw_id_fields = ('user',)

# Admin za ActivityLog
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    readonly_fields = ('timestamp',)

# Registracija modela
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)