from django.test import TestCase
from django.contrib.auth.models import User
from todo.models import Task


# -------------------------------------------------------------------------------------------------------
class TaskListViewTest(TestCase):
    """
            Here is the English version of your text:
            1.setUp: Creates two users and three tasks (two for the first user and one for the second).
    This prepares the test data and ensures that the view returns only the tasks belonging to the authenticated user.
            2.Authentication: Uses force_login to create a session for the user. The view requires permissions.IsAuthenticated.
            3.Sends a GET request to the endpoint and checks that an HTTP 200 OK response is returned.
            4.Parses the JSON response and verifies that only the authenticated user’s tasks are returned (count == 2) and that the task names match.

    """

    # ---------------------------------
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="pass1234"
        )
        self.other_user = User.objects.create_user(
            username="other", password="pass1234"
        )

        Task.objects.create(user=self.user, title="Task 1")
        Task.objects.create(user=self.user, title="Task 2")
        Task.objects.create(user=self.other_user, title="Task other")

    # ---------------------------------
    def test_tkas_list_returns_only_authenticated_user_tasks(self):

        self.client.force_login(self.user)

        response = self.client.get("/todo/api/task-list/")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data), 2)

        titles = {item.get("title") for item in data}
        self.assertSetEqual(titles, {"Task 1", "Task 2"})


# -------------------------------------------------------------------------------------------------------
class TaskDetailViewTest(TestCase):
    """
    1.setUp: Creates two users and two tasks (one for each user).
    2.Authentication: Logs in the first user.
    3.GET request: Requests the task using the task ID that belongs to the first user.
    4.Validation: Confirms that the status code is 200 and the returned data is correct.
    5.Additional test: Verifies that the other user’s task is not accessible (returns 404).

    """

    # ---------------------------------
    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser", password="pass1234"
        )
        self.other_user = User.objects.create_user(
            username="other", password="pass1234"
        )

        self.task_user1 = Task.objects.create(
            user=self.user, title="UserTask1", completed=False
        )

        self.task_user2 = Task.objects.create(
            user=self.other_user, title="UserTask2", completed=True
        )

    # ---------------------------------
    def test_task_detail_returns_correct_task(self):

        self.client.force_login(self.user)

        response = self.client.get(
            f"/todo/api/task-detail/{self.task_user1.id}/"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["id"], self.task_user1.id)
        self.assertEqual(data["title"], "UserTask1")
        self.assertEqual(data["completed"], False)
        self.assertEqual(data["user"], self.user.id)

    # ---------------------------------
    def test_task_detail_cannot_access_other_user_task(self):

        self.client.force_login(self.user)

        response = self.client.get(
            f"/todo/api/task-detail/{self.task_user2.id}/"
        )

        self.assertEqual(response.status_code, 404)


# -------------------------------------------------------------------------------------------------------
