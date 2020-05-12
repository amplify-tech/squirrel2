from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from . import models
from user.models import *
from datetime import datetime
import pytz
from django.db.models import Q
utc=pytz.UTC
# from myuser.models import User
# from myuser.models import UserManager
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.

def howtouse(request,  user_id=None):
	return render(request, 'howtouse.html') 

    
def thatperson(request,  user_id=None):
	who = User.objects.all().filter(id=int(user_id))
	if len(who)!=0:
		srchprsn = who[0]
		myprofile = profile.objects.get(owner = srchprsn)
		return render(request, 'public_profile.html', {'profiles': myprofile}) 
	else:
		return HttpResponse("<h2> url not exist ! </h2> <p> May be this profile is private and you need to Login! </p>")
 

def search(request):
	Alluser = User.objects.all()
	num = len(Alluser)
	name = request.POST['fname']
	if len(name) <1:
		response = {"status":0, "url":"/", "msz":"atleast 1 character required"}
	elif len(name) >15:
		response = {"status":0, "url":"/", "msz":"maximum 15 characters"}
	elif not name.isalnum():
		response = {"status":0, "url":"/", "msz":"only alphanumeric characters allowed"}
	elif name.isnumeric() :
		newurl = '/public/' + name 
		response = {"status":1, "url":newurl, "msz":"id found,ok"}
	elif len(name) <3:
		response = {"status":0, "url":"/", "msz":"atleast 3 character required"}
	else:
		query = Q(fullname__icontains=name)
		query.add(Q(bio__icontains=name), Q.OR)
		query.add(Q(school__icontains=name), Q.OR)
		query.add(Q(hometown__icontains=name), Q.OR)
		query.add(Q(livesin__icontains=name), Q.OR)

		profilelist = profile.objects.all().filter(query)

		if len(profilelist)==0:
			response = {"status":0, "url":"/", "msz":"Person with this info not found"}
		else:
			newurl= "/public/filter_search/" + name
			response = {"status":1, "url":newurl, "msz":"profile found. ok. redirecting."}
	return JsonResponse(response, safe=False)

def filter_search(request, thename=None):
	if thename==None:
		redirect("/")
	else:
		query = Q(fullname__icontains=thename)
		query.add(Q(bio__icontains=thename), Q.OR)
		query.add(Q(school__icontains=thename), Q.OR)
		query.add(Q(hometown__icontains=thename), Q.OR)
		query.add(Q(livesin__icontains=thename), Q.OR)

		profilelist = profile.objects.all().filter(query)
		return render(request, 'public_home.html', {'profilelist': profilelist}) 
