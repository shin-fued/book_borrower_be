from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Member(models.Model):
  username = models.CharField(max_length=255, unique=True)
  password = models.CharField(max_length=255)
  phone_number = models.PhoneNumberField(("phone number"), blank=True)
  role = models.CharField(max_length=50)
  created_at = models.DateTimeField(auto_now_add=True)
  
  