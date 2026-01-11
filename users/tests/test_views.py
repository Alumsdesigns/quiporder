"""Tests for user-related views."""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class HomePageTest(TestCase):
    """Tests for home page."""

    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class LoginPageTest(TestCase):
    """Tests for login page."""

    def setUp(self):
        self.client = Client()

    def test_login_page_loads(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)


class SignupPageTest(TestCase):
    """Tests for signup page."""

    def setUp(self):
        self.client = Client()

    def test_signup_page_shows_closed_message(self):
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup_closed.html')


class LogoutTest(TestCase):
    """Tests for logout functionality."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='THERAPIST'
        )

    def test_logout_redirects(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/accounts/logout/')
        self.assertEqual(response.status_code, 302)