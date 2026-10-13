from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class RegistrationTests(TestCase):
    def test_registration_success(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newaccount",
                "password1": "StrongTestPass123!",
                "password2": "StrongTestPass123!",
            },
        )

        self.assertRedirects(
            response,
            reverse("home"),
        )
        self.assertTrue(
            User.objects.filter(
                username="newaccount"
            ).exists()
        )

        created_user = User.objects.get(
            username="newaccount"
        )
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            created_user.pk,
        )

    def test_invalid_registration_is_rejected(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "invalidaccount",
                "password1": "StrongTestPass123!",
                "password2": "DifferentTestPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/register.html",
        )
        self.assertFalse(
            User.objects.filter(
                username="invalidaccount"
            ).exists()
        )
        self.assertIn(
            "password2",
            response.context["form"].errors,
        )

class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser",
            password="StrongTestPass123!",
        )

    def test_login_success(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "loginuser",
                "password": "StrongTestPass123!",
            },
        )

        self.assertRedirects(
            response,
            reverse("home"),
        )
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )

    def test_failed_login_is_rejected(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "loginuser",
                "password": "WrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/login.html",
        )
        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )
        self.assertTrue(
            response.context["form"].non_field_errors()
        )

class LogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="logoutuser",
            password="StrongTestPass123!",
        )

    def test_logout_via_post(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("logout")
        )

        self.assertRedirects(
            response,
            reverse("home"),
        )
        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_logout_via_get_is_rejected(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("logout")
        )

        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )
