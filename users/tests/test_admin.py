"""Tests for user admin."""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserAdminTest(TestCase):
    """Tests for CustomUser admin."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com'
        )

    def test_admin_can_access_user_list(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/users/customuser/')
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_user_add(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/users/customuser/add/')
        self.assertEqual(response.status_code, 200)


class TherapistProfileAdminTest(TestCase):
    """Tests for TherapistProfile admin."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com'
        )

    def test_admin_can_access_therapist_list(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/users/therapistprofile/')
        self.assertEqual(response.status_code, 200)


class PatientProfileAdminTest(TestCase):
    """Tests for PatientProfile admin."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com'
        )

    def test_admin_can_access_patient_list(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/users/patientprofile/')
        self.assertEqual(response.status_code, 200)
