from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cart, User, UserProfile, ActivityLog, Product, Order

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_staff', 'date_joined')
    list_filter = ('is_admin', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_admin', 'phone_number', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('is_admin', 'phone_number', 'address')}),
    )

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth')
    search_fields = ('user__username', 'user__email')

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action')
    readonly_fields = ('timestamp',)

class ProductAdmin(admin.ModelAdmin):
    list_display=('name', 'price', 'category', 'stock')
    search_fields = ('name', 'category')

class OrderAdmin(admin.ModelAdmin):
    list_display=('id', 'user', 'total_price', 'status', 'created_at')

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    readonly_fields = ('user', 'items', 'updated_at')

# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart,CartAdmin)