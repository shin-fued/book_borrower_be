from django.db import models
from base_models.models import BaseModel
from users.models import Roles

# Create your models here.


class Permission(BaseModel):
    class PermissionType(models.TextChoices):
        CREATE = "create", "Create"
        READ = "read", "Read"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    permission_type = models.CharField(
        max_length=10,
        choices=PermissionType.choices,
    )

    def __str__(self: "Permission") -> str:
        return self.name


class RolePermission(BaseModel):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("role", "permission")
