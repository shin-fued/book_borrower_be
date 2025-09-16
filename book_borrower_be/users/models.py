from django.db import models

class Users(models.Model):
  username = models.CharField(max_length=255, unique=True)
  password = models.CharField(max_length=255)
  phone_number = models.CharField(max_length=20, unique=True)
  role = models.CharField(max_length=50)
  created_at = models.DateTimeField(auto_now_add=True)
  
  