"""Tests for equipment views."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from equipment.models import Equipment, EquipmentOrder
from users.models import TherapistProfile, PatientProfile

User = get_user_model()


class TherapistDashboardViewTest(TestCase):
    """Tests for therapist dashboard view."""

    def setUp(self):
        self.client = Client()
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

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('therapist_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_therapist_can_access_dashboard(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(reverse('therapist_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/therapist_dashboard.html')

    def test_patient_cannot_access_therapist_dashboard(self):
        self.client.login(username='patient1', password='testpass123')
        response = self.client.get(reverse('therapist_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_shows_statistics(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(reverse('therapist_dashboard'))
        self.assertIn('total_equipment', response.context)
        self.assertIn('total_orders', response.context)
        self.assertIn('pending_orders', response.context)
        self.assertIn('active_patients', response.context)


class PatientDashboardViewTest(TestCase):
    """Tests for patient dashboard view."""

    def setUp(self):
        self.client = Client()
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

    def test_patient_can_access_dashboard(self):
        self.client.login(username='patient1', password='testpass123')
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_therapist_cannot_access_patient_dashboard(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_patient_dashboard_shows_orders(self):
        self.client.login(username='patient1', password='testpass123')
        response = self.client.get(reverse('patient_dashboard'))
        self.assertIn('orders', response.context)


class EquipmentListViewTest(TestCase):
    """Tests for equipment list view."""

    def setUp(self):
        self.client = Client()
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
        self.equipment = Equipment.objects.create(
            name='Wheelchair',
            category='MOBILITY',
            size='MEDIUM',
            total_quantity=10,
            available_quantity=10
        )

    def test_equipment_list_requires_login(self):
        response = self.client.get(reverse('equipment_list'))
        self.assertEqual(response.status_code, 302)

    def test_therapist_can_view_equipment(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(reverse('equipment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wheelchair')

    def test_patient_cannot_view_equipment_list(self):
        self.client.login(username='patient1', password='testpass123')
        response = self.client.get(reverse('equipment_list'))
        self.assertEqual(response.status_code, 302)

    def test_equipment_list_context(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(reverse('equipment_list'))
        self.assertIn('equipment', response.context)


class OrderCreateViewTest(TestCase):
    """Tests for order creation view."""

    def setUp(self):
        self.client = Client()
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

    def test_create_order_requires_login(self):
        response = self.client.get(reverse('order_create'))
        self.assertEqual(response.status_code, 302)

    def test_therapist_can_access_create_order(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(reverse('order_create'))
        self.assertEqual(response.status_code, 200)

    def test_patient_cannot_create_order(self):
        self.client.login(username='patient1', password='testpass123')
        response = self.client.get(reverse('order_create'))
        self.assertEqual(response.status_code, 302)

    def test_create_order_context(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(reverse('order_create'))
        self.assertIn('patients', response.context)
        self.assertIn('equipment', response.context)

    def test_create_order_post_success(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.post(reverse('order_create'), {
            'patient': self.patient_profile.pk,
            'equipment': self.equipment.pk,
            'quantity': 2,
            'notes': 'Test order'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EquipmentOrder.objects.count(), 1)

    def test_create_order_missing_fields(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.post(reverse('order_create'), {
            'patient': '',
            'equipment': '',
            'quantity': ''
        })
        self.assertEqual(response.status_code, 302)

    def test_create_order_invalid_quantity(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.post(reverse('order_create'), {
            'patient': self.patient_profile.pk,
            'equipment': self.equipment.pk,
            'quantity': 0,
            'notes': ''
        })
        self.assertEqual(response.status_code, 302)

    def test_create_order_exceeds_stock(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.post(reverse('order_create'), {
            'patient': self.patient_profile.pk,
            'equipment': self.equipment.pk,
            'quantity': 999,
            'notes': ''
        })
        self.assertEqual(response.status_code, 302)


class OrderEditViewTest(TestCase):
    """Tests for order edit view."""

    def setUp(self):
        self.client = Client()
        self.therapist = User.objects.create_user(
            username='therapist1',
            password='testpass123',
            user_type='THERAPIST'
        )
        self.therapist2 = User.objects.create_user(
            username='therapist2',
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

    def test_edit_order_requires_login(self):
        response = self.client.get(f'/equipment/order/edit/{self.order.pk}/')
        self.assertEqual(response.status_code, 302)

    def test_therapist_can_access_edit_order(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(f'/equipment/order/edit/{self.order.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_other_therapist_cannot_edit_order(self):
        self.client.login(username='therapist2', password='testpass123')
        response = self.client.get(f'/equipment/order/edit/{self.order.pk}/')
        self.assertEqual(response.status_code, 302)

    def test_patient_cannot_edit_order(self):
        self.client.login(username='patient1', password='testpass123')
        response = self.client.get(f'/equipment/order/edit/{self.order.pk}/')
        self.assertEqual(response.status_code, 302)

    def test_edit_order_context(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(f'/equipment/order/edit/{self.order.pk}/')
        self.assertIn('order', response.context)
        self.assertIn('patients', response.context)
        self.assertIn('equipment', response.context)
        self.assertTrue(response.context['is_edit'])


class OrderDeleteViewTest(TestCase):
    """Tests for order delete view."""

    def setUp(self):
        self.client = Client()
        self.therapist = User.objects.create_user(
            username='therapist1',
            password='testpass123',
            user_type='THERAPIST'
        )
        self.therapist2 = User.objects.create_user(
            username='therapist2',
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

    def test_delete_order_requires_login(self):
        response = self.client.get(f'/equipment/order/delete/{self.order.pk}/')
        self.assertEqual(response.status_code, 302)

    def test_therapist_can_access_delete_order(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(f'/equipment/order/delete/{self.order.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_other_therapist_cannot_delete_order(self):
        self.client.login(username='therapist2', password='testpass123')
        response = self.client.get(f'/equipment/order/delete/{self.order.pk}/')
        self.assertEqual(response.status_code, 302)

    def test_patient_cannot_delete_order(self):
        self.client.login(username='patient1', password='testpass123')
        response = self.client.get(f'/equipment/order/delete/{self.order.pk}/')
        self.assertEqual(response.status_code, 302)

    def test_delete_order_post(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.post(f'/equipment/order/delete/{self.order.pk}/')
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertIsNotNone(self.order.deleted_at)

    def test_delete_order_context(self):
        self.client.login(username='therapist1', password='testpass123')
        response = self.client.get(f'/equipment/order/delete/{self.order.pk}/')
        self.assertIn('order', response.context)
