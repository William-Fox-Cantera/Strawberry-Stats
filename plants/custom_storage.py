import os 
from django.views import View
from django.http import JsonResponse
from django_backend.custom_storages import MediaStorage

class ImageStorage(S3Boto3Storage):
    bucket_name = 'tric-static-bucket'
    location = 'images'
    default_acl = 'public-read'
    