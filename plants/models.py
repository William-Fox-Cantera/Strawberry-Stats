from django.db import models
from django import forms
from django.contrib.auth.models import User
from plants.storage_backends import PublicMediaStorage, PrivateMediaStorage
from .helpers import get_path, get_profile_pic_path, get_fields
from django.contrib.postgres.fields import JSONField
import datetime

# Create your models here.

# Steps to updating the database models:
#
#   - python manage.py makemigrations
#   - python manage.py migrate

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True) 
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(upload_to=get_profile_pic_path,
                                    storage=PublicMediaStorage(),
                                    null=True, 
                                    blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    file_upload = models.FileField(upload_to=get_path, 
                                        storage=PrivateMediaStorage(), 
                                        null=True, 
                                        blank=True)
    meta_list = JSONField(null=True, default=dict)
    area_info_forms = JSONField(null=True, default=dict)
    date_collected = models.DateField(default=datetime.date.today)
    
    permitted_fields = models.CharField(max_length=500, null=True)
    field_id = models.CharField(max_length=200, null=True, choices=(('---', '---'), ('---', '---')), default="---") 
    field_notes = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name or ''


class FieldInfo(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    operator_name = models.CharField(max_length=200)
    field_name = models.CharField(max_length=200)
    pixels_per_meter = models.CharField(max_length=200)
    rotational_offset = models.CharField(max_length=200)
    datum_latitude = models.CharField(max_length=200)
    datum_longitude = models.CharField(max_length=200)
    camera_to_gps_x = models.CharField(max_length=200)
    camera_to_gps_y = models.CharField(max_length=200)




