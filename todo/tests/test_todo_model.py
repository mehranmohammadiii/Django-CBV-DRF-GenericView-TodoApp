from django.test import TestCase
from django.contrib.auth.models import User
from todo.models import Task

# -------------------------------------------------------------------------------------------------------


class TaskModelTest(TestCase):
    """تست‌های مدل Task.

    این تست‌ها بررسی می‌کند:
    1. ایجاد Task با داده‌های صحیح
    2. مقادیر پیش‌فرض (default values)
    3. روابط (Foreign Key)
    4. متد __str__
    5. محدودیت‌های مدل
    """

    # ---------------------------
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="pass1234"
        )

    # ---------------------------
    def test_task_creation(self):

        task = Task.objects.create(
            user=self.user, title="خرید میوه‌ها", completed=False
        )

        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, "خرید میوه‌ها")
        self.assertEqual(task.user, self.user)

    # ---------------------------
    def test_task_str_method(self):

        task = Task.objects.create(user=self.user, title="تمرین ورزشی")

        self.assertEqual(str(task), "تمرین ورزشی")

    # ---------------------------
    def test_task_default_completed_value(self):

        task = Task.objects.create(user=self.user, title="کار جدید")

        self.assertEqual(task.completed, False)

    # ---------------------------
    def test_task_completed_can_be_changed(self):

        task = Task.objects.create(
            user=self.user, title="کار درسی", completed=False
        )

        task.completed = True
        task.save()

        task_from_db = Task.objects.get(id=task.id)
        self.assertEqual(task_from_db.completed, True)

    # ---------------------------
    def test_task_title_max_length(self):

        long_title = "a" * 200
        task = Task.objects.create(user=self.user, title=long_title)

        self.assertEqual(len(task.title), 200)

    # ---------------------------
    def test_task_user_relationship(self):

        user1 = self.user
        user2 = User.objects.create_user(
            username="user2", password="pass1234"
        )

        task1 = Task.objects.create(user=user1, title="Task 1")
        task2 = Task.objects.create(user=user2, title="Task 2")

        self.assertEqual(task1.user, user1)
        self.assertEqual(task2.user, user2)
        self.assertNotEqual(task1.user, task2.user)

    # ---------------------------
    def test_task_cascade_delete(self):

        user = User.objects.create_user(
            username="temp_user", password="pass1234"
        )

        Task.objects.create(user=user, title="Task 1")
        Task.objects.create(user=user, title="Task 2")

        self.assertEqual(Task.objects.filter(user=user).count(), 2)

        user.delete()

        self.assertEqual(Task.objects.filter(user=None).count(), 0)

    # ---------------------------
    def test_task_created_date_auto_set(self):

        from django.utils import timezone

        before_creation = timezone.now()

        task = Task.objects.create(user=self.user, title="Task جدید")

        after_creation = timezone.now()

        self.assertGreaterEqual(task.created_date, before_creation)
        self.assertLessEqual(task.created_date, after_creation)

    # ---------------------------
    def test_task_updated_date_updates_on_save(self):

        import time

        task = Task.objects.create(user=self.user, title="Task")

        first_updated = task.updated_date

        time.sleep(0.1)
        task.title = "Task تغییر‌یافته"
        task.save()

        second_updated = task.updated_date

        self.assertGreater(second_updated, first_updated)


# -------------------------------------------------------------------------------------------------------
