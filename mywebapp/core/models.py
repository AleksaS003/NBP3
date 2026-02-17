from django.contrib.auth.models import AbstractUser
from djongo import models
from django.db import models as django_models
import json

class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    is_admin = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    """Additional user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.username}"

class ActivityLog(models.Model):
    """Track user activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    image_url = models.CharField(max_length=255, blank=True)
    
    # PROMENA: Umesto JSONField koristimo TextField
    specifications = models.TextField(default='{}', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'
    
    def __str__(self):
        return self.name
    
    def set_specifications(self, data):
        """Čuva dict kao JSON string"""
        if isinstance(data, dict):
            self.specifications = json.dumps(data)
        elif isinstance(data, str):
            # Proveri da li je već JSON string
            try:
                json.loads(data)
                self.specifications = data
            except:
                self.specifications = json.dumps({})
        else:
            self.specifications = json.dumps({})
    
    def get_specifications(self):
        """Vraća specifications kao dict"""
        if not self.specifications:
            return {}
        try:
            if isinstance(self.specifications, str):
                return json.loads(self.specifications)
            return self.specifications
        except:
            return {}
    
    def save(self, *args, **kwargs):
        # Osiguraj da je specifications uvek JSON string
        if hasattr(self, 'specifications') and self.specifications:
            if isinstance(self.specifications, dict):
                self.specifications = json.dumps(self.specifications)
        elif not self.specifications:
            self.specifications = '{}'
        super().save(*args, **kwargs)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    # PROMENA: Umesto JSONField koristimo TextField
    items = models.TextField(default='[]')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
    def set_items(self, items_list):
        """Čuva listu kao JSON string"""
        if isinstance(items_list, list):
            self.items = json.dumps(items_list)
        elif isinstance(items_list, str):
            try:
                json.loads(items_list)
                self.items = items_list
            except:
                self.items = json.dumps([])
        else:
            self.items = json.dumps([])
    
    def get_items(self):
        """Vraća items kao listu"""
        if not self.items:
            return []
        try:
            if isinstance(self.items, str):
                return json.loads(self.items)
            return self.items
        except:
            return []
    
    def save(self, *args, **kwargs):
        if hasattr(self, 'items') and self.items:
            if isinstance(self.items, list):
                self.items = json.dumps(self.items)
        elif not self.items:
            self.items = '[]'
        super().save(*args, **kwargs)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    # PROMENA: Umesto JSONField koristimo TextField
    items = models.TextField(default='[]', blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def set_items(self, items_list):
        """Čuva listu kao JSON string"""
        if isinstance(items_list, list):
            self.items = json.dumps(items_list)
        elif isinstance(items_list, str):
            try:
                json.loads(items_list)
                self.items = items_list
            except:
                self.items = json.dumps([])
        else:
            self.items = json.dumps([])
    
    def get_items(self):
        """Vraća items kao listu"""
        if not self.items:
            return []
        try:
            if isinstance(self.items, str):
                return json.loads(self.items)
            return self.items
        except:
            return []
    
    def save(self, *args, **kwargs):
        if hasattr(self, 'items') and self.items:
            if isinstance(self.items, list):
                self.items = json.dumps(self.items)
        elif not self.items:
            self.items = '[]'
        super().save(*args, **kwargs)