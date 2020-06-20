from django.db import models
from django.contrib.auth.models import User
from plants.storage_backends import PublicMediaStorage, PrivateMediaStorage
from .helpers import get_file_path

# Create your models here.

# Steps to updating the database models:
#
#   - python manage.py makemigrations
#   - python manage.py migrate


"""
CLASS - Upload, sets up a date and file field for public media storage
"""
class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=PublicMediaStorage())


"""
CLASS - UploadPrivate, sets up a date and file field for private media storage
"""
class UploadPrivate(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=PrivateMediaStorage())


class Customer(models.Model):
    # null = True allows for the fields to be blank without errors
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True) 
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default="default_pic.jpg", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    user_file_upload = models.FileField(
        upload_to=get_file_path, 
        storage=PrivateMediaStorage(), 
        null=True, 
        blank=True
    )

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