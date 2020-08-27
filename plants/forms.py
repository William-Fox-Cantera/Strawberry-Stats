from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'profile_pic']


"""
CLASS - CustomerFileUploadForm, form class just for handling file uploads.
"""
class CustomerFileUploadForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['field_id']

    def __init__(self, *args, **kwargs):
        username = kwargs.pop('username')
        super().__init__(*args, **kwargs)
        wanted_user = Customer.objects.get(name=username)

        fields = (("---"),("---"))
        if wanted_user.permitted_fields != None:
            fields = wanted_user.permitted_fields.split(",")
        FIELDS = (("---", "---"),)
        for field in fields:
            print(field)
            FIELDS = ((field, field),) + FIELDS     

        print(wanted_user.permitted_fields)

        self.fields['field_id'] = forms.CharField(label='Select Field', widget=forms.Select(choices=FIELDS))



class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class RawUploadForm(ModelForm):
    class Meta:
        model = RawUpload
        fields = ['file_upload']

class StaticFieldInfoForm(ModelForm):
    class Meta:
        model = StaticFieldInfo
        fields = '__all__'
        exclude = ['user']
