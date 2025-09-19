from ast import Tuple
from typing import Any, Dict, Optional
from urllib.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .serializers import RoleSerializer, UserRoleSerializer, UserSerializer
from .models import Roles, UserRole, Users
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"

    def create(
        self: "UserViewSet", request: Request, *args: object, **kwargs: object
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {"message": "User created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                {
                    "message": "User creation failed",
                    "errors": e.detail,  # includes field-specific errors
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": "Unexpected error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(
        self: "UserViewSet", request: Request, *args: any, **kwargs: any
    ) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})

    def retrieve(
        self: "UserViewSet", request: Request, *args: object, **kwargs: object
    ) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(
        self: "UserViewSet", request: Request, *args: object, **kwargs: object
    ) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {"message": "User updated successfully", "data": serializer.data}
            )
        except ValidationError as e:
            return Response(
                {"message": "User update failed", "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": "Unexpected error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(
        self: "UserViewSet", request: Request, *args: object, **kwargs: object
    ) -> Response:

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )

    # custom endpoint ie users/username/profile/
    @action(detail=True, methods=["get"])
    def profile(
        self: "UserViewSet", request: Request, username: Optional[str] = None
    ) -> Response:
        user = self.get_object()
        return Response(
            {
                "username": user.username,
                "phone_number": str(user.phone_number),
                "status": "active",
            }
        )

    # Get what books are borrowed by a specific user that are due


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RoleSerializer
    lookup_field = "name"
    filterset_fields = ["name"]


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    filterset_fields = ["user__username", "role__name"]
