from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm, CustomerFileUploadForm
from .filters import OrderFilter
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




"""
delete_zip_upload, removes the key and value pair from the meta-list attribute.
                   first gives the user a warning about deleting.

:param request: the html request
:param filename: the name of the file to be deleted
"""
def delete_zip_upload(request, filename=""):
    customer = request.user.customer
    form = CustomerFileUploadForm(instance=customer)
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
@allowed_users(allowed_roles=['customer'])
def zip_upload(request, destination="start"):
    customer = request.user.customer
    files = [ k for k, v in customer.meta_list.items() ]
    form = CustomerFileUploadForm(instance=customer)
    if destination == "start": # Just render the form if the start button is pressed
        return render(request, "plants/user.html", {'form':form, 'should_generate':True, 
                                                    'customer':customer, 'upload_names':files })
    elif destination == "farmville":
        meta = customer.meta_list
        return render(request, "plants/farmville.html", {"meta":meta, 'upload_names':files})
    elif destination == "upload":
        if request.method == 'POST':
            upload_name = ""
            form = CustomerFileUploadForm(request.POST, request.FILES, instance=customer)
            for filename, file in request.FILES.items(): # get the zip file name
                upload_name = request.FILES[filename].name
            if upload_name in customer.meta_list.keys(): # make sure the same file isn't being uploaded more than once
                messages.error(request, "A file with this name has already been uploaded.")
                return render(request, "plants/user.html", {'form':form, 'should_generate':True, 'customer':customer, 'upload_names':files})
            if form.is_valid() and upload_name.endswith(".zip"):
                messages.success(request, upload_name + " Successfully Uploaded")
                upload = form.save()
                user_upload = request.user.customer.user_file_upload
                upload_images(upload_name, customer.name)
                files.append(upload_name)
                return render(request, 'plants/user.html', { 'form':form, 'should_generate':True, 
                                                             'customer':customer, 'upload_names':files })
            else:
                messages.error(request, "Please upload a file ending with \".zip\"")
        else: # If not a post, make a blank form 
            form = CustomerFileUploadForm()

        context = { 'form':form, 'should_generate':True, 'customer':customer,
                    'total_plants':100, 'date_captured':"6/16/2020",
                    'percent_flowered':"60%", 'upload_names':files }
        return render(request, 'plants/user.html', context)


def upload_images(upload_name, customer_name):
    media_storage = PublicMediaStorage()
    meta_list = []
    customer = Customer.objects.get(name=customer_name)
    with ZipFile(customer.user_file_upload, 'r') as zipfile:
        zipfile.extractall()
        i = 1
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
                i += 1
        customer.meta_list[upload_name] = meta_list
        customer.save() # add the list of dictionaries to the database
        customer.user_file_upload.delete(save=False) # removes from postgresql, s3


"""
user_page, simple method for rendering the home page for the user.

:param request: the html request from teh template
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


@login_required(login_url='login') # Redirects user back to login page if they try to access a page without being logged in
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count() # Filter for orders trhat are delivered
    pending = orders.filter(status='Pending').count()

    context = {'orders': orders, 'customers': customers,
    'total_orders': total_orders, 'delivered':delivered,
    'pending':pending }
    
    return render(request, "plants/dashboard.html", context)


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


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, "plants/products.html", {'products': products })


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all() # Query customers child object from model
    order_count = orders.count()
   
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer':customer, 'orders':orders, 'order_count':order_count, 
               'myFilter':myFilter}
    return render(request, "plants/customer.html", context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    
    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save() # Saves into database
            return redirect('/') # Sends user back to dashboard

    context = {'formset':formset}
    return render(request, 'plants/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save() # Saves into database
            return redirect('/') # Sends user back to dashboard
    
    context = {'form':form}
    return render(request, 'plants/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == "POST":
        order.delete()
        return redirect('/')

    context = {'item':order}
    return render(request, 'plants/delete.html', context)