from django.db import models
from django import forms
from django.contrib.auth.models import User
from plants.storage_backends import PublicMediaStorage, PrivateMediaStorage
from .helpers import get_raw_upload_path, get_profile_pic_path
from django.contrib.postgres.fields import JSONField

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
    meta_list = JSONField(null=True, default=dict)
    area_info_forms = JSONField(null=True, default=dict)
    
    permitted_fields = models.CharField(max_length=500, null=True)
    field_id = models.CharField(max_length=200, null=True, choices=(('---', '---'), ('---', '---')), default="---") 
    field_notes = models.CharField(max_length=500, null=True, blank=True)
    dataset_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name or ''


class RawUpload(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    file_upload = models.FileField(upload_to=get_raw_upload_path, storage=PublicMediaStorage(), null=True, blank=True)



class StaticFieldInfo(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    field_id = models.IntegerField()
    datum_latitude = models.CharField(max_length=200)
    datum_longitude = models.CharField(max_length=200)


