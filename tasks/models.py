from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    telegram_chat_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f'Profile for {self.user.username}'


class TaskNotification(models.Model):
    task = models.OneToOneField(
        'Task',
        on_delete=models.CASCADE,
        related_name='deadline_notification',
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification sent for {self.task.title} at {self.sent_at}'


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    class Status(models.TextChoices):
        BACKLOG = 'backlog', 'Backlog'
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE = 'done', 'Done'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='tasks',
    )
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.BACKLOG,
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(default=timezone.localtime)
    duration = models.DurationField(
        default=timedelta(hours=1),
        help_text='Planned duration for the task',
    )
    actual_duration = models.DurationField(
        default=timedelta(0),
        help_text='Time spent to complete the task',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', 'priority', 'title']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return self.status != self.Status.DONE and self.deadline < timezone.localtime()

    def is_urgent(self):
        if self.status == self.Status.DONE:
            return False
        return self.deadline <= timezone.localtime() + timedelta(days=1)

    def deadline_remaining(self):
        return self.deadline - timezone.localtime()

    def deadline_remaining_display(self):
        remaining = self.deadline_remaining()
        if remaining.total_seconds() < 0:
            hours = abs(int(remaining.total_seconds() // 3600))
            if hours:
                return f'Overdue by {hours}h'
            return 'Overdue'
        if remaining.days == 0:
            return 'Today'
        return f'{remaining.days}d'

    @staticmethod
    def format_duration(duration):
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60

        if hours and minutes:
            return f'{hours}h {minutes}m'
        if hours:
            return f'{hours}h'
        return f'{minutes}m'

    def get_duration_display(self):
        return self.format_duration(self.duration)

    def get_actual_duration_display(self):
        return self.format_duration(self.actual_duration)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
