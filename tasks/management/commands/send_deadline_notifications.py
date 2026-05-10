import os
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Task, TaskNotification
from tasks.telegram_utils import send_telegram_message


class Command(BaseCommand):
    help = 'Send Telegram notifications for tasks with upcoming deadlines.'

    def handle(self, *args, **options):
        now = timezone.localtime()
        one_day_from_now = now + timedelta(days=1)

        tasks = Task.objects.filter(
            deadline__gte=now,
            deadline__lte=one_day_from_now,
        ).exclude(status=Task.Status.DONE)

        if not tasks.exists():
            self.stdout.write('No upcoming task deadlines for today.')
            return

        for task in tasks:
            if TaskNotification.objects.filter(task=task).exists():
                continue

            profile = getattr(task.owner, 'profile', None)
            if not profile or not profile.telegram_chat_id:
                self.stdout.write(f'Skipping task {task.pk} because no Telegram chat ID is configured.')
                continue

            message = self.build_message(task)
            try:
                result = send_telegram_message(profile.telegram_chat_id, message)
            except Exception as exc:
                self.stderr.write(
                    f'Error sending notification for task {task.pk}: invalid chat_id {profile.telegram_chat_id} ({exc})'
                )
                continue

            if result.get('ok'):
                TaskNotification.objects.create(task=task)
                self.stdout.write(f'Notification sent for task {task.pk}.')
            else:
                self.stderr.write(
                    f'Failed to send notification for task {task.pk}: {result.get("error", "unknown error")}'
                )

    def build_message(self, task: Task) -> str:
        deadline = task.deadline.strftime('%Y-%m-%d %H:%M')
        title = task.title
        status = task.get_status_display()
        time_label = task.start_time.strftime('%Y-%m-%d %H:%M') if task.start_time else 'No start time'

        return (
            f'🔔 <b>Task deadline within the next day</b>\n\n'
            f'<b>Title:</b> {title}\n'
            f'<b>Status:</b> {status}\n'
            f'<b>Deadline:</b> {deadline}\n'
            f'<b>Start time:</b> {time_label}\n'
        )
