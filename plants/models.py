from django.db import models
from django.contrib.auth.models import User


# Create your models here.

# Steps to updating the database models:
#
#   - python manage.py makemigrations
#   - python manage.py migrate


class Customer(models.Model):
    # null = True allows for the fields to be blank without errors
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True) 
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default="default_pic.jpg", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    """
    __str__: Method to enumerate the class, especially in the database.
    """
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, null=True) 
    
    """
    __str__: Method to enumerate the class, especially in the database.
    """
    def __str__(self):
        return self.name


class Product(models.Model):
    CATEGORY = (
        ('Indoor', 'Indoor'),
        ("Out Door", 'Out Door'),
    )
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(null=True)
    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    description = models.CharField(max_length=200, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    tags = models.ManyToManyField(Tag)

    """
    __str__: Method to enumerate the class, especially in the database.
    """
    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    )
    # SET_NULL makes it so the order won't be deleted if the customer is deleted for whatever reason
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS)
    note = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.product.name