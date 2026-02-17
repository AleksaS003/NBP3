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
    
    # Popravljeno: JSONField sa odgovarajućim default-om i validacijom
    specifications = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validacija i konverzija specifications polja"""
        if isinstance(self.specifications, str):
            try:
                self.specifications = json.loads(self.specifications)
            except json.JSONDecodeError:
                self.specifications = {}
        elif self.specifications is None:
            self.specifications = {}
        elif not isinstance(self.specifications, (dict, list)):
            self.specifications = {}
    
    def save(self, *args, **kwargs):
        """Pozovi clean pre save-a"""
        self.clean()
        super().save(*args, **kwargs)
    
    def get_specifications_dict(self):
        """Pomoćna metoda za bezbedno dohvatanje specifikacija"""
        if isinstance(self.specifications, dict):
            return self.specifications
        return {}

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    # Popravljeno: Dodat default=list
    items = models.JSONField(default=list)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
    def clean(self):
        """Validacija items polja"""
        if isinstance(self.items, str):
            try:
                self.items = json.loads(self.items)
            except json.JSONDecodeError:
                self.items = []
        elif self.items is None:
            self.items = []
        elif not isinstance(self.items, list):
            self.items = [self.items] if self.items else []
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def get_items_list(self):
        """Pomoćna metoda za bezbedno dohvatanje items-a"""
        if isinstance(self.items, list):
            return self.items
        return []

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    # Ovo je već bilo dobro
    items = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def clean(self):
        """Validacija items polja"""
        if isinstance(self.items, str):
            try:
                self.items = json.loads(self.items)
            except json.JSONDecodeError:
                self.items = []
        elif self.items is None:
            self.items = []
        elif not isinstance(self.items, list):
            self.items = [self.items] if self.items else []
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def get_items_list(self):
        """Pomoćna metoda za bezbedno dohvatanje items-a"""
        if isinstance(self.items, list):
            return self.items
        return []