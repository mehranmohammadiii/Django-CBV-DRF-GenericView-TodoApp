from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from .tasks import send_email_task


@receiver(post_save, sender=Task)
def task_created_signal(sender, instance, created, **kwargs):
    if created:
        send_email_task.delay(instance.id)
