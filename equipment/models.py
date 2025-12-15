# Create your models here.
# Equipment, EquipmentCategory, EquipmentOrder tables

"""
Models for equipment app.

- Equipment represents items available for allocation
- EquipmentOrder tracks assignment of equipment to patients
"""

from django.db import models
from users.models import PatientProfile


class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    total_quantity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class EquipmentOrder(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('RETURNED', 'Returned'),
    ]

    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name='equipment_orders'
    )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    quantity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='REQUESTED'
    )

    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.equipment.name} → {self.patient.user.username}"
