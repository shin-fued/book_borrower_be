from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from users.serializers import RoleSerializer

from .models import (
    Permission,
    RolePermission,
)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "description", "permission_type"]


class RolePermissionSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    permission = PermissionSerializer(read_only=True)

    class Meta:
        model = RolePermission
        fields = ["id", "role", "permission"]
