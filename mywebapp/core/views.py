import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CheckoutForm, ReviewForm
from .models import Cart, Order, User, ActivityLog, UserProfile, Product, Review
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from .models import Cart, Order, User, ActivityLog, UserProfile, Product, Review, ContactMessage

def home(request):
    context = {
        'title': 'Welcome to Shongo ',
    }
    return render(request, 'core/home.html', context)

def about(request):
    context = {
        'title': 'About Us',
    }
    return render(request, 'core/about.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            try:
                contact_message = ContactMessage(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                if request.user.is_authenticated:
                    contact_message.user = request.user
                
                contact_message.save()
                
                messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
                return redirect('contact')
            except Exception as e:
                messages.error(request, 'There was an error sending your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {
        'title': 'Contact Us',
    }
    return render(request, 'core/contact.html', context)

@staff_member_required
def admin_contact_messages(request):
    from django.db import connection
    db = connection.cursor().db_conn
    
    filter_status = request.GET.get('filter', 'all')
    
    mongo_filter = {}
    if filter_status == 'unread':
        mongo_filter['is_read'] = False
    elif filter_status == 'read':
        mongo_filter['is_read'] = True
    
    messages_cursor = db.contact_messages.find(mongo_filter).sort('created_at', -1)
    messages_list = list(messages_cursor)
    
    for msg in messages_list:
        msg['id'] = str(msg['_id'])  # Konvertuj ObjectId u string
        if msg.get('user_id'):
            user = db.users.find_one({'_id': msg['user_id']})
            if user:
                msg['user'] = user
    
    total_messages = db.contact_messages.count_documents({})
    unread_count = db.contact_messages.count_documents({'is_read': False})
    
    context = {
        'title': 'Contact Messages',
        'messages': messages_list,
        'total_messages': total_messages,
        'unread_count': unread_count,
        'current_filter': filter_status,
    }
    return render(request, 'core/admin_contact_messages.html', context)

@staff_member_required
def admin_contact_message_detail(request, message_id):
    from django.db import connection
    from bson.objectid import ObjectId
    db = connection.cursor().db_conn
    
    message = db.contact_messages.find_one({'_id': ObjectId(message_id)})
    
    if not message:
        messages.error(request, 'Message not found.')
        return redirect('admin_contact_messages')
    
    db.contact_messages.update_one(
        {'_id': ObjectId(message_id)},
        {'$set': {'is_read': True}}
    )
    message['is_read'] = True
    message['id'] = str(message['_id'])
    
    if message.get('user_id'):
        user = db.users.find_one({'_id': message['user_id']})
        if user:
            message['user'] = user
    
    context = {
        'title': f'Message from {message.get("name")}',
        'message': message,
    }
    return render(request, 'core/admin_contact_message_detail.html', context)

@staff_member_required
def admin_contact_message_delete(request, message_id):
    if request.method == 'POST':
        from django.db import connection
        from bson.objectid import ObjectId
        db = connection.cursor().db_conn
        
        db.contact_messages.delete_one({'_id': ObjectId(message_id)})
        messages.success(request, 'Message deleted successfully.')
    
    return redirect('admin_contact_messages')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
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
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action='User logged out',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def dashboard(request):
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

@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_activities = ActivityLog.objects.all()[:20]
    recent_orders = Order.objects.all().order_by('-created_at')[:10]

    collection = connection.cursor().db_conn.order

    revenue_pipeline = [
        {
            "$group": {
                "_id": None,
                "totalRevenue": {"$sum": "$total_price"},
                "totalOrders": {"$sum": 1}
            }
        }
    ]

    revenue_result = list(collection.aggregate(revenue_pipeline))

    total_revenue = 0
    total_orders = 0

    if revenue_result:
        total_revenue = revenue_result[0].get("totalRevenue", 0)
        total_orders = revenue_result[0].get("totalOrders", 0)

    daily_pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "dailyRevenue": {"$sum": "$total_price"},
                "orders": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]

    daily_data = list(collection.aggregate(daily_pipeline))

    formatted_daily_data = []

    for item in daily_data:
        formatted_daily_data.append({
            "date": item.get("_id"),
            "dailyRevenue": item.get("dailyRevenue", 0),
            "orders": item.get("orders", 0),
        })

    daily_data = formatted_daily_data

    context = {
        'title': 'Admin Dashboard',
        'total_users': total_users,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_users': recent_users,
        'recent_activities': recent_activities,
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'daily_data': daily_data,
    }

    return render(request, 'core/admin_dashboard.html', context)

@staff_member_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'title': 'Manage Users',
        'users': users,
    }
    return render(request, 'core/admin_users.html', context)

@staff_member_required
def admin_user_detail(request, user_id):
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

def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        has_purchased = False
        can_review = False
        user_review = None
        
        if request.user.is_authenticated:
            orders = Order.objects.filter(user=request.user)
            for order in orders:
                try:
                    items = json.loads(order.items)
                    for item in items:
                        if item.get('product_id') == product_id:
                            has_purchased = True
                            break
                    if has_purchased:
                        break
                except:
                    continue
            
            try:
                user_review = Review.objects.filter(product=product, user=request.user).first()
            except:
                user_review = None
                
            can_review = has_purchased and (user_review is None)
        
        from django.db import connection
        db = connection.cursor().db_conn
        
        pipeline_avg = [
            {"$match": {"product_id": product_id, "is_approved": True}},
            {
                "$group": {
                    "_id": None,
                    "average_rating": {"$avg": "$rating"},
                    "total_reviews": {"$sum": 1},
                    "rating_counts": {"$push": "$rating"}
                }
            }
        ]
        
        avg_result = list(db.reviews.aggregate(pipeline_avg))
        
        avg_rating = 0
        total_reviews = 0
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        if avg_result and len(avg_result) > 0:
            avg_rating = round(avg_result[0].get('average_rating', 0), 1)
            total_reviews = avg_result[0].get('total_reviews', 0)
            
            if 'rating_counts' in avg_result[0]:
                for r in avg_result[0]['rating_counts']:
                    if r in rating_distribution:
                        rating_distribution[r] += 1

        reviews_cursor = db.reviews.find({
            "product_id": product_id,
            "is_approved": True
        }).sort("created_at", -1)
        
        reviews_data = list(reviews_cursor)
        
        reviews_list = []
        for review in reviews_data:
            user_id = review.get('user_id')
            username = "Unknown User"
            
            if user_id:
                user_data = db.users.find_one({"_id": user_id})
                if user_data:
                    username = user_data.get('username', 'Unknown User')
            
            image_urls = []
            if review.get('image_urls'):
                try:
                    if isinstance(review['image_urls'], str):
                        image_urls = json.loads(review['image_urls'])
                    elif isinstance(review['image_urls'], list):
                        image_urls = review['image_urls']
                except:
                    image_urls = []
            elif review.get('image_url'):
                image_urls = [review['image_url']]
            
            created_at = review.get('created_at')
            if created_at:
                if hasattr(created_at, 'strftime'):
                    formatted_date = created_at.strftime("%B %d, %Y")
                else:
                    formatted_date = str(created_at)[:10]
            else:
                formatted_date = "Unknown date"
            
            reviews_list.append({
                'id': str(review.get('_id')),
                'user': {
                    'username': username
                },
                'rating': review.get('rating', 0),
                'comment': review.get('comment', ''),
                'image_urls': image_urls,
                'created_at': formatted_date,
                'can_edit': request.user.is_authenticated and str(review.get('user_id')) == str(request.user.id)
            })
        
        context = {
            'title': product.name,
            'product': product,
            'reviews': reviews_list,
            'avg_rating': avg_rating,
            'total_reviews': total_reviews,
            'rating_distribution': rating_distribution,
            'has_purchased': has_purchased,
            'can_review': can_review,
            'user_review': user_review,
        }
        
        return render(request, 'core/product_detail.html', context)
        
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('product_list')
    except Exception as e:
        print(f"Error in product_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        
        context = {
            'title': product.name if 'product' in locals() else 'Product',
            'product': product if 'product' in locals() else None,
            'reviews': [],
            'avg_rating': 0,
            'total_reviews': 0,
            'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'has_purchased': False,
            'can_review': False,
            'user_review': None,
        }
        return render(request, 'core/product_detail.html', context)

def product_list(request):
    """List all products with advanced filtering"""
    products = Product.objects.all()
    
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        try:
            min_price_float = float(min_price)
            all_products = []
            for p in products:
                if float(str(p.price)) >= min_price_float:
                    all_products.append(p.id)
            products = products.filter(id__in=all_products)
        except ValueError:
            pass
    
    if max_price:
        try:
            max_price_float = float(max_price)
            all_products = []
            for p in products:
                if float(str(p.price)) <= max_price_float:
                    all_products.append(p.id)
            products = products.filter(id__in=all_products)
        except ValueError:
            pass

    spec_filters = {}

    for key in request.GET:
        if key.startswith('spec_'):
            spec_key = key[5:]
            spec_filters[spec_key] = request.GET.getlist(key)

    if spec_filters:
        filtered_products = []

        for product in products:
            specs = product.get_specifications()
            match = True

            for key, values in spec_filters.items():
                if key not in specs or str(specs[key]) not in values:
                    match = False
                    break

            if match:
                filtered_products.append(product.id)

        products = products.filter(id__in=filtered_products)


    selected_flat = []

    for key, values in spec_filters.items():
        for v in values:
            selected_flat.append(f"{key}:{v}")
    
    categories = Product.objects.values_list('category', flat=True).distinct()
    categories = sorted([c for c in categories if c])
    
    all_specs = {}
    for product in Product.objects.all():
        specs = product.get_specifications()
        for key, value in specs.items():
            if key not in all_specs:
                all_specs[key] = set()
            all_specs[key].add(str(value))
    
    for key in all_specs:
        all_specs[key] = sorted(list(all_specs[key]))
    
    context = {
        'title': 'Shop',
        'products': products,
        'categories': categories,
        'all_specs': all_specs,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'selected_flat': selected_flat,
    }
    return render(request, 'core/product_list.html', context)

@login_required
def delete_review(request, review_id):
    try:
        from bson.objectid import ObjectId
        
        from django.db import connection
        db = connection.cursor().db_conn
        
        review = db.reviews.find_one({
            "_id": ObjectId(review_id),
            "user_id": request.user.id
        })
        
        if not review:
            messages.error(request, 'Review not found or you do not have permission to delete it.')
            return redirect('product_list')
        
        product_id = review.get('product_id')
        
        if request.method == 'POST':
            db.reviews.delete_one({"_id": ObjectId(review_id)})
            
            try:
                Review.objects.filter(id=int(review_id) if review_id.isdigit() else None).delete()
            except:
                pass
                
            messages.success(request, 'Your review has been deleted.')
        
        return redirect('product_detail', product_id=product_id)
        
    except Exception as e:
        print(f"Error deleting review: {str(e)}")
        messages.error(request, f'Error deleting review: {str(e)}')
        return redirect('product_list')

@staff_member_required
def admin_add_product(request):
    """Admin view for adding new products with dynamic category selection"""
    existing_categories = Product.objects.values_list('category', flat=True).distinct()
    existing_categories = sorted([cat for cat in existing_categories if cat])
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category = request.POST.get('category')
        new_category = request.POST.get('new_category', '').strip()
        stock = request.POST.get('stock', 0)
        image_url = request.POST.get('image_url', '')
        specifications = request.POST.get('specifications', '{}')
        
        if new_category:
            category = new_category
        
        errors = []
        if not name:
            errors.append("Product name is required.")
        if not price:
            errors.append("Price is required.")
        if not category:
            errors.append("Category is required.")
        
        if not errors:
            try:
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

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if cart.items:
        try:
            items = json.loads(cart.items)
        except json.JSONDecodeError:
            items = []
    else:
        items = []
    
    found = False
    for i, item in enumerate(items):
        if isinstance(item, dict) and item.get('product_id') == product_id:
            items[i]['quantity'] = items[i].get('quantity', 0) + 1
            found = True
            break

    if not found:
        items.append({
            'product_id': product_id,
            'quantity': 1,
            'name': product.name,
            'price': str(product.price)
        })
    
    cart.items = json.dumps(items)
    cart.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('product_list')

@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    cart_items = []
    total = 0
    
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
                    
                    if form.cleaned_data.get('save_info'):
                        user = request.user
                        user.first_name = form.cleaned_data['first_name']
                        user.last_name = form.cleaned_data['last_name']
                        user.phone_number = form.cleaned_data['phone_number']
                        user.address = form.cleaned_data['delivery_address']
                        user.save()
                    
                    cart.items = json.dumps([])
                    cart.save()
                    
                    messages.success(request, f"Order #{order.id} placed successfully!")
                    return redirect('order_confirmation', order_id=order.id)
                else:
                    messages.error(request, "No valid items in cart.")
        else:
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
    
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    orders = Order.objects.filter(
        user=request.user,
        status__in=['Pending', 'Completed', 'Delivered']
    )
    
    has_purchased = False
    purchased_order = None
    
    for order in orders:
        try:
            items = json.loads(order.items)
            for item in items:
                if str(item.get('product_id')) == str(product_id) or item.get('product_id') == product_id:
                    has_purchased = True
                    purchased_order = order
                    break
            if has_purchased:
                break
        except:
            continue
    
    existing_review = None
    try:
        existing_reviews = Review.objects.filter(product=product, user=request.user)
        if existing_reviews.exists():
            existing_review = existing_reviews.first()
    except:
        existing_review = None
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            image_urls = form.cleaned_data.get('image_urls', [])
            
            if existing_review:
                existing_review.rating = form.cleaned_data['rating']
                existing_review.comment = form.cleaned_data['comment']
                existing_review.set_image_urls(image_urls)
                existing_review.save()
                messages.success(request, 'Your review has been updated!')
            else:
                if not has_purchased:
                    messages.error(request, 'You can only review products you have purchased.')
                    return redirect('product_detail', product_id=product_id)
                
                review = Review.objects.create(
                    product=product,
                    user=request.user,
                    order=purchased_order if purchased_order else None,
                    rating=form.cleaned_data['rating'],
                    comment=form.cleaned_data['comment']
                )
                review.set_image_urls(image_urls)
                review.save()
                messages.success(request, 'Thank you for your review!')
            
            return redirect('product_detail', product_id=product_id)
    else:
        if existing_review:
            initial_data = {
                'rating': existing_review.rating,
                'comment': existing_review.comment,
                'image_urls': '\n'.join(existing_review.get_image_urls())
            }
            form = ReviewForm(initial=initial_data)
        else:
            form = ReviewForm()
    
    context = {
        'product': product,
        'form': form,
        'existing_review': existing_review,
        'has_purchased': has_purchased,
    }
    
    return render(request, 'core/add_review.html', context)