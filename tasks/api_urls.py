from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api import TaskViewSet

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
