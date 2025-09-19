from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PermissionViewSet, RolePermissionViewSet

router = DefaultRouter()
router.register(r"", PermissionViewSet)
router.register(r"role-permission", RolePermissionViewSet, basename="role-permission")

urlpatterns = [
    path("", include(router.urls)),
]
