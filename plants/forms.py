from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user', 'file_upload', 'meta_list']


"""
CLASS - CustomerFileUploadForm, form class just for handling file uploads.
"""
class CustomerFileUploadForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'date_collected', 'field_id', 'file_upload', 'field_notes']

    def __init__(self, *args, **kwargs):
        username = kwargs.pop('username')
        super().__init__(*args, **kwargs)
        wanted_user = Customer.objects.get(name=username)
        print(wanted_user.field_id)
        FRUIT_CHOICES = (('HEY', "HJ"), ("BANAAN", "APLLE"))
        self.fields['field_id'] = forms.CharField(label='What is your favorite fruit?', widget=forms.Select(choices=FRUIT_CHOICES))



class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class FieldInfoForm(ModelForm):
    class Meta:
        model = FieldInfo
        fields = '__all__'
        exclude = ['user']