from django.db import models

# Create your models here.


class Workers(models.Model):

    name = models.CharField(max_length=30,unique=True)
