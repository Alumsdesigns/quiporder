"""Tests for user models."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import TherapistProfile, PatientProfile

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Tests for CustomUser model."""

    def test_create_therapist_user(self):
        user = User.objects.create_user(
            username='therapist1',
            password='testpass123',
            user_type='THERAPIST',
            first_name='John',
            last_name='Smith'
        )
        self.assertEqual(user.user_type, 'THERAPIST')
        self.assertEqual(user.get_full_name(), 'John Smith')

    def test_create_patient_user(self):
        user = User.objects.create_user(
            username='patient1',
            password='testpass123',
            user_type='PATIENT'
        )
        self.assertEqual(user.user_type, 'PATIENT')
        self.assertFalse(user.is_staff)

    def test_user_str_representation(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='THERAPIST'
        )
        self.assertIn('testuser', str(user))
        self.assertIn('Therapist', str(user))

    def test_full_name_property(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='THERAPIST',
            first_name='Jane',
            last_name='Doe'
        )
        self.assertEqual(user.full_name, 'Jane Doe')

    def test_full_name_empty(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='THERAPIST'
        )
        self.assertEqual(user.full_name, '')


class TherapistProfileModelTest(TestCase):
    """Tests for TherapistProfile model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='therapist1',
            password='testpass123',
            user_type='THERAPIST',
            first_name='Dr.',
            last_name='Smith'
        )

    def test_create_therapist_profile(self):
        profile = TherapistProfile.objects.create(
            user=self.user,
            license_number='LIC12345',
            max_caseload=25
        )
        self.assertEqual(profile.license_number, 'LIC12345')
        self.assertEqual(profile.status, 'ACTIVE')

    def test_therapist_profile_str_with_name(self):
        profile = TherapistProfile.objects.create(
            user=self.user,
            license_number='LIC12345',
            max_caseload=25
        )
        self.assertIn('Dr. Smith', str(profile))
        self.assertIn('LIC12345', str(profile))

    def test_therapist_profile_str_without_name(self):
        user = User.objects.create_user(
            username='therapist2',
            password='testpass123',
            user_type='THERAPIST'
        )
        profile = TherapistProfile.objects.create(
            user=user,
            license_number='LIC99999',
            max_caseload=25
        )
        self.assertIn('therapist2', str(profile))


class PatientProfileModelTest(TestCase):
    """Tests for PatientProfile model."""

    def setUp(self):
        self.therapist_user = User.objects.create_user(
            username='therapist1',
            password='testpass123',
            user_type='THERAPIST'
        )
        self.therapist_profile = TherapistProfile.objects.create(
            user=self.therapist_user,
            license_number='LIC123',
            max_caseload=20
        )
        self.patient_user = User.objects.create_user(
            username='patient1',
            password='testpass123',
            user_type='PATIENT',
            first_name='John',
            last_name='Doe'
        )

    def test_create_patient_profile(self):
        profile = PatientProfile.objects.create(
            user=self.patient_user,
            assigned_therapist=self.therapist_profile,
            medical_record_number='MRN001'
        )
        self.assertEqual(profile.medical_record_number, 'MRN001')
        self.assertEqual(profile.status, 'ACTIVE')

    def test_patient_profile_str_with_name(self):
        profile = PatientProfile.objects.create(
            user=self.patient_user,
            assigned_therapist=self.therapist_profile,
            medical_record_number='MRN001'
        )
        self.assertIn('John Doe', str(profile))
        self.assertIn('MRN001', str(profile))

    def test_patient_profile_str_without_name(self):
        user = User.objects.create_user(
            username='patient2',
            password='testpass123',
            user_type='PATIENT'
        )
        profile = PatientProfile.objects.create(
            user=user,
            assigned_therapist=self.therapist_profile,
            medical_record_number='MRN002'
        )
        self.assertIn('patient2', str(profile))