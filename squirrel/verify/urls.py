from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('sendotp/', views.sendotp, name='sendotp'),
    path('verifyme/<nvuser_id>', views.verifyme, name='verifyme'),
    path('sendotpagain/<nvuser_id>', views.sendotpagain, name='sendotpagain'),
]
