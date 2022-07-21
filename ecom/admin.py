from django.contrib import admin
from .models import *

class WishlistAdmin(admin.ModelAdmin):
    filter_horizontal = ('product',)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name','price', 'owner', 'quantity', 'category' ,'date_listed')

admin.site.register(User)
admin.site.register(Item,ItemAdmin)
admin.site.register(Order)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Review)
admin.site.register(Checkout)
admin.site.register(History)