from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Protected pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/users/', views.admin_users, name='admin_users'),
    path('dashboard/admin/user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('dashboard/admin/products/add/', views.admin_add_product, name='admin_add_product'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # Reviews
    path('product/<int:product_id>/review/add/', views.add_review, name='add_review'),
    path('review/<str:review_id>/delete/', views.delete_review, name='delete_review'),

    # contact messages
    path('dashboard/admin/messages/', views.admin_contact_messages, name='admin_contact_messages'),
    path('dashboard/admin/message/<str:message_id>/', views.admin_contact_message_detail, name='admin_contact_message_detail'),
    path('dashboard/admin/message/<str:message_id>/delete/', views.admin_contact_message_delete, name='admin_contact_message_delete'),
]