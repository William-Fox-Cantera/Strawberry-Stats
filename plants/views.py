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
from PIL import Image
"""
farm_view, this function renders the view for the "farm" in which the data is displayed.

:param request: the html request from the template farmville.html
"""
def farm_view(request, pk):
    customer = Customer.objects.get(id=pk)
    user_upload = customer.user_file_upload
    with ZipFile(user_upload, 'r') as zipfile:
        zipfile.extractall()
        meta_list = []
        i = 0
        zipfile.printdir()
        for filename in zipfile.namelist(): 
            if filename.endswith(".jpg"): # Other files shouldn't be trusted
                exif_dict = piexif.load("testImages/" + str(i) + '.jpg')

                data = zipfile.read("temp/" + str(i) + '.jpg')
                dataEnc = BytesIO(data)
                img = Image.open(dataEnc)
                print(img)
                media_storage = PublicMediaStorage()
                
                media_storage.save('Sam/hi.jpg', dataEnc)
                break
                comment = piexif.helper.UserComment.load(exif_dict['Exif'][piexif.ExifIFD.UserComment])
                meta_dict = json.loads(comment)
                meta_dict["image"] = filename
                meta_list.append(meta_dict) # list of dictionaries containing the meta data 
                i += 1

    context = {"meta":meta_list}
    return render(request, "plants/farmville.html", context)



"""
csv_upload, this function renders the user page for uploading a csv file into the database.
            If the has_started boolean is false, it just displays a start button to get 
            the user, started. Otherwise it displays the form for submitting the files.

:param request: the html request from the template user.html
:param has_started: boolean, true if the start button has been pressed yet
"""
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def csv_upload(request, has_started="False"):
    customer = request.user.customer
    form = CustomerFileUploadForm(instance=customer)
    if has_started == "False": # Just render the form if the start button is pressed
        return render(request, "plants/user.html", {'form':form, 'should_generate':True, 'customer':customer})
    else:
        if request.method == 'POST':
            form = CustomerFileUploadForm(request.POST, request.FILES, instance=customer)
            name = ""
            for filename, file in request.FILES.items():
                name = request.FILES[filename].name

            if form.is_valid() and name.endswith(".zip"):
                messages.success(request, name + " Successfully Uploaded")
                upload = form.save()
                return render(request, 'plants/user.html', {'form':form, 'should_generate':True, 'customer':customer})
            else:
                messages.error(request, "Please upload a file ending with \".zip\"")
        else: # If not a post, make a blank form 
            form = CustomerFileUploadForm()

        context = { 'form':form, 'should_generate':True, 'customer':customer,
                    'total_plants':100, 'date_captured':"6/16/2020",
                    'percent_flowered':"60%" }
        return render(request, 'plants/user.html', context)


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