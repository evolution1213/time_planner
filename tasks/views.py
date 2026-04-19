import json
from datetime import timedelta

from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import TaskForm
from .models import Task


class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    queryset = Task.objects.select_related('category').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        next_week = today + timedelta(days=7)
        tasks = self.object_list

        context.update({
            'Task': Task,
            'overdue_tasks': tasks.filter(deadline__lt=today).exclude(status=Task.Status.DONE),
            'today_tasks': tasks.filter(deadline=today).exclude(status=Task.Status.DONE),
            'week_tasks': tasks.filter(deadline__gt=today, deadline__lte=next_week).exclude(status=Task.Status.DONE),
            'future_tasks': tasks.filter(deadline__gt=next_week).exclude(status=Task.Status.DONE),
        })
        return context


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')


class TaskStatsView(TemplateView):
    template_name = 'tasks/task_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = Task.objects.all()
        status_colors = {
            'backlog': '#6c757d',
            'todo': '#0d6efd',
            'in_progress': '#0dcaf0',
            'done': '#198754',
        }

        total_estimated = tasks.aggregate(total=Sum('duration'))['total'] or timedelta(0)
        total_actual = tasks.aggregate(total=Sum('actual_duration'))['total'] or timedelta(0)

        status_labels = []
        status_values = []
        status_color_list = []
        status_rows = []

        for value, label in Task.Status.choices:
            task_duration = tasks.filter(status=value).aggregate(total=Sum('duration'))['total'] or timedelta(0)
            hours = round(task_duration.total_seconds() / 3600, 2)
            status_labels.append(label)
            status_values.append(hours)
            status_color_list.append(status_colors.get(value, '#adb5bd'))
            status_rows.append({
                'name': label,
                'hours': hours,
                'days': round(hours / 24, 2),
                'color': status_colors.get(value, '#adb5bd'),
            })

        context.update({
            'total_tasks': tasks.count(),
            'total_estimated_hours': round(total_estimated.total_seconds() / 3600, 2),
            'total_estimated_days': round(total_estimated.total_seconds() / 86400, 2),
            'total_actual_hours': round(total_actual.total_seconds() / 3600, 2),
            'total_actual_days': round(total_actual.total_seconds() / 86400, 2),
            'status_labels': json.dumps(status_labels),
            'status_values': json.dumps(status_values),
            'status_colors': json.dumps(status_color_list),
            'status_rows': status_rows,
        })
        return context


class TaskStatusUpdateView(UpdateView):
    model = Task
    fields = ['status']
    http_method_names = ['post']
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        task = form.save(commit=False)
        if task.status == Task.Status.IN_PROGRESS and not task.start_time:
            task.start_time = timezone.now()
        if task.status == Task.Status.DONE and not task.end_time:
            task.end_time = timezone.now()
        task.save()
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        return redirect(self.success_url)


class TaskToggleDoneView(View):
    http_method_names = ['post']

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        done = request.POST.get('done') == 'true'

        if done:
            task.status = Task.Status.DONE
            if not task.end_time:
                task.end_time = timezone.now()
        else:
            task.status = Task.Status.TODO
            task.end_time = None

        task.save(update_fields=['status', 'end_time', 'updated_at'])
        return JsonResponse({'success': True, 'status': task.status})

    def get(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


class TaskStartTimerView(View):
    http_method_names = ['post']

    def post(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        if not task.start_time:
            task.start_time = timezone.now()
            task.status = Task.Status.IN_PROGRESS
            task.save(update_fields=['start_time', 'status', 'updated_at'])
        return redirect(reverse_lazy('task_list'))

    def get(self, request, *args, **kwargs):
        return redirect(reverse_lazy('task_list'))
