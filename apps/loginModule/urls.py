from django.urls import path
from . import views
app_name = 'loginModule'
urlpatterns = [
    path('login/', views.loginPage, name='loginPage'),
    path('register/', views.registerPage, name='registerPage'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('sendEmail/', views.sendEmail, name='sendEmail'),
    path('registerCheck/', views.registerCheck, name='registerCheck'),
    path('loginCheck/', views.loginCheck, name='loginCheck'),
]