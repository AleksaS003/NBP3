from django.contrib.auth.models import AbstractUser
from djongo import models
from django.db import models as django_models  # Keep this for some fields

class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    # Don't explicitly define id - let Djongo handle it
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
    details = models.JSONField(default=dict, blank=True)  # JSONField works with Djongo
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    description= models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    category = models.CharField(max_length=100)
    stock= models.IntegerField(default=0)
    image_url= models.CharField(max_length=255,blank=True)
    #ugnjezdeni objekat npr za velicinu patika, RAM za laptop...
    specifications = models.JSONField(default=dict, blank=True)

    crated_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='products'
    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='orders')
    items = models.JSONField() #lista proizvoda u trenutku kupovine
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=50,default='Pending')
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table= 'orders'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    
    items = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
    
