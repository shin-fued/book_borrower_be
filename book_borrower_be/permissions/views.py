from rest_framework import viewsets

from .serializers import PermissionSerializer, RolePermissionSerializer
from .models import Permission, RolePermission


# Create your views here.
class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    lookup_field = "name"
    filterset_fields = ["name", "permission_type"]


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    filterset_fields = ["role__name", "permission__name"]
