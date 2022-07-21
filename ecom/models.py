
from django.db import models
from django.contrib.auth.models import AbstractUser

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



class User(AbstractUser):

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
        }


class Item(models.Model):
    name = models.CharField(max_length=30)
    price = models.FloatField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='item_images', blank=False)
    category = models.CharField(max_length=64, choices=CATEGORIES)
    date_listed = models.DateTimeField(auto_now_add=True)
    # Add Image and Category field later

    def __str__(self):
        return f'{self.name}, {self.owner}, {self.price}, {self.quantity}'

    @property
    def total_quantity(self):
        all_items = self.product_items.all()
        total = sum([item.quantity for item in all_items])
        return total

    @property
    def average_rating(self):
        all_reviews = self.reviews.all()
        sum = 0
        for review in all_reviews:
            sum += review.rating
        if len(all_reviews) > 0:
            average = sum / len(all_reviews)
        else:
            average = 0
        return average

    @property
    def len_of_reviews(self):
        all_reviews = self.reviews.all()
        return len(all_reviews)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'owner': self.owner.serialize(),
            'description': self.description,
            'quantity': self.quantity,
            'date_listed': self.date_listed.strftime("%b %d %Y, %I:%M %p"),
            'total_quantity': self.total_quantity
        }

class Order(models.Model):
    buyer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    product = models.ForeignKey(Item, related_name='product_items', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product}"

    def serialize(self):
        return {
            'buyer': self.buyer.serialize(),
            'product': self.product.serialize(),
            'quantity': self.quantity,
            'date_added': self.date_added.strftime("%b %d %Y, %I:%M %p"),
            'price_per_item': self.price_per_item
        }

    @property
    def price_per_item(self):
        total = self.quantity * self.product.price 
        return total

    def delete_and_create(self):
        History.objects.create(user=self.buyer, product=self.product, quantity=self.quantity, price=self.price_per_item)
        super().delete()


class History(models.Model):
    user = models.ForeignKey(User, related_name='history_users', on_delete=models.CASCADE)
    product = models.ForeignKey(Item, related_name='history_items', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product}"
        
    def serialize(self):
        return {
            'user': self.user.serialize(),
            'product': self.product.serialize(),
            'quantity': self.quantity,
            'date_added': self.date_added.strftime("%b %d %Y, %I:%M %p"),
            'price': self.price
        }


class Checkout(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkout_users')
    purchased = models.BooleanField(default=False)
    date_purchased = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer}"


class Wishlist(models.Model):
    product = models.ManyToManyField(Item)
    user = models.ForeignKey(User, related_name='watchlists', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"
    
    def serialize(self):
        return {
            'product': self.product.all().serialize(),
            'user': self.user.serialize()
        }

class Review(models.Model):
    product = models.ForeignKey(Item, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="user_reviews", on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    comment = models.CharField(max_length=200)
    rating = models.FloatField()
    date_posted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} {self.rating}"

