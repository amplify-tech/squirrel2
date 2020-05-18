import json
from django.http import JsonResponse
from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.contrib.auth.models import auth
# from myuser.models import User
# from myuser.models import UserManager
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import *
import re, csv
from datetime import datetime
import pytz
from .forms import *
from django.db.models import Q
from django.db.models import Sum
import string  
from django.contrib.auth import get_user_model
User = get_user_model()

allpunc = string.punctuation

tz = pytz.timezone('Asia/Kolkata')
helpdeskid = 2

def dashboard(request,  user_id=None):
    if request.user.is_authenticated: 
        if int(user_id) == request.user.id:
            user = request.user
            myprofile = profile.objects.get(owner = user)
            total_notify = myprofile.all_notify
            isprivate = Private_prof.objects.filter(owner=user).exists()

            form = Prof_form()
            status_form = Status_form()
            pictures = Profile_pic.objects.all().filter(owner=request.user).last()
            status = Status.objects.all().filter(owner=request.user).order_by('-id')
            status_likelist_islike=[]
            for i in status:
                islike =  Likes.objects.filter(status_id=i.id, who_like=user).exists()
                status_likelist_islike.append([i,islike])

            context= {'profile':myprofile, 'form' : form,  'status_form' : status_form,
                    'pimages' : pictures, 'status':status_likelist_islike,
                    'all_notify':total_notify, "isprivate":isprivate}
            return render(request, 'profile.html', context) 

    return redirect("/")

def chat(request,  user_id=None , ricvr_id=None) :
    if request.user.is_authenticated: 
        if int(user_id) == request.user.id:
            user = request.user
            myprofile = profile.objects.get(owner = user)
           
            if int(ricvr_id) == int(user_id):

                total_notify = myprofile.all_notify
                thischat_key= str(user_id+"@"+user_id)
                oldchat = Chate.objects.all().filter(chatkey=thischat_key)

                context = {'ourchat': oldchat ,'rcvr': user,
                'rcvr_id':user.id, 'all_notify':total_notify, 'chat_key':thischat_key}
                return render(request, 'chat.html', context)

            else:
                # now he is reading msz so remove some notification

                ricvr = User.objects.get(id=int(ricvr_id))
                isprivate = Private_prof.objects.filter(owner=ricvr).exists()
                isflwing = User_Following.objects.filter(user_id=user.id, following=ricvr).exists()
                isflwer = User_Follower.objects.filter(user_id=user.id, follower=ricvr).exists()
                if int(ricvr_id)==1 or int(ricvr_id)==helpdeskid :
                    isflwing=True
                    isflwer= True

                if int(user_id)==1 or int(user_id)==helpdeskid :
                    isflwing=True
                    isflwer= True

                if  isprivate and (not isflwing) and (not isflwer):
                    return HttpResponse("<h2> This account is private </h2>")
                if  (not isflwing) and (not isflwer):
                    return HttpResponse("<h2> you can only chat with your following/follower</h2>")
                else:

                    thischat_key =  str(min(user.id, int(ricvr_id))) + "@" + str(max(user.id, int(ricvr_id)))

                    oldchat = Chate.objects.all().filter(chatkey=thischat_key)

                    # notifiction  --n     ********************************
                    n1 = 0
                    n2 = 0 
                    # following
                    flwing = User_Following.objects.all().filter(user_id=user.id, following=ricvr)
                    if len(flwing) != 0:
                        flwing1 = flwing[0]
                        n1 = flwing1.notification
                        flwing1.notification = 0
                        flwing1.save()

                    # followers
                    flwer = User_Follower.objects.all().filter(user_id=user.id, follower=ricvr)
                    if len(flwer) != 0:
                        flwer1 = flwer[0]
                        n2 = flwer1.notification
                        flwer1.notification = 0
                        flwer1.save()

                    # all notify**********************
                    myprofile.all_notify = myprofile.all_notify - max(n1, n2)   #hopefully n1=n2
                    myprofile.save()

                    total_notify2 = myprofile.all_notify
                    # **************************************************
                    context = {'ourchat': oldchat ,'rcvr': ricvr,
                    'rcvr_id':ricvr_id, 'all_notify':total_notify2, 'chat_key':thischat_key}
                    return render(request, 'chat.html', context)
    
    return redirect("/")


def myfrnd(request,  user_id=None) :
    if request.user.is_authenticated: 
        if int(user_id) == request.user.id:
            user = request.user
            myprofile = profile.objects.get(owner = user)
            
            # following
            if int(user_id) == helpdeskid:
                ishelp=True
                allproblem=[]
                alluser=User.objects.all()
                for uu in alluser:
                    thischat_key =  str(min(uu.id, helpdeskid)) + "@" + str(max(uu.id, helpdeskid))
                    nummsz = len( Chate.objects.filter(chatkey = thischat_key) )
                    allproblem.append([uu,nummsz])
            else:
                allproblem=[]
                ishelp=False

            flwing = User_Following.objects.all().filter(user_id=user.id)
            
            query = Q(owner=user)
            profile_flwing=[]
            for i in flwing:
                query.add(Q(owner=i.following), Q.OR)
                hisprofile = profile.objects.get(owner = i.following)
                profile_flwing.append([i , hisprofile])

            # follower       list of pair 
            flwer = User_Follower.objects.all().filter(user_id=user.id)
           
            # all notification

            pstiveflwing = flwing.filter(notification__gt=0).values('following_id', 'notification')
            pstiveflwer = flwer.filter(notification__gt=0).values('follower_id','notification')
            notfy_union = pstiveflwing.union(pstiveflwer)
            l = list(notfy_union)
            total_notify = sum([x['notification'] for x in l])

            myprofile.all_notify =  total_notify
            myprofile.save()


            profile_flwer=[]
            for i in flwer:
                himprofile = profile.objects.get(owner = i.follower)
                profile_flwer.append([i , himprofile])

            allstatus = Status.objects.all().filter(query).order_by('-id')
            status_likelist_islike=[]
            for i in allstatus:
                islike = Likes.objects.filter(status_id=i.id,who_like=user).exists()
                status_likelist_islike.append([i,islike])


            context =  { 'ishelp':ishelp, 'allproblem':allproblem, 'allfollowing': profile_flwing, 'allfolower': profile_flwer,
                        'all_notify':total_notify, 'status':status_likelist_islike}

            return render(request, 'myfrnd.html', context)
    
    return redirect("/")

def findfrnd(request,  user_id=None) :
    if request.user.is_authenticated: 
        if int(user_id) == request.user.id:
            user = request.user
            myprofile = profile.objects.get(owner = user)
            total_notify = myprofile.all_notify
            myflwing = User_Following.objects.all().filter(user_id=user.id)
            all_users = User.objects.all().exclude(id=user.id)
            for f in myflwing:
                all_users=all_users.exclude(id=f.following.id)   
                 #remove those are already  following

            all_private = Private_prof.objects.all()
            for pp in all_private:
                all_users=all_users.exclude(id=pp.owner.id)   
                 #remove those are already  following

            all_users = all_users.order_by('first_name')
            return render(request, 'findfrnd.html', {'alluser': all_users, 'all_notify':total_notify})

    return redirect("/")

def saveprofile(request,user_id=None ):
    user = request.user
    myprofile = profile.objects.get(owner = user)

    bio = request.POST['bio']
    livesin = request.POST['livesin']
    hometown = request.POST['hometown']
    school = request.POST['school']
    fullname = request.POST['fullname']

    myprofile.fullname = fullname
    myprofile.bio = bio
    myprofile.livesin = livesin
    myprofile.hometown = hometown
    myprofile.school = school
    myprofile.save()

    user.first_name = fullname
    user.save()
    return redirect('/user/' +str(request.user.id))

def following(request,user_id=None ):
    user = request.user
    ideal_user_id = request.POST['idealid']
    ideal_user = User.objects.get(id=int(ideal_user_id))

    # following **************************************************
    newflwing = User_Following(user_id = user.id, following = ideal_user, notification=0)
    newflwing.save()

    # # follower ***************************************************
    newflwr = User_Follower(user_id = ideal_user.id, follower = user, notification=0)
    newflwr.save()

    return HttpResponse("success")


def delete_flwing(request,user_id=None ):
    user = request.user
    myprofile = profile.objects.get(owner = user)
    whom = request.POST['idealid']
    his_profile = profile.objects.get(owner = int(whom))

    flwinglist = User_Following.objects.filter(user_id=user.id, following=int(whom))
    if len(flwinglist) !=0:
        myprofile.all_notify =myprofile.all_notify -  flwinglist[0].notification
        flwinglist.delete()

    flwerlist = User_Follower.objects.filter(user_id=int(whom), follower=user.id)
    if len(flwerlist) !=0:
        his_profile.all_notify =his_profile.all_notify -  flwerlist[0].notification
        flwerlist.delete()

    myprofile.save()
    his_profile.save()

    return HttpResponse("success")

def delete_flwer(request,user_id=None ):
    user = request.user
    whom = request.POST['flwer_del_id']

    myprofile = profile.objects.get(owner = user)
    his_profile = profile.objects.get(owner = int(whom))

    flwerlist = User_Follower.objects.filter(user_id=user.id, follower=int(whom))
    if len(flwerlist) !=0:
        myprofile.all_notify =myprofile.all_notify -  flwerlist[0].notification
        flwerlist.delete()

    flwinglist = User_Following.objects.filter(user_id=int(whom), following=user.id)
    if len(flwinglist) !=0:
        his_profile.all_notify =his_profile.all_notify -  flwinglist[0].notification
        flwinglist.delete()

    myprofile.save()
    his_profile.save()

    return HttpResponse("success")


def chat_del(request,user_id=None,  ricvr_id=None):
    user = request.user
    thischat_key = request.POST['chate_key_del']

    Chate.objects.all().filter(chatkey = thischat_key).delete()

    return HttpResponse("success")

def prof_del(request,user_id=None):
    if request.user.is_authenticated: 
        if int(user_id) == request.user.id:
            user = request.user
            profile.objects.all().filter(owner = user).delete()
            Chate.objects.all().filter(sender= user).delete()
            User_Following.objects.all().filter(user_id= user.id).delete()
            User_Following.objects.all().filter(following= user).delete()
            User_Follower.objects.all().filter(user_id= user.id).delete()
            User_Follower.objects.all().filter(follower= user).delete()
            Profile_pic.objects.all().filter(owner= user).delete()
            Status.objects.all().filter(owner= user).delete()
            User.objects.all().filter(id= user.id).delete()

            return render(request, 'home.html')

    return redirect("/")


def viewprofile(request,user_id=None, ricvr_id=None ):
    if request.user.is_authenticated: 
        if int(user_id) == request.user.id:

            user = request.user
            # who_id = request.POST['userid_view']
            whose_user = User.objects.get(id=int(ricvr_id))
            whose_profile = profile.objects.get(owner=whose_user)
            status = Status.objects.all().filter(owner=whose_user).order_by('-id')
            status_likelist_islike=[]
            for i in status:
                islike =  Likes.objects.filter(status_id=i.id, who_like= user).exists()
                status_likelist_islike.append([i,islike])

            pictures = Profile_pic.objects.all().filter(owner=whose_user).last()
            num_flwing= User_Following.objects.all().filter(user_id=int(ricvr_id)).count()
            num_flwer= User_Follower.objects.all().filter(user_id=int(ricvr_id)).count()

            isprivate = Private_prof.objects.filter(owner=whose_user).exists()
            isflwing = User_Following.objects.filter(user_id=user.id, following=whose_user).exists()
            isflwer = User_Follower.objects.filter(user_id=user.id, follower=whose_user).exists()

            isprivate= isprivate and (not isflwer) and (not isflwing)

            context = {'whose_profile' :whose_profile, 'status':status_likelist_islike,
                        'pimages':pictures, 'num_flwing':num_flwing,
                        'num_flwer':num_flwer, "isprivate":isprivate}
            return render(request, 'viewprofile.html' ,context)

    return redirect("/")


def send_msz(request,user_id=None):
    user = request.user
    last_msz_id = request.POST['last_msz_id']
    curmsz = request.POST['mymsz']
    chat_key = request.POST['chat_key']
    rcvr = request.POST['rcvr_id']
    
    newstr = curmsz
    newmsz_list = []
    for c in curmsz:
        if c =='\n':
            newmsz_list.append("<br>")
        elif c ==' ':
            newmsz_list.append("&nbsp;")
        elif c =='\t':
            newmsz_list.append("&nbsp; &nbsp; &nbsp; &nbsp;")

        elif c.isalnum():
            newmsz_list.append(c)
        elif c in allpunc:
            newmsz_list.append(c)
        else:
            newmsz_list.append(str(' &#x{:X}; '.format(ord(c))))

    newmsz = ''.join(newmsz_list)


    if len(newstr.strip()) == 0:
        pass
    elif int(rcvr)==user.id:
        tempdate = datetime.now(tz).strftime("%a %-d %b, %-I:%M %p")
        msz1 = Chate(sender=user, chatkey=chat_key, msz=newmsz, date=tempdate)
        msz1.save()

    else:
        # notifiction  +1     ********************************
        # following
        flwing = User_Following.objects.all().filter(user_id=int(rcvr), following=user)
        if len(flwing) != 0:
            flwing1 = flwing[0]
            flwing1.notification = flwing1.notification + 1
            flwing1.save()

        # followers
        flwer = User_Follower.objects.all().filter(user_id=int(rcvr), follower=user)
        if len(flwer) != 0:
            flwer1 = flwer[0]
            flwer1.notification = flwer1.notification + 1
            flwer1.save()
        # all notify**********************

        user_ricvr = User.objects.get(id=int(rcvr))
        rcvr_profile = profile.objects.get(owner = user_ricvr)
        rcvr_profile.all_notify =  rcvr_profile.all_notify  + 1
        rcvr_profile.save()
        # **************************************************

        
        tempdate = datetime.now(tz).strftime("%a %-d %b, %-I:%M %p")
        msz1 = Chate(sender=user, chatkey=chat_key, msz=newmsz, date=tempdate)
        msz1.save()

    last_msz_id1 = int(last_msz_id)
    after_chat = list(Chate.objects.all().filter(chatkey=chat_key, pk__gt=last_msz_id1).order_by('id').values())
    return JsonResponse(after_chat, safe=False)

def check_msz(request,user_id=None):
    last_msz_id = request.POST['last_msz_id']
    chat_key = request.POST['chat_key']

    last_msz_id1 = int(last_msz_id)
    after_chat = list(Chate.objects.all().filter(chatkey=chat_key, pk__gt=last_msz_id1).order_by('id').values())
    return JsonResponse(after_chat, safe=False)

def find_all_liker(request,user_id=None):
    status_id = request.POST['status_id']
    status_id1 = int(status_id)

    all_liker = list(Likes.objects.all().filter(status_id=status_id1).order_by('id').values('who_like__first_name','who_like'))
    return JsonResponse(all_liker, safe=False)

def update_pic(request, user_id=None): 
    if request.method == 'POST': 
        form = Prof_form(request.POST, request.FILES) 
        if form.is_valid():
            temp = form.save(commit=False) 
            temp.owner = request.user
            temp.save()

            # return redirect('success') 
    else: 
        form = Prof_form()
    return redirect('/user/' +str(request.user.id))


def update_status(request, user_id=None): 
    if request.method == 'POST': 
        form = Status_form(request.POST, request.FILES) 
        if form.is_valid(): 
            temp = form.save(commit=False) 
            temp.owner = request.user
            temp.save()

            # return redirect('success') 
    else: 
        form = Status_form()
    return redirect('/user/' +str(request.user.id)+"#posts")


def likes(request, user_id=None):
    status_id = request.POST['status_id']
    oldlike, newlike = Likes.objects.get_or_create(status_id=int(status_id), who_like=request.user)

    if newlike:
        the_status = Status.objects.get(id=int(status_id))
        the_status.num_like +=1
        numlike = the_status.num_like
        the_status.save()

    else:
        oldlike.delete()
        the_status = Status.objects.get(id=int(status_id))
        the_status.num_like -=1
        numlike = the_status.num_like
        the_status.save()

    return HttpResponse(numlike) # Sending an success response

def other_likes(request, user_id=None, ricvr_id=None ):
    status_id = request.POST['status_id']

    oldlike, newlike = Likes.objects.get_or_create(status_id=int(status_id), who_like=request.user)

    if newlike:
        the_status = Status.objects.get(id=int(status_id))
        the_status.num_like +=1
        the_status.save()

    else:
        oldlike.delete()
        the_status = Status.objects.get(id=int(status_id))
        the_status.num_like -=1
        the_status.save()

    return redirect('/user/' +str(request.user.id) + "/viewprofile/"+ str(ricvr_id) + "#" + str(status_id))


def del_status(request, user_id=None):
    status_id = request.POST['status_id']
    
    the_status = Status.objects.get(id=int(status_id))
    the_status.delete()
    Likes.objects.filter(status_id=int(status_id)).delete()
    return HttpResponse("success") # Sending an success response

def del_prof_pic(request, user_id=None):
    Profile_pic.objects.all().filter(owner=request.user).delete()

    return redirect('/user/' +str(request.user.id))


def makeprivate(request, user_id=None):
    if request.user.is_authenticated: 
        if int(user_id) == request.user.id:
            user = request.user
            if Private_prof.objects.filter(owner=user).exists() :
                thprof =Private_prof.objects.get(owner=user)
                thprof.delete();
            else:
                newprv = Private_prof(owner=user)
                newprv.save()

            return HttpResponse("success")


    return redirect("/")


# imp ++++++++++++++++++++++++********************************
# id = 'some identifier'
# person, created = Person.objects.get_or_create(identifier=id)

# if created:
#    # means you have created a new person
# else:
#    # person just refers to the existing one
