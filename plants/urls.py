from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Login/Registration
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    # Dashboard
    path('', views.home, name="home"),
    path('user/', views.userPage, name="user-page"),
    path('account/', views.accountSettings, name="account"),
    path('products', views.products, name="products"),
    path('customer/<str:pk>/', views.customer, name="customer"),
    
    # File Upload
    path('image_upload', views.image_upload, name="image_upload"),

    # CRUD
    path('create_order/<str:pk>/', views.createOrder, name="create_order"),
    path('update_order/<str:pk>/', views.updateOrder, name="update_order"),
    path('delete_order/<str:pk>/', views.deleteOrder, name="delete_order"),

    # Password reset stuff
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="plants/password_reset.html"),
    name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="plants/password_reset_sent.html"),
    name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="plants/password_reset_form.html"), 
    name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="plants/password_reset_done.html"), 
    name="password_reset_complete"),
]   
