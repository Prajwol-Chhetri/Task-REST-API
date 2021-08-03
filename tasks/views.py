from django.http import request
from rest_framework import viewsets, mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from core.models import Task

from tasks import serializers


class TaskViewSet(viewsets.ModelViewSet):
    """Manage tasks in the database"""
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return serializers.AdminTaskSerializer
        return serializers.TaskSerializer

    def get_queryset(self):
        """Retrieve the tasks for the authenticated user"""
        if self.request.user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new task"""
        if self.request.user.is_superuser:
            serializer.save()
        else:
            serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Update a existing task"""
        if self.request.user.is_superuser:
            serializer.save()
        else:
            serializer.save(user=self.request.user)





