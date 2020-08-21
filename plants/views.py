from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .forms import CreateUserForm, CustomerForm, CustomerFileUploadForm, StaticFieldInfoForm
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .storage_backends import PrivateMediaStorage, PublicMediaStorage
import json
import piexif
import piexif.helper
from zipfile import ZipFile
from io import BytesIO
from .models import Customer
from django.http import JsonResponse
from .admin import generate_field_info_dict


def get_area_form(request):
    print(request.user.customer.area_info_forms)
    return JsonResponse({"area_form":request.user.customer.area_info_forms})

def saveAreaForm(request):
    set_to_modify = request.GET.get('current_dataset', None)
    name = request.GET.get("area_name", None)
    soil_type = request.GET.get("soil_type", None)
    user = request.user.customer
    area_form = user.area_info_forms
    area_form[set_to_modify] = {name:{"soil_type":soil_type}}
    user.save()    
    return JsonResponse({})


"""
remove_plant_index, removes the is_favorited and notes attributes from the given index in the users meta_list.
                    This way, it won't be rendered next time the user goes to the page.

Consumes: request, the html request
Produces: Nothing
"""
def remove_plant_index(request):
    user = request.user.customer
    user_meta = user.meta_list
    set_to_modify = request.GET.get('current_dataset', None)
    favorite_to_remove = request.GET.get('plant_index', None)
    if user_meta[set_to_modify][int(favorite_to_remove)]['is_favorited']:
        user_meta[set_to_modify][int(favorite_to_remove)].pop('is_favorited')
    if  user_meta[set_to_modify][int(favorite_to_remove)]['notes']:
        user_meta[set_to_modify][int(favorite_to_remove)].pop('notes')
    user.save()
    return JsonResponse({})


"""
save_favorite_plants, gets an ajax request with the data about a favorited plant. Saves this
                      in the database by adding an attribute to the meta list to indicate that
                      plant is favorited.

Consumes: Nothing
Produces: Nothing
"""
def save_favorite_plants(request):
    user = request.user.customer
    user_meta = user.meta_list
    set_to_modify = request.GET.get('current_dataset', None)
    data_to_add = json.loads(request.GET.get('notes', None))

    for key, val in data_to_add.items():
        user_meta[set_to_modify][int(key)]['notes'] = val
        user_meta[set_to_modify][int(key)]['is_favorited'] = 'True'

    user.save()
    return JsonResponse(data_to_add)

    

"""
delete_zip_upload, removes the key and value pair from the meta-list attribute.
                   first gives the user a warning about deleting.

:param request: the html request
:param filename: the name of the file to be deleted
"""
def delete_zip_upload(request, filename=""):
    customer = request.user.customer
    form = CustomerFileUploadForm(instance=customer, username=customer.name)
    if (customer.meta_list.get(filename) != None):
        customer.meta_list.pop(filename)
        customer.save()
    files = [ k for k, v in customer.meta_list.items() ]    

    context = {'should_generate':True, 'upload_names':files, 'form':form}
    return render(request, "plants/user.html", context)


"""
zip_upload, this function renders the user page for uploading a csv file into the database.
            If the has_started boolean is false, it just displays a start button to get 
            the user, started. Otherwise it displays the form for submitting the files.

:param request: the html request from the template user.html
:param destination: string, what action the function should take
"""
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def zip_upload(request, destination="start"):
    customer = request.user.customer
    files = [ k for k, v in customer.meta_list.items() ]
    form = CustomerFileUploadForm(instance=customer, username=customer.name)
    if destination == "start": # Just render the form if the start button is pressed
        return render(request, "plants/user.html", {'form':form, 'should_generate':True, 
                                                    'customer':customer, 'upload_names':files })
    elif destination == "farmville":
        meta = customer.meta_list
        return render(request, "plants/farmville.html", {"meta":meta, 'upload_names':files, 'date_captured':"6/16/2020",
                                                         "percent_flowered":"50%", "total_plants":"8"})
    elif destination == "upload":
        if request.method == 'POST':
            upload_name = ""
            form = CustomerFileUploadForm(request.POST, request.FILES, instance=customer, username=customer.name)
            for filename, file in request.FILES.items(): # get the zip file name
                upload_name = request.FILES[filename].name
            if upload_name in customer.meta_list.keys(): # make sure the same file isn't being uploaded more than once
                messages.error(request, "A file with this name has already been uploaded.")
                return render(request, "plants/user.html", {'form':form, 'should_generate':True, 'customer':customer, 'upload_names':files})
            if form.is_valid() and upload_name.endswith(".zip"):
                messages.success(request, upload_name + " Successfully Uploaded")
                upload = form.save()
                user_upload = request.user.customer.file_upload
                upload_images(request, upload_name)
                files.append(upload_name)
                return render(request, 'plants/user.html', { 'form':form, 'should_generate':True, 'date_captured':"6/16/2020",
                                                             'customer':customer, 'upload_names':files })
            else:
                messages.error(request, "Please upload a file ending with \".zip\"")
        else: # If not a post, make a blank form 
            form = CustomerFileUploadForm()

        context = { 'form':form, 'should_generate':True, 'customer':customer,
                    'total_plants':100, 'date_captured':"6/16/2020",
                    'percent_flowered':"60%", 'upload_names':files}
        return render(request, 'plants/user.html', context)


"""
upload_images, takes all of the images int he users uploaded zip file, uploads them the aws s3, then saves
               the meta data from the images in a JSONField for the customer. The zip file is deleted after.

:param upload_name: string, the filename of the zip file uploaded
:param customer_name: string, the name of the customer doing the upload
"""
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def upload_images(request, upload_name):
    media_storage = PublicMediaStorage()
    meta_list = []
    customer = request.user.customer
    with ZipFile(customer.file_upload, 'r') as zipfile:
        zipfile.extractall()
        i = 1
        file_list = zipfile.namelist()
        jpg_list = [name for name in file_list if name.endswith(".jpg")]
        json_database = next(name for name in file_list if name.endswith(".json"))
        for filename in jpg_list: 
            data = zipfile.read(str(i) + '.jpg')
            dataEnc = BytesIO(data)
            full_image_path = "%s/%s/%s" % (customer.name, "1-1-16", filename)
            media_storage.save(full_image_path, dataEnc)
            i += 1

        json_read = zipfile.read(json_database)
        json_data = json.loads(json_read) 
        json_length = len(json_data)
        j = 1
        while True:
            if j > json_length:
                break
            json_data["plant_" + str(j)]["image"] = "%s/%s/%s" % (customer.name, "1-1-16", str(j) + ".jpg")
            meta_list.append(json_data["plant_" + str(j)])
            j += 1
        print(meta_list)
        customer.meta_list[upload_name] = meta_list
        customer.save() # add the list of dictionaries to the database
        customer.file_upload.delete(save=False) # removes from postgresql, s3


"""
user_page, simple method for rendering the home page for the user.

:param request: the html request from the template
"""
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def user_page(request):
    should_generate = False
    context = { 'should_generate':should_generate }
    return render(request, 'plants/user.html', context)



@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save() # Creates the user
            username = form.cleaned_data.get('username')
            

            messages.success(request, 'Account successfully created for: ' + username)
            
            return redirect('login') # Send user to login if they just made an account

    context = {'form':form}
    return render(request, "plants/register.html", context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')
            return render(request, "plants/login.html")

    context = {}
    return render(request, "plants/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid:
            form.save()

    context = {'form':form}
    return render(request, 'plants/account_settings.html', context)



def home(request):
    if request.user.groups.filter(name='admin').exists():
        form = StaticFieldInfoForm()

        usernames = []
        for user in Customer.objects.all():
            usernames.append(user.name)
        fields_dict = generate_field_info_dict()

        context = {'field_form':form, 'fields':StaticFieldInfo.objects.all(), 'usernames':usernames, 'fields_dict':fields_dict}
        return render(request, "plants/admin_input.html", context)
    else:
        return render(request, "plants/user.html")



def save_field_form(request):
    if request.method == 'POST':
        submitted_form = StaticFieldInfoForm(request.POST)
        if submitted_form.is_valid():
            submitted_form.save()
            form = StaticFieldInfoForm()
            return redirect("home")

    usernames = []
    for user in Customer.objects.all():
        usernames.append(user.name)

    fields_dict = generate_field_info_dict()
    context = {'field_form':form, 'fields':StaticFieldInfo.objects.all(), 'usernames':usernames, 'fields_dict':fields_dict}
    return render(request, "plants/admin_input.html", context)


def delete_field_form(request, fieldname):
    form = StaticFieldInfoForm()
    field_names = []
    field = StaticFieldInfo.objects.filter(field_id=fieldname)
    fields_dict = generate_field_info_dict()
    usernames = []

    for user in Customer.objects.all():
        user.field_id = ""
        user.permitted_fields = ""
        user.save()
        usernames.append(user.name)

    field.delete()
    context = {'field_form':form, 'usernames':usernames, 'fields':StaticFieldInfo.objects.all(), 'fields_dict':fields_dict}
    return render(request, "plants/admin_input.html", context)



def get_field_permissions(request):
    username = request.GET.get("username", None)
    fieldname = request.GET.get("fieldname", None)
    print("USER: " + username)
    print("FIELD: " + fieldname)
    user = Customer.objects.get(name=username)
    current_fields = user.permitted_fields.split(",")
    if fieldname in current_fields: # Ignore duplicate fields
        return redirect("home")

    if user.permitted_fields == None:
        user.permitted_fields = ""
    user.permitted_fields += fieldname + ","
    user.save()
    return redirect("home")



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def admin_input(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all() # Query customers child object from model
    order_count = orders.count()
   
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer':customer, 'orders':orders, 'order_count':order_count, 
               'myFilter':myFilter}
    return render(request, "plants/admin_input.html", context)


