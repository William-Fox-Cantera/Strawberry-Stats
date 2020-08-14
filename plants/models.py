from django.db import models
from django.contrib.auth.models import User
from plants.storage_backends import PublicMediaStorage, PrivateMediaStorage
from .helpers import get_csv_path, get_profile_pic_path
from django.contrib.postgres.fields import JSONField


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
    profile_pic = models.ImageField(upload_to=get_profile_pic_path,
                                    storage=PublicMediaStorage(),
                                    null=True, 
                                    blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    file_upload = models.FileField(upload_to=get_csv_path, 
                                        storage=PrivateMediaStorage(), 
                                        null=True, 
                                        blank=True)
    meta_list = JSONField(null=True, default=dict)
    area_info_forms = JSONField(null=True, default=dict)
    date_collected = models.DateTimeField(auto_now_add=False, null=True)
    FIELD1 = 'Fifer'
    FIELD2 = 'Camden'
    FIELDS = (
        (FIELD1, 'Fifer'),
        (FIELD2, 'Camden')
    )
    field_id = models.CharField(max_length=200, choices=FIELDS, default=FIELD1) 

    """
    __str__: Method to enumerate the class, especially in the database.
    """
    def __str__(self):
        return self.name or ''

