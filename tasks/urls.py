from django.urls import path

from . import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task_list'),
    path('new/', views.TaskCreateView.as_view(), name='task_create'),
    path('stats/', views.TaskStatsView.as_view(), name='task_stats'),
    path('task/<int:pk>/status/', views.TaskStatusUpdateView.as_view(), name='task_change_status'),
    path('task/<int:pk>/toggle/', views.TaskToggleDoneView.as_view(), name='task_toggle_done'),
    path('task/<int:pk>/start/', views.TaskStartTimerView.as_view(), name='task_start_timer'),
]