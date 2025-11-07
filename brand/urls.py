from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('brand/<int:pk>/', views.brand_detail, name='brand_detail'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('product_dashboard/', views.product_dashboard, name='product_dashboard'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_success/', views.order_success, name='order_success'),
    path('orders/', views.order_list, name='order_list'),
    path('users/', views.user_list, name='user_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
]
