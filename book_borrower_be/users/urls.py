from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, UserRoleViewSet, UserViewSet

router = DefaultRouter()
router.register(r"role", RoleViewSet, basename="role")
router.register(r"", UserViewSet)
router.register(r"user-role", UserRoleViewSet, basename="user-role")

urlpatterns = [
    path("", include(router.urls)),
]
