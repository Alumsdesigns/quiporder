"""Tests for equipment admin."""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from equipment.models import Equipment, EquipmentOrder
from users.models import TherapistProfile, PatientProfile

User = get_user_model()


class EquipmentAdminTest(TestCase):
    """Tests for Equipment admin."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com'
        )
        self.equipment = Equipment.objects.create(
            name='Wheelchair',
            category='MOBILITY',
            size='MEDIUM',
            total_quantity=10,
            available_quantity=10
        )

    def test_admin_can_access_equipment_list(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/equipment/equipment/')
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_equipment_add(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/equipment/equipment/add/')
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_equipment_change(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/equipment/equipment/{self.equipment.pk}/change/')
        self.assertEqual(response.status_code, 200)


class EquipmentOrderAdminTest(TestCase):
    """Tests for EquipmentOrder admin."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com'
        )
        self.therapist = User.objects.create_user(
            username='therapist1',
            password='testpass123',
            user_type='THERAPIST'
        )
        self.therapist_profile = TherapistProfile.objects.create(
            user=self.therapist,
            license_number='LIC123',
            max_caseload=20
        )
        self.patient_user = User.objects.create_user(
            username='patient1',
            password='testpass123',
            user_type='PATIENT'
        )
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            assigned_therapist=self.therapist_profile,
            medical_record_number='MRN001'
        )
        self.equipment = Equipment.objects.create(
            name='Wheelchair',
            category='MOBILITY',
            size='MEDIUM',
            total_quantity=10,
            available_quantity=10
        )
        self.order = EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=1,
            status='PENDING',
            created_by=self.therapist
        )

    def test_admin_can_access_order_list(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/equipment/equipmentorder/')
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_order_change(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(f'/admin/equipment/equipmentorder/{self.order.pk}/change/')
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_status_history(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/equipment/equipmentorderstatushistory/')
        self.assertEqual(response.status_code, 200)
