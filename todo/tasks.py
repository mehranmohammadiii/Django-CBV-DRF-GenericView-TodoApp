# task
from .models import Task
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail

# -----------------------------------------


@shared_task
def send_email_task(task_id):
    """
    This task takes the task ID, reads its information from the database
    and sends an email to the user.
    """

    task_obj = get_object_or_404(Task, id=task_id)

    subject = f"New task created : {task_obj.title}"
    message = f' hello task "{task_obj.title}" Successfully registered in the system.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [
        "user@example.com",
    ]
    send_mail(subject, message, email_from, recipient_list)
    return f"Email sent for Task ID {task_id}"


# -----------------------------------------


@shared_task
def count_incomplete_tasks():
    """
    This task counts and logs the number of uncompleted tasks.
    """
    count = Task.objects.filter(completed=False).count()

    print(f"📊 REPORT: You have {count} incomplete tasks pending!")
    return count


# -----------------------------------------


@shared_task
def delete_completed_tasks():
    """
    Deletes completed tasks (is_completed=True) from the database.
    """
    deleted_count, _ = Task.objects.filter(completed=True).delete()

    if deleted_count > 0:
        return f"🧹 Cleanup: Deleted {deleted_count} completed tasks."
    else:
        return "🧹 Cleanup: No completed tasks to delete."


# -----------------------------------------
