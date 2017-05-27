from django.db import models

# Create your models here.

class workers(models.Model):

    name = models.CharField(max_length=30,unique=True)
