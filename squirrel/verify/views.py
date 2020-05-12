from django.http import JsonResponse
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from user.models import profile
from datetime import datetime
import pytz
from django.core.mail import send_mail
from django.conf import settings
from random import randint
from django.contrib.auth import get_user_model
User = get_user_model()

tz = pytz.timezone('Asia/Kolkata')
import re 
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
# email regex

vrfystr="sxawnvryqzof"
def makestr(x):
	str1 = str(x)
	str2="vrf"
	for c in str1:
		str2+=vrfystr[int(c)]
	str2+="dnxkegl"
	return str2
# use decad(makestr(num)[3:-7])
def decad(mkstr):
	strr=""
	for c in mkstr:
		strr+=str(vrfystr.find(c))
	return strr

def check(email): 
	if(re.search(regex,email)): 
		return True	
	else: 
		return False

def home(request):
    if request.user.is_authenticated:
        return redirect('/user/' +str(request.user.id))
    else:
        all_users = User.objects.all()
        num = len(all_users)
        return render(request, 'home.html' , {'numuser' : num})

def login(request):
    if request.method == 'POST':
        email = request.POST['email_login']
        paswd = request.POST['pswd_login']
        if len(email) <5 or len(email)>40:
            messages.info(request, 'Invalid Email')
            return redirect('/')
        elif len(paswd) <5 or len(paswd)>25:
            messages.info(request, 'Incorrect Password')
            return redirect('/')
        else:
	        user = auth.authenticate(email=email, password=paswd)

	        if user is not None:
	            auth.login(request,user)
	            myprofile = profile.objects.get(owner = user)
	            myprofile.isactive = True
	            myprofile.save()
	            return redirect('/user/' +str(user.id))
	        else:
	            messages.info(request, 'Invalid Email or Password')
	            return redirect('/#heading')

    else:
        return render(request, '/')


def logout(request):
    user = request.user
    myprofile = profile.objects.get(owner = user)
    myprofile.isactive = False
    myprofile.save()
    auth.logout(request)
    return redirect('/')


def email_send(email):
	theemail=Email.objects.get(email=email)
	the_nvuser = nvuser.objects.get(email=email)

	name=the_nvuser.fullname
	num=theemail.otp

	subject = "Email Address Verification for Squirrel"
	oldmsz ="""Hello {}
  your OTP for email verification on Squirrel is 

  OTP : {} 
  email : {}

  Thank you for using Squirrel
  Squirrel Team


If you didn't add this email to your Squirrel Account,
ignore this email and that address won't be added to your Squirrel Account.
Someone may have made a mistake typing their own email address.
without this OTP no one can be able to register this email on Squirrel.


  https://squirrel.pythonanywhere.com/ """

	newmsz = oldmsz.format(name,num,email)

	message = str(newmsz)

	email_from = settings.EMAIL_HOST_USER
	recipient_list = [str(email),]
	try:
		x = send_mail( subject, message, email_from, recipient_list,fail_silently=False, )
		if x>0:
			return True
		else:
			return False
	except Exception:
		return False



def verifyme(request,  nvuser_id=None):
	decadme = decad(nvuser_id[3:-7])
	if decadme.isnumeric():
		if Email.objects.filter(id=int(decadme)).exists():
			theemail=Email.objects.get(id=int(decadme))
			if request.method == 'POST':
				num = request.POST['num']
				if int(num)==theemail.otp:
					the_nvuser = nvuser.objects.get(email=theemail.email)
					vuser = User.objects.create_user(email=the_nvuser.email,first_name=the_nvuser.fullname ,password=the_nvuser.lastname)
					vuser.save()
					newprofile = profile(owner=vuser , fullname=the_nvuser.fullname, isactive=True)
					newprofile.save()

					temp1 = the_nvuser.email
					temp2 = the_nvuser.lastname
					user = auth.authenticate(email=temp1, password=temp2)
					auth.login(request,user)

					nvuser.objects.filter(email=temp1).delete()
					Email.objects.filter(email=temp1).delete()

					return redirect('/user/'+str(vuser.id))
				else:
					itsmsz=" wrong OTP! now you have "+ str(5-theemail.otp_try) + " attempts"
					messages.info(request, itsmsz)
					theemail.otp_try+=1
					theemail.save()
					return redirect("/verifyme/" + str(nvuser_id))

			elif theemail.otp_try>5 :
				myalert="<h2> you tried 5 times invalid OTP :( try again after 24hrs :) </h2>"
				return HttpResponse(myalert)
			elif theemail.num_try>3:
				myalert="<h2> we sent you OTP 3 times on your registered email,each time you entered wrong OTP :( try again after 24hrs :) </h2>"
				return HttpResponse(myalert)
			else:
				action = "/verifyme/" + str(nvuser_id)
				action2= "/sendotpagain/" + str(nvuser_id)
				context={"theemail":theemail, "action":action, "action2":action2} 
				return render(request, 'verifyme.html', context)
		else:
			return HttpResponse("<h2> url not exist !!! </h2>")
	else:
		return HttpResponse("<h2> url not exist ! </h2>")

def sendotp(request,  nvuser_id=None):
	myname = request.POST['myname']
	myemail = request.POST['myemail']
	mypswd1 = request.POST['mypswd1']
	mypswd2 = request.POST['mypswd2']
	msz=""
	valid=True
	if len(myname) <4 or len(myname)>25 :
		valid=False
		msz+="fullname should be 4-25 char long. "
	if len(mypswd1) <4 or len(mypswd1)>25 :
		valid=False
		msz+="password should be 4-25 char long. "
	if len(mypswd2) <4 or len(mypswd2)>25 :
		valid=False
		msz+="password should be 4-25 char long. "
	if mypswd2 != mypswd1:
		valid=False
		msz+="password not match. "
	if not check(myemail):
		valid=False
		msz+="Invalid email. "

	if User.objects.filter(email=myemail).exists():
		valid=False
		msz+="this email is already taken. "

	if(valid):
		cur_otp = randint(134154, 948752)
		if Email.objects.filter(email=myemail).exists():
			oldemail = Email.objects.get(email=myemail)
			oldemail.email=myemail
			oldemail.num_try+=1
			oldemail.otp=cur_otp
			oldemail.save()
			alrdysend=oldemail.num_try
			newurl =  "/verifyme/" + makestr(oldemail.id)
		else:
			newemail = Email(email=myemail,num_try=1,otp_try=1,otp=cur_otp)
			newemail.save()
			alrdysend=1
			newurl =  "/verifyme/" + makestr(newemail.id)

		if nvuser.objects.filter(email=myemail).exists():
			old_nvuser = nvuser.objects.get(email=myemail)
			old_nvuser.email=myemail
			old_nvuser.fullname=myname
			old_nvuser.lastname=mypswd1
			old_nvuser.save()
		else:
			new_nvuser = nvuser(email=myemail,fullname=myname,lastname=mypswd1)
			new_nvuser.save()

		if alrdysend<=3:

			ismail_send = email_send(myemail)
			if ismail_send:
				response = {"status":"valid", "msz":"OTP sent, check your mail", "url":newurl}
			else:
				errormsz = """there is some problem in sending the mail!
				 Either the email you provided does not exists or 
				 there is a problem with the mail server.
				 Try later with a valid email :) """
				response = {"status":"invalid", "msz":errormsz, "url":"/"}
		else:
			response = {"status":"valid", "msz":"3 times sent", "url":newurl}

	else:
		response = {"status":"invalid", "msz":msz, "url":"/"}
	return JsonResponse(response, safe=False)


def sendotpagain(request,  nvuser_id=None):
	decadme = decad(nvuser_id[3:-7])
	if decadme.isnumeric():
		if Email.objects.filter(id=int(decadme)).exists():
			cur_otp = randint(134154, 948752)
			theemail=Email.objects.get(id=int(decadme))
			theemail.num_try+=1
			theemail.otp = cur_otp
			theemail.save()
			if theemail.num_try<=3:
				email_send(theemail.email)
			return redirect("/verifyme/"+ str(nvuser_id))

		else:
			return HttpResponse("<h2> url not exist !!! </h2>")
	else:
		return HttpResponse("<h2> url not exist ! </h2>")
