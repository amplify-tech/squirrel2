from django.db import models
# from django.contrib.auth.admin import User

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

class nvuser(models.Model):
    email = models.EmailField(max_length = 60) 
    fullname = models.TextField(default="")
    lastname = models.TextField(default="")

class Email(models.Model):
    email = models.EmailField(max_length = 60) 
    num_try = models.IntegerField(default=0)
    otp_try = models.IntegerField(default=0)
    otp = models.IntegerField(default=487569)
