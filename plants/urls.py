from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # AJAX
    url(r'^ajax/save_favorite_plants/$', views.save_favorite_plants, name='save_favorite_plants'),
    url(r'^ajax/remove_plant_index/$', views.remove_plant_index, name='remove_plant_index'),
    url(r'^ajax/saveAreaForm/$', views.saveAreaForm, name='saveAreaForm'),
    url(r'^ajax/get_area_form/$', views.get_area_form, name='get_area_form'),
    url(r'^ajax/get_field_permissions/$', views.get_field_permissions, name='get_field_permissions'),

    # Login/Registration
    path('register/', views.registerPage, name="register"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    # Dashboard
    path('', views.home, name="home"),
    path('account/', views.accountSettings, name="account"),
    path('user-page/', views.user_page, name="user-page"),
    path('admin-input/<str:pk>/', views.admin_input, name="admin-input"),
    
    # File Upload
    path('zip_upload/', views.zip_upload, name="zip_upload"),
    path('zip_upload/<str:destination>/', views.zip_upload, name="zip_upload"),

    # Admin field info 
    path('save_field_form/', views.save_field_form, name="save_field_form"),
    path('delete_field_form/<str:fieldname>/', views.delete_field_form, name="delete_field_form"),

    # CRUD
    path('delete_zip_upload/', views.delete_zip_upload, name="delete_zip_upload"),
    path('delete_zip_upload/<str:filename>/', views.delete_zip_upload, name="delete_zip_upload"),

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
