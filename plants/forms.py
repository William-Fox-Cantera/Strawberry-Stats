from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user', 'user_file_upload']


"""
CLASS - CustomerFileUploadForm, form class just for handling file uploads.
"""
class CustomerFileUploadForm(ModelForm):
    class Meta:
        model = Customer
        fields = ('user_file_upload',)


class OrderForm(ModelForm):
    class Meta: # Minimum two fields
        model = Order # Which model to build a form for
        fields = '__all__' # Create the form with all the fields from the model
    

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']