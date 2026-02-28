from django.contrib.auth.models import AbstractUser
from djongo import models
from django.db import models as django_models
import json

class User(AbstractUser):
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.username}"

class ActivityLog(models.Model):
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
            try:
                json.loads(data)
                self.specifications = data
            except:
                self.specifications = json.dumps({})
        else:
            self.specifications = json.dumps({})
    
    def get_specifications(self):
        if not self.specifications:
            return {}
        try:
            if isinstance(self.specifications, str):
                return json.loads(self.specifications)
            return self.specifications
        except:
            return {}
    
    def save(self, *args, **kwargs):
        if hasattr(self, 'specifications') and self.specifications:
            if isinstance(self.specifications, dict):
                self.specifications = json.dumps(self.specifications)
        elif not self.specifications:
            self.specifications = '{}'
        super().save(*args, **kwargs)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items = models.TextField(default='[]')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    delivery_address = models.TextField(blank=True)
    delivery_city = models.CharField(max_length=100, blank=True)
    delivery_zip = models.CharField(max_length=20, blank=True)
    delivery_country = models.CharField(max_length=100, blank=True, default='Serbia')
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items = models.TextField(default='[]')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    delivery_address = models.TextField(blank=True)
    delivery_city = models.CharField(max_length=100, blank=True)
    delivery_zip = models.CharField(max_length=20, blank=True)
    delivery_country = models.CharField(max_length=100, blank=True, default='Serbia')
    delivery_notes = models.TextField(blank=True, help_text="Additional delivery instructions")

    class Meta:
        db_table = 'orders'
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def full_address(self):
        parts = [self.delivery_address, self.delivery_city, self.delivery_zip, self.delivery_country]
        return ", ".join([p for p in parts if p])
    
    def set_items(self, items_list):
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
    items = models.TextField(default='[]', blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    def set_items(self, items_list):
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

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='reviews')
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rating from 1 to 5")
    comment = models.TextField(blank=True, help_text="Your review comment")
    
    image_url = models.TextField(blank=True, help_text="Single image URL (legacy)")
    image_urls = models.TextField(default='[]', blank=True, help_text="JSON array of image URLs")
    
    additional_data = models.TextField(default='{}', blank=True, help_text="Additional metadata")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_approved = models.BooleanField(default=True, help_text="Approve this review to show on site")
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username} - {self.rating}★"
    
    def get_image_urls(self):
        if self.image_urls and self.image_urls != '[]':
            try:
                if isinstance(self.image_urls, str):
                    urls = json.loads(self.image_urls)
                    if isinstance(urls, list):
                        return urls
                elif isinstance(self.image_urls, list):
                    return self.image_urls
            except:
                pass
        
        if self.image_url:
            return [self.image_url]
        
        return []
    
    def set_image_urls(self, urls_list):
        if isinstance(urls_list, list):
            self.image_urls = json.dumps(urls_list)
        elif isinstance(urls_list, str):
            try:
                json.loads(urls_list)
                self.image_urls = urls_list
            except:
                self.image_urls = json.dumps([])
        else:
            self.image_urls = json.dumps([])
    
    def get_additional_data(self):
        if not self.additional_data:
            return {}
        try:
            if isinstance(self.additional_data, str):
                return json.loads(self.additional_data)
            return self.additional_data
        except:
            return {}
    
    def save(self, *args, **kwargs):
        if hasattr(self, 'image_urls') and self.image_urls:
            if isinstance(self.image_urls, list):
                self.image_urls = json.dumps(self.image_urls)
        elif not self.image_urls:
            self.image_urls = '[]'
            
        if hasattr(self, 'additional_data') and self.additional_data:
            if isinstance(self.additional_data, dict):
                self.additional_data = json.dumps(self.additional_data)
        elif not self.additional_data:
            self.additional_data = '{}'
            
        super().save(*args, **kwargs)
    
    @property
    def formatted_created_at(self):
        return self.created_at.strftime("%B %d, %Y")
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()