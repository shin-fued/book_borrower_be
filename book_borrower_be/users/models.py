from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

class Users(AbstractUser):
    # Add any additional fields if necessary
    phone_number = PhoneNumberField(_("phone number"), unique=True)
    role = models.CharField(max_length=50, default='borrower')  # e.g., 'admin', 'borrower'
  
#abstract model user use that
  

class Meta:
        ordering = ["username"]
  