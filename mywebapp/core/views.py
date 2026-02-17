from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import Cart, Order, User, ActivityLog, UserProfile, Product

# Public views
def home(request):
    """Home page view"""
    context = {
        'title': 'Welcome to My Web App',
    }
    return render(request, 'core/home.html', context)

def about(request):
    """About page view"""
    context = {
        'title': 'About Us',
    }
    return render(request, 'core/about.html', context)

def contact(request):
    """Contact page view"""
    context = {
        'title': 'Contact Us',
    }
    return render(request, 'core/contact.html', context)

# Authentication views
def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the activity
            ActivityLog.objects.create(
                user=user,
                action='User registered',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'title': 'Register',
        'form': form,
    }
    return render(request, 'core/register.html', context)

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Log the activity
                ActivityLog.objects.create(
                    user=user,
                    action='User logged in',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    
    context = {
        'title': 'Login',
        'form': form,
    }
    return render(request, 'core/login.html', context)

def logout_view(request):
    """User logout view"""
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action='User logged out',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# Protected views (require login)
@login_required
def dashboard(request):
    """User dashboard view"""
    recent_activities = ActivityLog.objects.filter(user=request.user)[:10]
    
    context = {
        'title': 'Dashboard',
        'user': request.user,
        'recent_activities': recent_activities,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def profile(request):
    """User profile view"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'title': 'My Profile',
        'form': form,
        'user': request.user,
    }
    return render(request, 'core/profile.html', context)

@login_required
def profile_edit(request):
    """Edit user profile view"""
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.address = request.POST.get('address', user.address)
        user.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    
    context = {
        'title': 'Edit Profile',
        'user': request.user,
    }
    return render(request, 'core/profile_edit.html', context)

# Admin views
@staff_member_required
def admin_dashboard(request):
    """Admin dashboard view"""
    total_users = User.objects.count()
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_activities = ActivityLog.objects.all()[:20]
    
    context = {
        'title': 'Admin Dashboard',
        'total_users': total_users,
        'recent_users': recent_users,
        'recent_activities': recent_activities,
    }
    return render(request, 'core/admin_dashboard.html', context)

@staff_member_required
def admin_users(request):
    """Admin user management view"""
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'title': 'Manage Users',
        'users': users,
    }
    return render(request, 'core/admin_users.html', context)

@staff_member_required
def admin_user_detail(request, user_id):
    """Admin view user details"""
    try:
        user = User.objects.get(id=user_id)
        user_activities = ActivityLog.objects.filter(user=user)[:20]
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_users')
    
    context = {
        'title': f'User Details: {user.username}',
        'view_user': user,
        'user_activities': user_activities,
    }
    return render(request, 'core/admin_user_detail.html', context)


def product_list(request):
    products= Product.objects.all()
    context = {
        'title': 'Shop',
        'products': products,
    }
    return render(request, 'core/product_list.html',context)

def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('product_list')
    context = {
        'title': product.name,
        'product': product,
    }
    return render(request,'core/product_detail.html',context)

def add_to_cart(request, product_id):
    
    cart, created = Cart.objects.get_or_create(user=request.user)

    items = cart.items
    found = False
    
    for item in items:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            found = True
            break
            
    if not found:
        items.append({'product_id': product_id, 'quantity': 1})
    
    cart.items = items
    cart.save()
    messages.success(request, "Added to permanent cart!")
    return redirect('product_list')

def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
        
    cart_items = []
    total = 0
    
    for item in cart.items:
        product = Product.objects.get(id=item['product_id'])
        item_total = product.price * item['quantity']
        total += item_total
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'item_total': item_total
        })
        
    return render(request, 'core/cart.html', {'cart_items': cart_items, 'total': total})

def remove_from_cart(request, product_id):
    try:
        cart = Cart.objects.get(user=request.user)
        
        cart.items = [item for item in cart.items if item['product_id'] != product_id]
        cart.save()
        messages.success(request, "Item removed from your permanent cart.")
    except Cart.DoesNotExist:
        pass 
        
    return redirect('view_cart')

def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items:
            messages.error(request, "Your cart is empty.")
            return redirect('product_list')

   
        total_price = 0
        order_items = []
        for item in cart.items:
            product = Product.objects.get(id=item['product_id'])
            item_total = product.price * item['quantity']
            total_price += item_total
          
            order_items.append({
                'product_name': product.name,
                'quantity': item['quantity'],
                'price_at_purchase': float(product.price)
            })

        
        Order.objects.create(
            user=request.user,
            items=order_items,
            total_price=total_price,
            status='Pending'
        )

      
        cart.items = []
        cart.save()

        messages.success(request, "Order placed successfully!")
        return redirect('dashboard')
        
    except Cart.DoesNotExist:
        return redirect('product_list')