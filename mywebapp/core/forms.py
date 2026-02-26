from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, UserProfile
from .models import Order

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'address', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'date_of_birth')


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True, label='First Name')
    last_name = forms.CharField(max_length=100, required=True, label='Last Name')
    phone_number = forms.CharField(max_length=20, required=True, label='Phone Number')
    email = forms.EmailField(required=False, label='Email (optional)')
    
    delivery_address = forms.CharField(max_length=255, required=True, label='Address')
    delivery_city = forms.CharField(max_length=100, required=True, label='City')
    delivery_zip = forms.CharField(max_length=20, required=True, label='ZIP/Postal Code')
    delivery_country = forms.CharField(max_length=100, required=True, initial='Serbia', label='Country')
    
    delivery_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Delivery Notes (optional)',
        help_text='Additional instructions for delivery'
    )
    
    save_info = forms.BooleanField(
        required=False,
        initial=True,
        label='Save this information for future orders'
    )
    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        import re
        if not re.match(r'^[\d\s\+\-]{6,20}$', phone):
            raise forms.ValidationError('Enter a valid phone number')
        return phone
    
class ReviewForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, f"{i} ★") for i in range(1, 6)],
        widget=forms.RadioSelect,
        required=True,
        label="Your Rating"
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this product...'}),
        required=False,
        label="Your Review"
    )
    image_urls = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Enter image URLs (one per line)'
        }),
        required=False,
        label="Product Images (optional)",
        help_text="Add links to your product photos, one per line"
    )
    
    def clean_image_urls(self):
        urls_text = self.cleaned_data.get('image_urls', '')
        if not urls_text:
            return []
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        import re
        url_pattern = re.compile(r'^https?://\S+$')
        valid_urls = []
        for url in urls:
            if url_pattern.match(url):
                valid_urls.append(url)
            else:
                raise forms.ValidationError(f"Invalid URL: {url}")
        
        return valid_urls