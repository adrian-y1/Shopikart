import email
from multiprocessing import context
from pyexpat import model
from re import M
from secrets import choice
from unittest.util import _MAX_LENGTH
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from sqlalchemy import desc, false
from .models import *
from django import forms
from django.http import JsonResponse
import json
from django.contrib import messages
import datetime
# import zoneinfo
import pytz

class SellItemForm(forms.Form):
    name = forms.CharField(label='Name:', max_length=30,  widget=forms.TextInput(attrs={'placeholder': 'Item name', 'class': 'form-control'}))
    description = forms.CharField(label='Description:', max_length=200, widget=forms.Textarea(attrs={'placeholder': 'Item description', 'class': 'form-control'}))
    quantity = forms.IntegerField(label='Quantity:',min_value=0, max_value=100 , widget=forms.NumberInput(attrs={'placeholder': 'Item quantity', 'class': 'form-control'}))
    category = forms.ChoiceField(label='Category:', choices=CATEGORIES, widget=forms.Select(attrs={'class': 'form-control'}))
    image = forms.FileField(label='Image:', required=True)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'comment', 'rating']


def get_user_tz(request):
    try:
        user_tz = json.loads(request.body)['timezone']
        request.session['timezone'] = user_tz
    except ValueError:
        return JsonResponse({'Error': 'Cannot access this data.'})
    return JsonResponse({'user_tz': 'user_tz'}, safe=False)


def index(request):
    all_items = Item.objects.all().order_by('-date_listed')
    context = {'all_items': all_items}
    return render(request, 'ecom/index.html', context)


def category_view(request, name):
    category_list = []

    for category in CATEGORIES:
        category_list.append(category[0])
        
    if name not in category_list:
        messages.success(request, 'The requested page does not exist.')
        return redirect('index')
    else:
        items = Item.objects.filter(category=name)
        
    context = {'category_items': items, "category_name": name}
    return render(request, 'ecom/category_pg.html', context)


@login_required(login_url='/login')
def sell_item(request):
    if request.method == 'POST':
        form = SellItemForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if float(request.POST['price']) <= 10000000:
                    name = form.cleaned_data['name']
                    description = form.cleaned_data['description']
                    price = request.POST['price']
                    quantity = form.cleaned_data['quantity']
                    image = form.cleaned_data['image']
                    category = form.cleaned_data['category']
                    Item.objects.create(name=name, description=description, image=image,category=category, price=price, owner=request.user,  quantity=quantity)
                    messages.success(request, 'Item has been successfully listed for sale.')
                    return redirect('index')
                else:
                    messages.error(request, 'Price field max value exceeded. Max value is 10000000.')
                    return redirect('sell') 
            except ValueError:
                messages.error(request, 'Price field cannot be blank!')
                return redirect('sell') 

    context = {'sell_form': SellItemForm()}
    return render(request, 'ecom/sell.html',context)


@login_required(login_url='/login')
def view_item(request, item_id):
    try:
        requested_item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        messages.error(request, 'The request item does not exist')
        return redirect('index') 

    quantity = 'p' * requested_item.quantity
    item_reviews = Review.objects.filter(product=item_id).order_by('-date_posted')
    history_obj = History.objects.filter(product=item_id, user=request.user)
    tz = pytz.timezone(request.session['timezone'])
    item_listing_date = requested_item.date_listed.astimezone(tz).strftime("%b %d %Y, %I:%M %p")

    for item in item_reviews:
        item.date_posted = item.date_posted.astimezone(tz).strftime("%b %d %Y, %I:%M %p")

    context = {
        'req_item': requested_item, 
        'quantity': quantity, 
        'item_reviews': item_reviews, 
        'history_obj': history_obj,
        'item_listing_date': item_listing_date
        }

    try: 
       if request.user.is_authenticated:
            wishlist_items = Wishlist.objects.get(user=request.user)
            context['wishlist_items'] = wishlist_items.product.all()
    except Wishlist.DoesNotExist:
        pass
    

    if request.method == 'POST':
        
        if request.user.is_authenticated:
            if request.POST.get('delete_item') == 'Delete Item':
                get_item = Item.objects.get(id=item_id)
                get_item.delete()
                return redirect('index')
            
            elif 'rating'in request.POST:
                if len(request.POST['comment']) <= 200:
                    if len(request.POST['title']) <= 30:
                        try:
                        # If user already has a review for this product, update the existing one
                            user_review = Review.objects.get(user=request.user, product=item_id)
                            review_form = ReviewForm(request.POST, instance=user_review)
                            review_form.save()
                            messages.success(request, 'Your review has been successfully updated.')
                            return redirect(f'/item/{item_id}')

                        except Review.DoesNotExist:
                            # Create a new review
                            review_form = ReviewForm(request.POST)
                            if review_form.is_valid():
                                try:
                                    product_obj = Item.objects.get(id=item_id)
                                    title = review_form.cleaned_data['title']
                                    comment = review_form.cleaned_data['comment']
                                    rating = review_form.cleaned_data['rating']
                                    user_review = Review(product=product_obj, user=request.user, title=title, comment=comment, rating=rating)
                                    user_review.save()
                                    messages.success(request, f'You have successfully placed a review on {requested_item.name}.')
                                    return redirect(f'/item/{item_id}')
                                except Item.DoesNotExist:
                                    pass
                    else:
                        messages.error(request, 'Review Title length exceeded. Max length is 30.')
                        return redirect(f'/item/{item_id}')
                else:
                    messages.error(request, 'Comment Length Exceeded. Max length is 200.')
                    return redirect(f'/item/{item_id}')
            else:
                messages.error(request, 'Rating field cannot be blank!')
                return redirect(f'/item/{item_id}')

        else:
            return redirect('login')
    
    return render(request, 'ecom/item.html', context)


@login_required(login_url='/login')
def edit_item(request, item_id):
    try:
        item = Item.objects.get(owner=request.user, id=item_id)
    except Item.DoesNotExist:
        messages.error(request, 'FORBIDDEN! You have attempted to access a forbidden request.')
        return redirect('index')
    
    description = json.loads(request.body)['description']
    title = json.loads(request.body)['title']
    price = json.loads(request.body)['price']
    quantity = json.loads(request.body)['quantity']

    if len(description) <= 200:
        item.description = description
        item.save()
    else:
        messages.error(request, 'Description Length Exceeded. Max length is 200.')
        return redirect(f'/item/{item_id}')

    if len(title) <= 30:
        item.name = title
        item.save()
    else:
        messages.error(request, 'Title length exceeded. Max length is 30.')
        return redirect(f'/item/{item_id}')

    if float(price) <= 10000000:
        item.price = price
        item.save()
    else:
        messages.error(request, 'Price field max value exceeded. Max Value is 10000000!')
        return redirect(f'/item/{item_id}')

    if int(quantity) >= item.quantity and int(quantity) < 100:
        item.quantity = quantity
        item.save()
    else:
        messages.error(request, 'Quantity must be higher than or equal to current quantity, and cannot exceed the threshold of 100.')
        return redirect(f'/item/{item_id}')

    return JsonResponse(item.serialize(), safe=False)


@login_required(login_url='/login')
def cart(request):
    try:
        orders = Order.objects.filter(buyer=request.user)
    except Order.DoesNotExist:
        pass

    for order in orders:
        if order.quantity <= 0:
            order.delete()

        if order.product.quantity > 0 and order.quantity > order.product.quantity:
            order.quantity = order.product.quantity
            order.save()
            messages.info(request, 'Item quantity has been changed due to insufficient availability.')
            return redirect('cart')

        elif order.product.quantity <= 0:
            order.delete()
            messages.error(request, 'Item no longer available.')
            return redirect('cart')

    total = sum([order.price_per_item for order in orders])

    if request.method == "POST":
        if 'cart_order_id' in request.POST:
            order_obj = Order.objects.get(id=int(request.POST['cart_order_id']))

        if request.POST.get('remove') == 'Remove':
            order_obj.delete()
            return redirect('cart')

    context = {'my_orders': orders, 'total_price': total}

    return render(request, 'ecom/cart.html', context)


@login_required(login_url='/login')
def update_cart(request):

    data = json.loads(request.body)
    try:
        item_obj = Item.objects.get(id=int(data['item_id']))
    except Item.DoesNotExist:
        messages.error(request, 'The requested item does not exist.')
        return redirect('index')
    
    order, created = Order.objects.get_or_create(buyer=request.user, product=item_obj)

    try:
        orders = Order.objects.filter(buyer=request.user)
    except Order.DoesNotExist:
        pass

    if data['action'] == 'add':
        if order.quantity < item_obj.quantity:
            if 'quantity' in data:
                if (order.quantity + int(data['quantity'])) <= item_obj.quantity:
                    order.quantity = order.quantity + int(data['quantity'])
                    order.save()
                else:
                    total = 0
                    for order in orders:
                        total += order.quantity
                    send_to_js = json.dumps({'total': total})
                    return JsonResponse({'amount_exceeding': send_to_js})

            else:
                order.quantity = order.quantity + 1
                order.save()
        else:
            total = 0
            for order in orders:
                total += order.quantity
            send_to_js = json.dumps({'total': total})
            return JsonResponse({'amount_exceeded': send_to_js})

    elif data['action'] == 'remove':
        order.quantity = order.quantity - 1
        order.save()
    try:
        user_orders = Order.objects.filter(buyer=request.user)
    except Order.DoesNotExist:
        pass

    return JsonResponse([user_order.serialize() for user_order in user_orders], safe=False)


@login_required(login_url='/login')
def checkout(request):
    checkout, created = Checkout.objects.get_or_create(buyer=request.user, purchased=False)
    orders = checkout.buyer.orders.all()
    total = sum([order.price_per_item for order in orders])
    context = {'orders': orders, 'total_price': total}

    for order in orders:
        if order.quantity <= 0:
            order.delete()

        if order.product.quantity > 0 and order.quantity > order.product.quantity:
            order.quantity = order.product.quantity
            order.save()
            messages.info(request, 'Item quantity has been changed due to insufficient availability.')
            return redirect('checkout')

        elif order.product.quantity <= 0:
            order.delete()
            messages.error(request, 'Item no longer available.')
            return redirect('cart')

    if request.method == 'POST':
        for order in orders:
            order_item = Item.objects.get(id=order.product.id)
            order_item.quantity = order_item.quantity - order.quantity
            order_item.save()
            order.delete_and_create()
        messages.success(request, 'Congratulations, Your order was successfully purchased.')
        return redirect('history')

    return render(request, 'ecom/checkout.html', context)


@login_required(login_url='/login')
def history(request):
    try:
        history_obj = History.objects.filter(user=request.user).order_by('-date_added')
        tz = pytz.timezone(request.session['timezone'])
        for obj in history_obj:
            obj.date_added = obj.date_added.astimezone(tz).strftime("%b %d %Y, %I:%M %p")
    except History.DoesNotExist:
        pass

    
    context = {'my_history': history_obj}
    return render(request, 'ecom/history.html', context)


@login_required(login_url='/login')
def wishlist_view(request):
    try:
        wishlist_items = Wishlist.objects.filter(user=request.user)
    except Wishlist.DoesNotExist:
        pass

    context = {'wishlist_items': wishlist_items}

    return render(request, 'ecom/wishlist.html', context)


@login_required(login_url='/login')
def update_wishlist(request):
    data = json.loads(request.body)

    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    try:
        item_obj = Item.objects.get(id=int(data['item_id']))
    except Item.DoesNotExist:
        messages.error(request, 'The requested item does not exist.')
        return redirect('index')

    if data['action'] == 'add':
        wishlist.product.add(item_obj)
    elif data['action'] == 'remove':
        wishlist.product.remove(item_obj)

    try:
        wishlist_obj = Wishlist.objects.get(user=request.user)
        wishlist_items = wishlist_obj.product.all()
    except Wishlist.DoesNotExist:
        pass

    return JsonResponse([item.serialize() for item in wishlist_items], safe=False)


@login_required(login_url='/login')
def my_listings(request):
    my_items = Item.objects.filter(owner=request.user)
    return render(request, 'ecom/my_listings.html', {'my_items': my_items})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        
        if password != confirmation:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        if username == '':
            messages.error(request, 'Username field cannot be blank.')
            return redirect('register')
        if email == '':
            messages.error(request, 'Email field cannot be blank.')
            return redirect('register')
        if password == '':
            messages.error(request, 'Password field cannot be blank.')
            return redirect('register')
        if confirmation == '':
            messages.error(request, 'Confirmation field cannot be blank.')
            return redirect('register')
        if first_name == "":
            messages.error(request, 'First Name field cannot be blank.')
            return redirect('register')
        if last_name == "":
            messages.error(request, 'Last Name field cannot be blank.')
            return redirect('register')

        all_users = User.objects.all()

        for u in all_users:
            if username == u.username:
                messages.error(request, 'Username already taken.')
                return redirect('register')
            elif email == u.email:
                messages.error(request, 'Email already taken.')
                return redirect('register')
        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            user.save()
        except IntegrityError:
            messages.error(request, 'Username already taken.')
            return redirect('register')
        login(request, user)
        return redirect('index')
    else:
        return render(request, "ecom/register.html")


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else: 
            messages.error(request, 'Invalid username and/or password.')
            return redirect('login')
    return render(request, "ecom/login.html")

def logout_view(request):
    logout(request)
    return redirect('index')
