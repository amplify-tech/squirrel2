# forms.py 
from django import forms 
from .models import *

class Prof_form(forms.ModelForm): 

	class Meta: 
		model = Profile_pic 
		fields = ['prof_pic']

class Status_form(forms.ModelForm): 

	class Meta: 
		model = Status 
		fields = ['status_pic', 'status']
