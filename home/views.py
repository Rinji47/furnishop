from django.shortcuts import render, redirect
from .models import Product, Category, Cart, Order, WishList
import hmac, uuid, hashlib, base64
from django_esewa import EsewaPayment

# Create your views here.
def home(request):
    products = Product.objects.all()
    new_arrivals = products.order_by('-created_at')[:10]
    categories = Category.objects.all()
    wishlist_items = WishList.objects.filter(user=request.user).values_list('product_id', flat=True) if request.user.is_authenticated else []

    context = {
        'products': products,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'home.html',context)

def product_details(request, id):
    product_details = Product.objects.filter(id=id).first()
    related_products = Product.objects.filter(category=product_details.category).exclude(id=product_details.id)[:4]
    wishlist_items = WishList.objects.filter(user=request.user).values_list('product_id', flat=True) if request.user.is_authenticated else []

    context = {
        'product_details': product_details,
        'related_products': related_products,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'shop-single.html', context)

def add_to_cart(request, id):
    if request.method == "POST":
        product_id = id
        quantity = int(request.POST.get('qty', 1))
        cart_item, created = Cart.objects.get_or_create( user = request.user, product_id=product_id, is_active=True)
        if created:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.quantity += quantity
            cart_item.save()
    refferer = request.META.get('HTTP_REFERER', 'home')
    return redirect(refferer)

def decrement_cart_item(request, id):
    if request.method == "POST":
        cart_item = Cart.objects.filter(id=id, user=request.user, is_active=True).first()
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        refferer = request.META.get('HTTP_REFERER', 'home')
        return redirect(refferer)

def increment_cart_item(request, id):
    if request.method == "POST":
        cart_item = Cart.objects.filter(id=id, user=request.user, is_active=True).first()
        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        refferer = request.META.get('HTTP_REFERER', 'home')
        return redirect(refferer)
    
def delete_cart_item(request, id):
    if request.method == "POST":
        cart_item = Cart.objects.filter(id=id, user=request.user, is_active=True).first()
        if cart_item:
            cart_item.delete()
        refferer = request.META.get('HTTP_REFERER', 'home')
        return redirect(refferer)

def buy_now(request, id):
    product_details = Product.objects.filter(id=id).first()
    context = {
        'product_details': product_details,
    }
    return render(request, 'checkout.html', context)

def cart(request):
    cart_items = Cart.objects.filter(user=request.user, is_active=True)
    total_price = sum([item.product.price * item.quantity for item in cart_items])
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

def generate_signature(key, message):
    key = key.encode('utf-8')
    message = message.encode('utf-8')

    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()

    #Convert the digest to a Base64-encoded string
    signature = base64.b64encode(digest).decode('utf-8')

    return signature

def cart_checkout(request):
    cart_items = Cart.objects.filter(user=request.user, is_active=True)
    tax_amount = 0.0
    secret_key = '8gBm/:&EnhH.1/q'
    total_price = float(sum([item.product.price * item.quantity for item in cart_items]))

    transaction_uuid = request.session.get('transaction_uuid')
    order = None
    form = None

    if not transaction_uuid:
        transaction_uuid = str(uuid.uuid4())
        order = Order.objects.create(
            user=request.user,
            status='PENDING',
            product_code='EPAYTEST',
            amount=total_price,
            tax_amount=tax_amount,
            total_amount=tax_amount + total_price,
            delivery_charge=0.0,
            service_charge=0.0,
            transaction_uuid=transaction_uuid
        )
        order.carts.set(cart_items)
        request.session['transaction_uuid'] = transaction_uuid
        
    else:
        order = Order.objects.filter(transaction_uuid=transaction_uuid).first()

    if order:
        epayment = EsewaPayment(
            amount=order.amount,
            total_amount=order.total_amount,
            transaction_uuid=str(order.transaction_uuid),
            product_code=order.product_code,
            success_url=f'http://localhost:8000/success/{order.transaction_uuid}/',
            failure_url=f'http://localhost:8000/failure/{order.transaction_uuid}/',
            product_delivery_charge=order.delivery_charge,
            product_service_charge=order.service_charge,
            tax_amount=order.tax_amount,
            secret_key=secret_key
        )
        epayment.create_signature()
        form = epayment.generate_form()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'form': form,
    }
    return render(request, 'checkout.html', context)

    
def success(request, transaction_uuid):
    request.session.pop('transaction_uuid', None)
    order = Order.objects.filter(transaction_uuid=transaction_uuid).first()
    epayment = EsewaPayment(
            amount=order.amount,
            total_amount=order.total_amount,
            transaction_uuid=str(order.transaction_uuid),
            product_code=order.product_code,
            success_url=f'http://localhost:8000/success/{order.transaction_uuid}/',
            failure_url=f'http://localhost:8000/failure/{order.transaction_uuid}/',
            product_delivery_charge=order.delivery_charge,
            product_service_charge=order.service_charge,
            tax_amount=order.tax_amount,
            secret_key='8gBm/:&EnhH.1/q'
        )
    epayment.create_signature()
    if epayment.is_completed(True):
        order.status = 'COMPLETED'
        order.carts.update(is_active=False)
        order.save()
        return render(request, 'success.html', {'transaction_uuid': transaction_uuid})
    else:
        order.status = 'FAILED'
        order.save()
        return redirect('failure', transaction_uuid=transaction_uuid)


def failure(request, transaction_uuid):
    request.session.pop('transaction_uuid', None)
    return render(request, 'failure.html', {'transaction_uuid': transaction_uuid})

def wishlist(request):
    wishlist_items = WishList.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist.html', context)

def add_to_wishlist(request, id):
    if request.method == "POST":
        product = Product.objects.filter(id=id).first()
        wishlist_item, created = WishList.objects.get_or_create(user=request.user, product=product)
        if created:
            wishlist_item.save()
            refferer = request.META.get('HTTP_REFERER', 'home')
            return redirect(refferer)
        else:
            refferer = request.META.get('HTTP_REFERER', 'home')
            return redirect(refferer)
    # else:
    #     wishlist_item.delete()
    #     refferer = request.META.get('HTTP_REFERER', 'home')
    #     return redirect(refferer)
        
def remove_from_wishlist(request, id):
    if request.method == "POST":
        wishlist_item = WishList.objects.filter(product=id, user=request.user).first()
        if wishlist_item:
            wishlist_item.delete()
            refferer = request.META.get('HTTP_REFERER', 'home')
            return redirect(refferer)
        return redirect('wishlist')