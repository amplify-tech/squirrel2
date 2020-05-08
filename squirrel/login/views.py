from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models
from user.models import *
# from myuser.models import User
# from myuser.models import UserManager
from login.models import *
from django.contrib.auth.models import User, auth
from django.contrib import messages
# Create your views here.
from django.contrib.auth import get_user_model
User = get_user_model()

def home(request):
    if request.user.is_authenticated:
        return redirect('/user/' +str(request.user.id))
    else:
        all_users = User.objects.all()
        num = len(all_users)
        return render(request, 'home.html' , {'numuser' : num})

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        paswd = request.POST['pswd']

        user = auth.authenticate(email=email, password=paswd)

        if user is not None:
            auth.login(request,user)
            myprofile = profile.objects.get(owner = user)
            myprofile.isactive = True
            myprofile.save()
            return redirect('/user/' +str(user.id))
        else:
            messages.info(request, 'Invalid email or Password')
            return redirect('/login')

    else:
        return render(request, 'login.html')
        

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        fullname = request.POST['fullname']
        passwd = request.POST['pswd']
        passwd1 = request.POST['pswd1']

        if User.objects.filter(email=email).exists():
            messages.info(request, 'email Taken')
            return redirect('register')
        elif passwd != passwd1:
            messages.info(request, 'password not match')
            return redirect('register')
        else:
            user = User.objects.create_user(email=email,first_name=fullname ,password=passwd)
            user.save()
            print("proflie created")
            newprofile = profile(owner=user , fullname=fullname)
            newprofile.save()
            return redirect('login')

    else:
        return render(request, 'register.html')

def logout(request):
    print("logout")
    user = request.user
    myprofile = profile.objects.get(owner = user)
    myprofile.isactive = False
    myprofile.save()
    auth.logout(request)
    return redirect('/')
