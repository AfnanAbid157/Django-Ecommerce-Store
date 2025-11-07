from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .forms import SignUpForm
from .models import Brand, Product, CartItem, Order
from django.contrib.auth.models import User


# ------------------ AUTH VIEWS ------------------

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if username == 'admin' and password == '1234':
                return redirect('dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------ HOME / BRAND ------------------

@login_required
def home_view(request):
    brands = Brand.objects.all()
    return render(request, 'home.html', {'brands': brands})


@login_required
def brand_detail(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    return render(request, 'brand_detail.html', {'brand': brand})


# ------------------ ADMIN DASHBOARDS ------------------

@login_required
def dashboard_view(request):
    if request.user.username != 'admin':
        messages.warning(request, "Access denied. Only admin can view the dashboard.")
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST['name']
            title = request.POST['title']
            description = request.POST['description']
            logo = request.FILES.get('logo')
            Brand.objects.create(name=name, title=title, description=description, logo=logo)

        elif action == 'edit':
            brand_id = request.POST.get('brand_id')
            brand = get_object_or_404(Brand, id=brand_id)
            brand.name = request.POST['name']
            brand.title = request.POST['title']
            brand.description = request.POST['description']
            if 'logo' in request.FILES:
                brand.logo = request.FILES['logo']
            brand.save()

        elif action == 'delete':
            brand_id = request.POST.get('brand_id')
            Brand.objects.filter(id=brand_id).delete()

        return redirect('dashboard')

    brands = Brand.objects.all()
    return render(request, 'dashboard.html', {'brands': brands})


@login_required
def product_dashboard(request):
    if request.user.username != 'admin':
        messages.warning(request, "Access denied. Only admin can view this page.")
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            brand_id = request.POST['brand']
            title = request.POST['title']
            price = request.POST['price']
            picture = request.FILES.get('picture')
            Product.objects.create(brand_id=brand_id, title=title, price=price, picture=picture)

        elif action == 'edit':
            product_id = request.POST['product_id']
            product = get_object_or_404(Product, id=product_id)
            product.brand_id = request.POST['brand']
            product.title = request.POST['title']
            product.price = request.POST['price']
            if 'picture' in request.FILES:
                product.picture = request.FILES['picture']
            product.save()

        elif action == 'delete':
            product_id = request.POST['product_id']
            Product.objects.filter(id=product_id).delete()

        return redirect('product_dashboard')

    brands = Brand.objects.all()
    products = Product.objects.all()
    return render(request, 'product_dashboard.html', {'brands': brands, 'products': products})


# ------------------ CART & ORDER ------------------

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    messages.success(request, f"{product.title} added to your cart!")
    return redirect('cart')


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Item removed from your cart.")
    return redirect('cart')


@login_required
def place_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    total = sum(item.total_price() for item in cart_items)
    order = Order.objects.create(user=user, total_price=total)
    for item in cart_items:
        order.products.add(item.product)

    cart_items.delete()

    return redirect('order_success')


@login_required
def order_success(request):
    # ✅ Changed from 'brand/order_success.html' → 'order_success.html'
    return render(request, 'order_success.html')


@staff_member_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    # ✅ Changed from 'brand/order.html' → 'order.html'
    return render(request, 'order.html', {'orders': orders})



@staff_member_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users.html', {'users': users})
