from django.test import TestCase
from django.contrib.auth.models import User


# -------------------------------------------------------------------------------------
class IndexViewTest(TestCase):
    """
    1. Does the user get redirected without login?
    2. Does the page return 200 OK with login?
    3. Is the correct template being used?
    4. Does the request context have the correct data?
    """

    #  -------------------------
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="pass1234"
        )

    #  -------------------------
    def test_index_view_requires_login(self):
        """Check if indexView requires login."""

        response = self.client.get("/todo/")

        self.assertEqual(response.status_code, 302)

        # Check if the URL contains login
        self.assertIn("/accounts/login?next=/todo/", response.url)

    #  -------------------------
    def test_index_view_with_login(self):
        """Check indexView when user is logged in."""

        self.client.force_login(self.user)

        response = self.client.get("/todo/")

        self.assertEqual(response.status_code, 200)

    #  -------------------------
    def test_index_view_uses_correct_template(self):
        """Check that the correct template is being used."""

        self.client.force_login(self.user)

        response = self.client.get("/todo/")

        self.assertTemplateUsed(response, "todo/index.html")


# -------------------------------------------------------------------------------------
