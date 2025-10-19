from django.urls import path
from .views import home, product_details, add_to_cart, buy_now, cart, increment_cart_item, decrement_cart_item, delete_cart_item
from .views import success, failure, cart_checkout, wishlist, add_to_wishlist, remove_from_wishlist
from accounts.views import login, signup

urlpatterns = [
    path('', home, name='home'),
    path("product/<int:id>/", product_details, name="product_details"),
    path("add-to-cart/<int:id>/", add_to_cart, name="add_to_cart"),
    path("buy_now/<int:id>", buy_now, name="buy_now"),
    path("cart/", cart, name="cart"),
    path('cart/increment/<int:id>/', increment_cart_item, name='increment_cart_item'),
    path('cart/decrement/<int:id>/', decrement_cart_item, name='decrement_cart_item'),
    path('cart/delete/<int:id>/', delete_cart_item, name='delete_cart_item'),
    path('success/<str:transaction_uuid>/', success, name='success'),
    path('failure/<str:transaction_uuid>/', failure, name='failure'),
    path('cart_checkout/', cart_checkout, name='cart_checkout'),
    path('wishlist', wishlist, name='wishlist'),
    path('add-to-wishlist/<int:id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
]