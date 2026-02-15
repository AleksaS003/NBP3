from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import User, ActivityLog, UserProfile

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