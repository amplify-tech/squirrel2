from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from . import models
from user.models import *
from public.models import *
from django.db.models import Q

from django.contrib.auth import get_user_model
User = get_user_model()

import re
regex="^[a-zA-Z0-9 ]+$"
# isaplanmsapce regex
helpdeskid=2
def howtouse(request):
	return render(request, 'howtouse.html') 

def faq(request):
	ishelp=False
	if request.user.is_authenticated: 
		if request.user.id == helpdeskid or request.user.id==1:
			ishelp=True

	allq = FAQ.objects.all().order_by("-id")
	allqans_list=[]
	for q in allq:
		allans = Answer.objects.filter(question=q).order_by("-id")
		allqans_list.append([q,allans])
	context = {"allqans_list": allqans_list, "ishelp":ishelp}
	return render(request, 'faq.html',context) 

   
def ask(request):
	question = request.POST['question']
	newq = FAQ(question=question)
	newq.save()
	return redirect("/public/faq")

def ansfaq(request):
	qid = request.POST['qid']
	answer = request.POST['ans']
	theQ = FAQ.objects.get(id=int(qid))

	newans = Answer(question=theQ, answer=answer)
	newans.save()
	return redirect("/public/faq")

def delq(request,qid=None):
	FAQ.objects.get(id=int(qid)).delete()
	return redirect("/public/faq")

def delans(request,ansid=None):
	Answer.objects.get(id=int(ansid)).delete()
	return redirect("/public/faq")

def thatperson(request, user_id=None):
	isexists = User.objects.filter(id=int(user_id)).exists()
	if isexists:
		srchprsn  = User.objects.get(id=int(user_id))
		isprivate = Private_prof.objects.filter(owner=srchprsn).exists()
		if isprivate:
			return HttpResponse("<h2> This profile is private and you need to Login! </h2>")
		else:
			myprofile = profile.objects.get(owner = srchprsn)
			return render(request, 'public_profile.html', {'profiles': myprofile}) 
	else:
		return HttpResponse("<h2> url not exist ! </h2>")
 

def search(request):
	Alluser = User.objects.all()
	num = len(Alluser)
	name1 = request.POST['fname']
	name = name1.strip()
	isalphnmspace = bool(re.match(regex,name))
	if len(name) <1:
		response = {"status":0, "url":"/", "msz":"atleast 1 character required"}
	elif len(name) >15:
		response = {"status":0, "url":"/", "msz":"maximum 15 characters"}
	elif not isalphnmspace:
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

		public_prof = profile.objects.all()
		allprivate=Private_prof.objects.all()
		for pp in allprivate:
			public_prof = public_prof.exclude(owner = pp.owner)

		profilelist = public_prof.filter(query)

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
		isalphnmspace = bool(re.match(regex,thename))
		if  not isalphnmspace:
			return HttpResponse("<h2> only alphanumeric characters allowed </h2>")
		elif len(thename) <3:
			return HttpResponse("<h2> atleast 3 characters required </h2>")
		else:
			query = Q(fullname__icontains=thename)
			query.add(Q(bio__icontains=thename), Q.OR)
			query.add(Q(school__icontains=thename), Q.OR)
			query.add(Q(hometown__icontains=thename), Q.OR)
			query.add(Q(livesin__icontains=thename), Q.OR)

			public_prof = profile.objects.all()
			allprivate=Private_prof.objects.all()
			for pp in allprivate:
				public_prof = public_prof.exclude(owner = pp.owner)

			profilelist = public_prof.filter(query)
			return render(request, 'public_home.html', {'profilelist': profilelist}) 