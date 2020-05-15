from django.db import models
# from django.contrib.auth.admin import User
# from myuser.models import User
# from myuser.models import UserManager

from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.

def validate_file_size(value):
    filesize= value.size
    
    if filesize > 5242880:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    else:
        return value

class Chate(models.Model):
    sender = models.ForeignKey(User,on_delete=models.CASCADE)
    chatkey = models.TextField(default="")
    msz = models.TextField(default="")
    date = models.TextField(default="", blank=True)

class profile(models.Model):
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    fullname = models.TextField(default="")
    bio = models.TextField(default="")
    hometown = models.TextField(default="")
    school = models.TextField(default="")
    livesin = models.TextField(default="")
    isactive = models.BooleanField(default=False)
    all_notify = models.IntegerField(default=0)

class User_Following(models.Model):
    user_id = models.IntegerField(default=0)
    following = models.ForeignKey(User,on_delete=models.CASCADE)
    notification = models.IntegerField(default=0)

class User_Follower(models.Model):
    user_id = models.IntegerField(default=0)
    follower = models.ForeignKey(User,on_delete=models.CASCADE)
    notification = models.IntegerField(default=0)

class Profile_pic(models.Model): 
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    prof_pic = models.ImageField(upload_to='prof_pic/', verbose_name="", validators=[validate_file_size])

class Status(models.Model): 
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    status_pic = models.ImageField(upload_to='status_pic/', blank=True, verbose_name="", validators=[validate_file_size])
    status = models.TextField(default="I'm feeling lucky!")
    num_like = models.IntegerField(default=0)

class Likes(models.Model):
    status_id = models.IntegerField(default=0)
    who_like = models.ForeignKey(User,on_delete=models.CASCADE)

class Private_prof(models.Model):
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
