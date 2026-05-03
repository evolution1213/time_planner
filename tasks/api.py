from rest_framework import mixins, permissions, viewsets

from .models import Task
from .serializers import TaskSerializer


class IsOwnerPermission(permissions.BasePermission):
    """Allow access only to the owner of the object."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class TaskViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """API endpoint that allows users to manage their own tasks."""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]

    def get_queryset(self):
        # Restrict task access to the logged-in user only.
        return Task.objects.filter(owner=self.request.user).select_related('category', 'owner')

    def perform_create(self, serializer):
        # Automatically associate the task with the current user.
        serializer.save(owner=self.request.user)
