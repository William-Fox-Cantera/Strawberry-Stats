from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Customer)

def generate_field_info_dict():
    fields_dict = {}
    for fieldData in StaticFieldInfo.objects.all():
        fields_dict[str(fieldData.field_id)] = {
                                            "field_id":str(fieldData.field_id), 
                                            "datum_latitude":fieldData.datum_latitude,
                                            "datum_longitude":fieldData.datum_longitude
                                        }
    return fields_dict