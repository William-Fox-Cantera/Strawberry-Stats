from celery import shared_task
from celery_progress.backend import ProgressRecorder
from time import sleep
from django.core.files.storage import FileSystemStorage
from .storage_backends import PrivateMediaStorage, PublicMediaStorage
import json
import piexif
import piexif.helper
from zipfile import ZipFile
from io import BytesIO
from .models import Customer


@app.task
def add(x, y):
    return x + y

@shared_task(bind=True)
def upload_images(self, upload_name, customer_name):
    media_storage = PublicMediaStorage()
    meta_list = []
    progress_recorder = ProgressRecorder(self)
    customer = Customer.objects.get(name=customer_name)
    with ZipFile(customer.user_file_upload, 'r') as zipfile:
        zipfile.extractall()
        i = 0
        file_list = zipfile.namelist()
        root = file_list[0]
        file_list.remove(file_list[0]) # remove pesky root directory
        jpg_list = [name for name in file_list if name.endswith(".jpg")]
        for filename in jpg_list: 
            if filename.endswith(".jpg"): # Other files shouldn't be trusted
                exif_dict = piexif.load(str(i) + '.jpg') # file_list[0] is the name of the root dir in zip file
                comment = piexif.helper.UserComment.load(exif_dict['Exif'][piexif.ExifIFD.UserComment])
                meta_dict = json.loads(comment)
                data = zipfile.read(str(i) + '.jpg')
                dataEnc = BytesIO(data)
                full_image_path = "%s/%s/%s" % (customer_name, meta_dict["date_captured"], filename)
                media_storage.save(full_image_path, dataEnc)
                meta_dict["image"] = full_image_path
                meta_list.append(meta_dict) # list of dictionaries containing the meta data 
                progress_recorder.set_progress(i+1, len(jpg_list), f"uploading image: {i}")
        customer.meta_list[upload_name] = meta_list
        customer.save() # add the list of dictionaries to the database
        customer.user_file_upload.delete(save=False) # removes from postgresql, s3
        
