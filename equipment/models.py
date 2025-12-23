# Create your models here.
# Equipment, EquipmentCategory, EquipmentOrder tables
"""
Models for equipment app.

- Equipment represents items available for allocation
- EquipmentOrder tracks assignment of equipment to patients
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from users.models import PatientProfile


class Equipment(models.Model):
    """Equipment catalog with categories."""

    CATEGORY_CHOICES = [
        ('MOBILITY', 'Mobility Aids - Wheelchairs, Walkers, Canes'),
        ('ADL', 'Activities of Daily Living - Eating, Bathing, Dressing Aids'),
        ('SENSORY', 'Sensory Equipment - Weighted Blankets, Fidget Toys'),
    ]
    SIZE_CHOICES = [
        ('SMALL', 'Small'),
        ('MEDIUM', 'Medium'),
        ('LARGE', 'Large'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='MOBILITY')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='MEDIUM')
    total_quantity = models.PositiveIntegerField(
        help_text="Total units owned by facility"
    )
    available_quantity = models.PositiveIntegerField(
                help_text="Units currently available (not assigned to patients)"
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.category}, {self.size})"

    # Property to check if equipment has available stock
    @property
    def is_available(self):
        """Check if equipment has available stock."""
        return self.available_quantity > 0

    # Property to calculate utilization rate
    @property
    def utilization_rate(self):
        """Calculate what percentage of equipment is currently out."""
        if self.total_quantity == 0:
            return 0
        return ((self.total_quantity - self.available_quantity) / self.total_quantity) * 100

    # Validation method to ensure available_quantity doesn't exceed total_quantity +  Added None checks and proper error messages
    def clean(self):
        """Validate that available_quantity doesn't exceed total_quantity."""
        # COMMIT 1: Check if fields have values before comparing (prevents TypeError)
        if self.total_quantity is None:
            raise ValidationError({
                'total_quantity': 'Total quantity is required.'
            })
        
        if self.available_quantity is None:
            raise ValidationError({
                'available_quantity': 'Available quantity is required.'
            })
        
        # COMMIT 1: Now safe to compare (both are not None)
        if self.available_quantity > self.total_quantity:
            raise ValidationError({
                'available_quantity': f"Available quantity ({self.available_quantity}) cannot exceed total quantity ({self.total_quantity})"
            })
    
class EquipmentOrder(models.Model):
    """Orders for equipment assigned to patients."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
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

    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    ordered_at = models.DateTimeField(auto_now_add=True)

    # Track who created the order
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_orders',
        help_text="Therapist who created this order"
    )

    class Meta:
        verbose_name = 'Equipment Order'
        verbose_name_plural = 'Equipment Orders'
        ordering = ['-ordered_at']

    def __str__(self):
        return f"{self.equipment.name} → {self.patient.user.get_full_name()} ({self.get_status_display()})"

    # Enhanced save method with inventory management
    def save(self, *args, **kwargs):
        """Override save to update inventory and create status history."""
        is_new = self.pk is None
        old_status = None
        old_quantity = 0
        
        if not is_new:
            # Get old status and quantity before saving
            old_order = EquipmentOrder.objects.get(pk=self.pk)
            old_status = old_order.status
            old_quantity = old_order.quantity
            
            # If status changed to CANCELLED, restore inventory
            if old_status != 'CANCELLED' and self.status == 'CANCELLED':
                self.equipment.available_quantity += old_quantity
                self.equipment.save()
            # If status changed to DELIVERED, optionally adjust total_quantity
            elif old_status != 'DELIVERED' and self.status == 'DELIVERED':
                # adjust total_quantity if equipment won't return
                pass
        else:
            # New order, reduce available quantity
            if self.equipment.available_quantity >= self.quantity:
                self.equipment.available_quantity -= self.quantity
                self.equipment.save()
            else:
                raise ValueError(f"Insufficient stock. Available: {self.equipment.available_quantity}, Requested: {self.quantity}")
        
        super().save(*args, **kwargs)
        
        # Create status history entry if status changed
        if is_new or (old_status and old_status != self.status):
            EquipmentOrderStatusHistory.objects.create(
                order=self,
                old_status=old_status if old_status else 'CREATED',
                new_status=self.status,
                changed_by=kwargs.get('changed_by')
            )


class EquipmentOrderStatusHistory(models.Model):
    """
    Audit log for equipment order status changes.
    Tracks who changed status, what it changed to, and when.
    """
    
    order = models.ForeignKey(
        EquipmentOrder,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who made this status change"
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Optional notes about status change")
    
    class Meta:
        verbose_name = 'Status History'
        verbose_name_plural = 'Status Histories'
        ordering = ['-changed_at']
    
    def __str__(self):
        changed_by_name = self.changed_by.get_full_name() if self.changed_by else "System"
        return f"{self.order.equipment.name}: {self.old_status} → {self.new_status} by {changed_by_name}"