from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path("sell", views.sell_item, name="sell"),
    path("cart", views.cart, name="cart"),
    path("item/<int:item_id>", views.view_item, name="item"),
    path("category/<str:name>", views.category_view, name="category"),
    path("wishlist", views.wishlist_view, name="wishlist"),
    path('checkout', views.checkout, name='checkout'),
    path('history', views.history, name='history'),
    path('my_listings', views.my_listings, name='my_listings'),

    # API
    path("update_cart", views.update_cart, name="update_cart"),
    path("update_wishlist", views.update_wishlist, name="update_wishlist"),
    path('edit_item/<int:item_id>', views.edit_item, name='edit_item'),
    path('history_search', views.history_search_api, name='history_search'),
    path('get_user_tz', views.get_user_tz, name='get_user_tz'),

    # Authentication
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='ecom/password_reset.html'), name="reset_password"),
    path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(template_name='ecom/password_reset_done.html'), name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='ecom/password_reset_confirm.html'), name="password_reset_confirm"),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='ecom/password_reset_complete.html'), name="password_reset_complete"),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)