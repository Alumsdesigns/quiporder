"""Tests for equipment models."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from equipment.models import Equipment, EquipmentOrder, EquipmentOrderStatusHistory
from users.models import TherapistProfile, PatientProfile

User = get_user_model()


class EquipmentModelTest(TestCase):
    """Tests for Equipment model."""

    def setUp(self):
        self.equipment = Equipment.objects.create(
            name='Wheelchair',
            category='MOBILITY',
            size='MEDIUM',
            total_quantity=10,
            available_quantity=10,
            description='Standard wheelchair'
        )

    def test_equipment_creation(self):
        self.assertEqual(self.equipment.name, 'Wheelchair')
        self.assertEqual(self.equipment.total_quantity, 10)

    def test_equipment_str(self):
        expected = 'Wheelchair (MOBILITY, MEDIUM)'
        self.assertEqual(str(self.equipment), expected)

    def test_is_available_true(self):
        self.assertTrue(self.equipment.is_available)

    def test_is_available_false(self):
        self.equipment.available_quantity = 0
        self.equipment.save()
        self.assertFalse(self.equipment.is_available)

    def test_utilization_rate_partial(self):
        self.equipment.available_quantity = 5
        self.equipment.save()
        self.assertEqual(self.equipment.utilization_rate, 50.0)

    def test_utilization_rate_full(self):
        self.equipment.available_quantity = 0
        self.equipment.save()
        self.assertEqual(self.equipment.utilization_rate, 100.0)

    def test_utilization_rate_zero_total(self):
        self.equipment.total_quantity = 0
        self.equipment.available_quantity = 0
        self.equipment.save()
        self.assertEqual(self.equipment.utilization_rate, 0)

    def test_equipment_category_choices(self):
        """Test equipment can have different categories."""
        equipment = Equipment.objects.create(
            name='Bed',
            category='DAILY_LIVING',
            size='LARGE',
            total_quantity=5,
            available_quantity=5
        )
        self.assertEqual(equipment.category, 'DAILY_LIVING')

    def test_equipment_size_choices(self):
        """Test equipment can have different sizes."""
        equipment = Equipment.objects.create(
            name='Crutches',
            category='MOBILITY',
            size='SMALL',
            total_quantity=20,
            available_quantity=20
        )
        self.assertEqual(equipment.size, 'SMALL')


class EquipmentOrderModelTest(TestCase):
    """Tests for EquipmentOrder model."""

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
            user_type='PATIENT'
        )
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            assigned_therapist=self.therapist_profile,
            medical_record_number='MRN001'
        )
        self.equipment = Equipment.objects.create(
            name='Walker',
            category='MOBILITY',
            size='LARGE',
            total_quantity=5,
            available_quantity=5
        )

    def test_order_creation(self):
        order = EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=2,
            status='PENDING',
            created_by=self.therapist_user
        )
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.status, 'PENDING')

    def test_order_str(self):
        order = EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=1,
            status='PENDING',
            created_by=self.therapist_user
        )
        self.assertIn('Walker', str(order))

    def test_order_reduces_inventory(self):
        EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=2,
            status='PENDING',
            created_by=self.therapist_user
        )
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.available_quantity, 3)

    def test_order_status_choices(self):
        """Test order can have different statuses."""
        order = EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=1,
            status='APPROVED',
            created_by=self.therapist_user
        )
        self.assertEqual(order.status, 'APPROVED')

    def test_order_with_notes(self):
        """Test order can have notes."""
        order = EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=1,
            status='PENDING',
            created_by=self.therapist_user,
            notes='Urgent request'
        )
        self.assertEqual(order.notes, 'Urgent request')

    def test_order_deleted_at_initially_none(self):
        """Test deleted_at is None for new orders."""
        order = EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=1,
            status='PENDING',
            created_by=self.therapist_user
        )
        self.assertIsNone(order.deleted_at)

    def test_multiple_orders_same_equipment(self):
        """Test multiple orders can be created for same equipment."""
        EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=1,
            status='PENDING',
            created_by=self.therapist_user
        )
        EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=1,
            status='PENDING',
            created_by=self.therapist_user
        )
        self.assertEqual(EquipmentOrder.objects.count(), 2)


class EquipmentOrderStatusHistoryTest(TestCase):
    """Tests for EquipmentOrderStatusHistory model."""

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
            user_type='PATIENT'
        )
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            assigned_therapist=self.therapist_profile,
            medical_record_number='MRN001'
        )
        self.equipment = Equipment.objects.create(
            name='Walker',
            category='MOBILITY',
            size='LARGE',
            total_quantity=5,
            available_quantity=5
        )
        self.order = EquipmentOrder.objects.create(
            patient=self.patient_profile,
            equipment=self.equipment,
            quantity=1,
            status='PENDING',
            created_by=self.therapist_user
        )

    def test_status_history_creation(self):
        """Test status history can be created."""
        history = EquipmentOrderStatusHistory.objects.create(
            order=self.order,
            old_status='PENDING',
            new_status='APPROVED',
            changed_by=self.therapist_user
        )
        self.assertEqual(history.old_status, 'PENDING')
        self.assertEqual(history.new_status, 'APPROVED')

    def test_status_history_str(self):
        """Test status history string representation."""
        history = EquipmentOrderStatusHistory.objects.create(
            order=self.order,
            old_status='PENDING',
            new_status='APPROVED',
            changed_by=self.therapist_user
        )
        history_str = str(history)
        self.assertIn('PENDING', history_str)
        self.assertIn('APPROVED', history_str)
