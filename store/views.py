from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import home_product,contactform, community,shop_page, CartItem
from .forms import ContactForm

# this for home page url and contact form submission
def home(request):
    if request.method=='POST':
        name=request.POST.get('name', '').strip()
        email=request.POST.get('email', '').strip()
        if name and email:
            try:
                validate_email(email)
                contactform.objects.create(name=name,email=email)
                messages.success(request, "Thank you for subscribing to our newsletter!")
            except ValidationError:
                messages.error(request, "Please enter a valid email address.")
        return redirect("home")
            

    products = home_product.objects.all().order_by('product_id')
    community_items = community.objects.all()
    context = {
        'products': products,
        'community': community_items
    }
    return render(request, 'home.html', context)

# this for about page url
def about(request):
    products=home_product.objects.all().order_by('product_id')
    context={
        'products':products
    }
    return render(request, 'about.html',context)

# this for shop page url
def shop(request):
    products = home_product.objects.all().order_by('product_id')
    return render(request,'shop.html',{'products':products})

# this for product detail page url and also pass the products to footer in product detail page

def product_detail(request,pid):
    product=get_object_or_404(shop_page,product_id=pid)
    products=home_product.objects.all().order_by('product_id')
    return render(request,'shop_page.html',{'product':product, 'products':products})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return redirect("contact")
            
    return render(request, 'contact.html')

# ADD TO CART view
def add_to_cart(request, pid):
    if request.method == 'POST':
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        size = request.POST.get('size', 'M')
        quantity = int(request.POST.get('quantity', 1))

        # Check if the product already exists with the same size for this user
        existing_item = CartItem.objects.filter(
            session_key=session_key, product_id=pid, size=size
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
            messages.success(request, "Cart updated: added extra quantity.")
        else:
            # Look up product in home_product database
            product = get_object_or_404(home_product, product_id=pid)
            CartItem.objects.create(
                session_key=session_key,
                product_id=pid,
                product_name=product.name,
                price=product.price,
                product_image=product.main_image.url,
                size=size,
                quantity=quantity
            )
            messages.success(request, "Item added to cart successfully.")
        return redirect('cart_view')
    return redirect('product_detail', pid=pid)

# CART VIEW
def cart_view(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    items = CartItem.objects.filter(session_key=session_key).order_by('added_at')
    total = sum(item.subtotal() for item in items)
    
    # Calculate cart count for header dynamic updates
    cart_count = sum(item.quantity for item in items)
    
    context = {
        'items': items,
        'total': total,
        'cart_count': cart_count
    }
    return render(request, 'cart.html', context)

# REMOVE FROM CART view
def remove_from_cart(request, item_id):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    
    CartItem.objects.filter(id=item_id, session_key=session_key).delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart_view')

from django.http import JsonResponse
import json

def update_cart(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            
            item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
            
            if action == 'increase':
                item.quantity += 1
                item.save()
            elif action == 'decrease':
                if item.quantity > 1:
                    item.quantity -= 1
                    item.save()
                else:
                    item.delete()
                    return JsonResponse({'status': 'deleted'})
                    
            # Recalculate totals
            items = CartItem.objects.filter(session_key=session_key)
            total = sum(i.subtotal() for i in items)
            cart_count = sum(i.quantity for i in items)
            
            return JsonResponse({
                'status': 'updated',
                'quantity': item.quantity,
                'item_subtotal': item.subtotal(),
                'cart_total': total,
                'cart_count': cart_count
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)