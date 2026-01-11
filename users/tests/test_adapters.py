"""Tests for user adapters."""
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from users.adapters import NoSignupAccountAdapter

User = get_user_model()


class NoSignupAccountAdapterTest(TestCase):
    """Tests for NoSignupAccountAdapter."""

    def setUp(self):
        self.factory = RequestFactory()
        self.adapter = NoSignupAccountAdapter()
        self.therapist = User.objects.create_user(
            username='therapist1',
            password='testpass123',
            user_type='THERAPIST'
        )
        self.patient = User.objects.create_user(
            username='patient1',
            password='testpass123',
            user_type='PATIENT'
        )

    def test_is_open_for_signup_returns_false(self):
        request = self.factory.get('/accounts/signup/')
        self.assertFalse(self.adapter.is_open_for_signup(request))

    def test_get_login_redirect_url_therapist(self):
        request = self.factory.get('/accounts/login/')
        request.user = self.therapist
        url = self.adapter.get_login_redirect_url(request)
        self.assertEqual(url, '/equipment/dashboard/')

    def test_get_login_redirect_url_patient(self):
        request = self.factory.get('/accounts/login/')
        request.user = self.patient
        url = self.adapter.get_login_redirect_url(request)
        self.assertEqual(url, '/equipment/patient/dashboard/')