from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .serializers import UserSerializer
from .models import Users
from rest_framework import viewsets

class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "message": "User created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                "message": "User creation failed",
                "errors": e.detail  # includes field-specific errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message": "Unexpected error occurred",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "message": "User updated successfully",
                "data": serializer.data
            })
        except ValidationError as e:
            return Response({
                "message": "User update failed",
                "errors": e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message": "Unexpected error occurred",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def destroy(self, request, *args, **kwargs):
        
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "User deleted successfully 🗑️"
        }, status=status.HTTP_204_NO_CONTENT)
        
    #custom endpoint ie users/{id}/profile/
    @action(detail=True, methods=["get"])
    def profile(self, request, pk=None):
        user = self.get_object()
        return Response({
            "username": user.username,
            "email": user.email,
            "status": "active"
        })
        

# Create your views here.
