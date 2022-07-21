from re import T
from .models import *

def total_cart_items(request):
    if request.user.is_authenticated:
        try:
            orders = Order.objects.filter(buyer=request.user)
        except Order.DoesNotExist:
            pass
        total = 0
        for order in orders:
            total += order.quantity
        return {'total_cart_items': total}
    return {}

def total_wishlist_items(request):
    if request.user.is_authenticated:
        context = {}
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_items = wishlist.product.all()
            context['total_wishlist_items'] = len(wishlist_items)
        except Wishlist.DoesNotExist:
            pass
        return {'total_wishlist_items_dict': context}
    return {}

def all_categories(request):
    CATEGORIES = (
        ('', 'Select a Category'),
        ('Toys', 'Toys'),
        ('Fashion', 'Fashion'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home'),
        ('Outdoor', 'Outdoor'),
        ('Beauty', 'Beauty'),
        ('Video Games', 'Video Games'),
        ('Sports', 'Sports'),
        ('Accessories', 'Accessories'),
        ('Office', 'Office'),
        ('Health', 'Health'),
        ('Vehicles', 'Vehicles'),
        ('Other', 'Other')
    )
    return{'all_categories': CATEGORIES}