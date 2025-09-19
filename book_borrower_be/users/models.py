from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from base_models.models import BaseModel


class Users(BaseModel, AbstractUser):
    # Add any additional fields if necessary
    phone_number = PhoneNumberField(_("phone number"), unique=True)

    class Meta:
        ordering = ["username"]


class Roles(BaseModel):
    class RoleType(models.TextChoices):
        ADMIN = "admin", "Admin"
        BORROWER = "borrower", "Borrower"
        STAFF = "staff", "Staff"

    name = models.CharField(max_length=50, unique=True, choices=RoleType.choices)

    def __str__(self: "Roles") -> str:
        return self.name


class UserRole(BaseModel):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)

    def __str__(self: "UserRole") -> str:
        return f"User {self.user_id} - Role {self.role.name}"
