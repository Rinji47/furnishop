from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=5, blank=True, null=True)
    address = models.CharField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)