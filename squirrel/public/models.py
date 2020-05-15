from django.db import models

class FAQ(models.Model):
    question = models.TextField(default="")

class Answer(models.Model):
    question = models.ForeignKey(FAQ,on_delete=models.CASCADE)
    answer = models.TextField(default="")

