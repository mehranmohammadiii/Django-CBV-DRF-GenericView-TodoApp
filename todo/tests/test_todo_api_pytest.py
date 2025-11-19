import pytest
from django.contrib.auth.models import User
from todo.models import Task


# ---------------------------------------------------------------------------------------------------
@pytest.mark.django_db
class TestTaskListAPI:
    """
    Advantages of pytest over TestCase:
    1. Simplicity: Functions instead of classes
    2. Fixtures: Reusable fixtures
    3. Parametrize: Test multiple cases
    4. Readability: No self

    Testing Steps:
    1. Create Users and Tasks
    2. Authenticate
    3. Request API
    4. Review Results
    """

    # ----------------------------------
    @pytest.fixture(autouse=True)
    def setup(self):
        """Each test prepares this data before starting."""
        self.user = User.objects.create_user(username="testuser", password="pass1234")

        self.other_user = User.objects.create_user(
            username="other", password="pass1234"
        )

        self.task1 = Task.objects.create(
            user=self.user, title="Task 1", completed=False
        )
        self.task2 = Task.objects.create(user=self.user, title="Task 2", completed=True)

        self.task3 = Task.objects.create(
            user=self.other_user, title="Task از کاربر دیگر", completed=False
        )

    # ---------------------------------
    def test_task_list_requires_authentication(self, client):
        """Check if task-list requires authentication."""

        response = client.get("/todo/api/task-list/")

        assert response.status_code in [401, 403]

    def test_task_list_with_authentication(self, client):
        """Check task-list when user is logged in."""

        client.force_login(self.user)

        response = client.get("/todo/api/task-list/")

        assert response.status_code == 200

    # ---------------------------------
    def test_task_list_returns_only_user_tasks(self, client):
        """Check that task-list returns only user tasks."""

        client.force_login(self.user)

        response = client.get("/todo/api/task-list/")

        data = response.json()

        assert len(data) == 2

        titles = {item.get("title") for item in data}
        assert titles == {"Task 1", "Task 2"}

    # ---------------------------------
    def test_task_list_different_users_get_different_tasks(self, client):
        """Check that different users see different tasks."""

        client.force_login(self.user)
        response1 = client.get("/todo/api/task-list/")
        data1 = response1.json()
        assert len(data1) == 2

        client.logout()

        client.force_login(self.other_user)
        response2 = client.get("/todo/api/task-list/")
        data2 = response2.json()
        assert len(data2) == 1
        assert data2[0]["title"] == "Task از کاربر دیگر"

    # ---------------------------------
    def test_task_list_completed_field_values(self, client):
        """Check completed field values."""
        client.force_login(self.user)
        response = client.get("/todo/api/task-list/")
        data = response.json()

        completed_values = {item["title"]: item["completed"] for item in data}
        assert completed_values["Task 1"] == False
        assert completed_values["Task 2"] == True

    # ---------------------------------
    @pytest.mark.parametrize("title", ["Task 1", "Task 2"])
    def test_task_list_contains_title(self, client, title):
        """Parameterize check: Test all titles.
        @pytest.mark.parameterize allows us to run this test for each title.
        """

        client.force_login(self.user)
        response = client.get("/todo/api/task-list/")
        data = response.json()

        titles = [item["title"] for item in data]
        assert title in titles

    # ---------------------------------
    def test_task_list_http_method_post(self, client):
        """Check if POST works to create task."""
        client.force_login(self.user)

        response = client.post(
            "/todo/api/task-list/",
            data={"title": "Task جدید از POST", "completed": False},
            content_type="application/json",
        )

        # status code 201 (Created)
        assert response.status_code == 201

        # Check if the task was created in the database
        new_task = Task.objects.get(title="Task جدید از POST")
        assert new_task.user == self.user

    # ---------------------------------
    def test_task_list_empty_for_user_without_tasks(self, client):
        """Check if the user sees an empty list without a task."""

        new_user = User.objects.create_user(username="newuser", password="pass1234")

        client.force_login(new_user)
        response = client.get("/todo/api/task-list/")
        data = response.json()

        assert len(data) == 0
        assert data == []


# ---------------------------------------------------------------------------------------------------
# pytest todo/tests/test_todo_api_pytest.py -v
# pytest todo/tests/test_todo_api_pytest.py::TestTaskListAPI::test_task_list_returns_only_user_tasks
