import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CheckoutForm
from .models import Cart, Order, User, ActivityLog, UserProfile, Product
from django.contrib.admin.views.decorators import staff_member_required

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
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'title': 'Dashboard',
        'user': request.user,
        'recent_activities': recent_activities,
        'recent_orders': recent_orders,
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
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_activities = ActivityLog.objects.all()[:20]
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    context = {
        'title': 'Admin Dashboard',
        'total_users': total_users,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_users': recent_users,
        'recent_activities': recent_activities,
        'recent_orders': recent_orders,
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
        user_orders = Order.objects.filter(user=user).order_by('-created_at')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_users')
    
    context = {
        'title': f'User Details: {user.username}',
        'view_user': user,
        'user_activities': user_activities,
        'user_orders': user_orders,
    }
    return render(request, 'core/admin_user_detail.html', context)

# Product views
def product_list(request):
    products = Product.objects.all()
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    context = {
        'title': 'Shop',
        'products': products,
        'categories': sorted([c for c in categories if c]),
    }
    return render(request, 'core/product_list.html', context)

def product_detail(request, product_id):
    """Show product details"""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('product_list')
    
    context = {
        'title': product.name,
        'product': product,
    }
    return render(request, 'core/product_detail.html', context)

@staff_member_required
def admin_add_product(request):
    """Admin view for adding new products with dynamic category selection"""
    # Dohvati sve postojeće kategorije iz baze
    existing_categories = Product.objects.values_list('category', flat=True).distinct()
    # Ukloni None i prazne stringove, sortiraj
    existing_categories = sorted([cat for cat in existing_categories if cat])
    
    if request.method == 'POST':
        # Prikupi podatke iz forme
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category = request.POST.get('category')
        new_category = request.POST.get('new_category', '').strip()
        stock = request.POST.get('stock', 0)
        image_url = request.POST.get('image_url', '')
        specifications = request.POST.get('specifications', '{}')
        
        # Ako je uneta nova kategorija, koristi nju
        if new_category:
            category = new_category
        
        # Validacija
        errors = []
        if not name:
            errors.append("Product name is required.")
        if not price:
            errors.append("Price is required.")
        if not category:
            errors.append("Category is required.")
        
        if not errors:
            try:
                # Kreiraj novi proizvod
                product = Product.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    category=category,
                    stock=int(stock) if stock else 0,
                    image_url=image_url,
                    specifications=specifications
                )
                messages.success(request, f'Product "{product.name}" created successfully!')
                return redirect('product_list')
            except Exception as e:
                messages.error(request, f'Error creating product: {str(e)}')
        else:
            for error in errors:
                messages.error(request, error)
    
    context = {
        'title': 'Add New Product',
        'existing_categories': existing_categories,
    }
    return render(request, 'core/admin_add_product.html', context)

# Cart views
@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Učitaj trenutne items iz korpe (JSON string -> list)
    if cart.items:
        try:
            items = json.loads(cart.items)
        except json.JSONDecodeError:
            items = []
    else:
        items = []
    
    # Proveri da li proizvod već postoji u korpi
    found = False
    for i, item in enumerate(items):
        if isinstance(item, dict) and item.get('product_id') == product_id:
            items[i]['quantity'] = items[i].get('quantity', 0) + 1
            found = True
            break
    
    # Ako ne postoji, dodaj novi
    if not found:
        items.append({
            'product_id': product_id,
            'quantity': 1,
            'name': product.name,
            'price': str(product.price)
        })
    
    # Sačuvaj nazad kao JSON string
    cart.items = json.dumps(items)
    cart.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('product_list')

@login_required
def view_cart(request):
    """View cart contents"""
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    cart_items = []
    total = 0
    
    # Učitaj items iz korpe
    if cart.items:
        try:
            items = json.loads(cart.items)
            for item in items:
                if isinstance(item, dict) and 'product_id' in item:
                    try:
                        product = Product.objects.get(id=item['product_id'])
                        price = float(str(product.price))
                        item_total = price * item['quantity']
                        total += item_total
                        cart_items.append({
                            'product': product,
                            'quantity': item['quantity'],
                            'item_total': item_total
                        })
                    except Product.DoesNotExist:
                        continue
        except (json.JSONDecodeError, ValueError):
            pass
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart': cart
    }
    return render(request, 'core/cart.html', context)

@login_required
def remove_from_cart(request, product_id):
    """Remove item from cart"""
    try:
        cart = Cart.objects.get(user=request.user)
        
        if cart.items:
            try:
                items = json.loads(cart.items)
                # Filtriraj items (ukloni onaj sa datim product_id)
                items = [item for item in items if item.get('product_id') != product_id]
                cart.items = json.dumps(items)
                cart.save()
                messages.success(request, "Item removed from cart.")
            except json.JSONDecodeError:
                pass
    except Cart.DoesNotExist:
        pass
    
    return redirect('view_cart')

@login_required
def update_cart_quantity(request, product_id):
    """Update quantity of item in cart"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            cart = Cart.objects.get(user=request.user)
            
            if cart.items:
                try:
                    items = json.loads(cart.items)
                    for i, item in enumerate(items):
                        if item.get('product_id') == product_id:
                            if quantity > 0:
                                items[i]['quantity'] = quantity
                            else:
                                items.pop(i)
                            break
                    
                    cart.items = json.dumps(items)
                    cart.save()
                except json.JSONDecodeError:
                    pass
        except Cart.DoesNotExist:
            pass
    
    return redirect('view_cart')

@login_required
def checkout(request):
    """Checkout page - enter delivery information"""
    try:
        cart = Cart.objects.get(user=request.user)
        
        if not cart.items:
            messages.error(request, "Your cart is empty.")
            return redirect('product_list')
        
        try:
            items = json.loads(cart.items)
        except json.JSONDecodeError:
            messages.error(request, "Error processing cart.")
            return redirect('view_cart')
        
        if not items:
            messages.error(request, "Your cart is empty.")
            return redirect('product_list')
        
        # Izračunaj total za prikaz
        total_price = 0
        cart_items = []
        for item in items:
            try:
                product = Product.objects.get(id=item['product_id'])
                price = float(str(product.price))
                item_total = price * item['quantity']
                total_price += item_total
                cart_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'price': price,
                    'total': item_total
                })
            except (Product.DoesNotExist, ValueError):
                continue
        
        if request.method == 'POST':
            form = CheckoutForm(request.POST)
            if form.is_valid():
                # Pripremi order items za čuvanje
                order_items = []
                for item in items:
                    try:
                        product = Product.objects.get(id=item['product_id'])
                        price = float(str(product.price))
                        order_items.append({
                            'product_id': product.id,
                            'product_name': product.name,
                            'quantity': item['quantity'],
                            'price_at_purchase': price,
                            'total': price * item['quantity']
                        })
                    except Product.DoesNotExist:
                        continue
                
                if order_items:
                    # Kreiraj order sa podacima iz forme
                    order = Order.objects.create(
                        user=request.user,
                        items=json.dumps(order_items),
                        total_price=total_price,
                        status='Pending',
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        phone_number=form.cleaned_data['phone_number'],
                        delivery_address=form.cleaned_data['delivery_address'],
                        delivery_city=form.cleaned_data['delivery_city'],
                        delivery_zip=form.cleaned_data['delivery_zip'],
                        delivery_country=form.cleaned_data['delivery_country'],
                        delivery_notes=form.cleaned_data.get('delivery_notes', '')
                    )
                    
                    # Sačuvaj podatke u user profil ako je označeno
                    if form.cleaned_data.get('save_info'):
                        user = request.user
                        user.first_name = form.cleaned_data['first_name']
                        user.last_name = form.cleaned_data['last_name']
                        user.phone_number = form.cleaned_data['phone_number']
                        user.address = form.cleaned_data['delivery_address']
                        user.save()
                    
                    # Očisti korpu
                    cart.items = json.dumps([])
                    cart.save()
                    
                    messages.success(request, f"Order #{order.id} placed successfully!")
                    return redirect('order_confirmation', order_id=order.id)
                else:
                    messages.error(request, "No valid items in cart.")
        else:
            # Pre-popuni formu sa podacima iz user profila
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone_number': request.user.phone_number,
                'email': request.user.email,
                'delivery_address': request.user.address,
                'delivery_country': 'Serbia',
            }
            form = CheckoutForm(initial=initial_data)
        
        context = {
            'form': form,
            'cart_items': cart_items,
            'total': total_price,
        }
        return render(request, 'core/checkout.html', context)
            
    except Cart.DoesNotExist:
        messages.error(request, "Cart not found.")
        return redirect('product_list')

@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order_items = json.loads(order.items) if order.items else []
        
        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'core/order_confirmation.html', context)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('dashboard')