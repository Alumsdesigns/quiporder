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

    # Validation method to ensure available_quantity doesn't exceed total_quantity + added None checks and proper error messages
    def clean(self):
        """Validate that available_quantity doesn't exceed total_quantity."""
        # Check if fields have values before comparing (prevents TypeError)
        if self.total_quantity is None:
            raise ValidationError({
                'total_quantity': 'Total quantity is required.'
            })
        
        if self.available_quantity is None:
            raise ValidationError({
                'available_quantity': 'Available quantity is required.'
            })
        
        # Now safe to compare (both are not None)
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

    quantity = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(1)],
        help_text="Number of units to assign to patient"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    ordered_at = models.DateTimeField(auto_now_add=True)
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

    def clean(self):
        """Validate order before saving - enforce three rules."""
        super().clean()
        
        # Comprehensive validation of order quantity
        if self.equipment and self.quantity:
            # Calculate total of ALL active orders for this equipment
            active_statuses = ['PENDING', 'APPROVED', 'IN_TRANSIT', 'DELIVERED']
            
            # Get sum of all active orders, excluding current order if editing
            from django.db.models import Sum
            total_active_orders = EquipmentOrder.objects.filter(
                equipment=self.equipment,
                status__in=active_statuses
            ).exclude(pk=self.pk).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            # Add this order's quantity to the total
            total_with_this_order = total_active_orders + self.quantity
            
            # Total active orders cannot exceed total_quantity
            if total_with_this_order > self.equipment.total_quantity:
                currently_allocated = total_active_orders
                max_can_order = self.equipment.total_quantity - currently_allocated
                
                raise ValidationError({
                    'quantity': (
                        f"Cannot order {self.quantity} units. "
                        f"Total inventory is {self.equipment.total_quantity} units. "
                        f"Currently allocated to other active orders: {currently_allocated} units. "
                        f"Maximum you can order: {max_can_order} units."
                    )
                })
            
            # Check available_quantity (both new AND edited orders)
            # Calculate how much is truly available for this order
            current_available = self.equipment.available_quantity
            
            # If editing existing active order, add back its old quantity
            if self.pk:
                try:
                    old_order = EquipmentOrder.objects.get(pk=self.pk)
                    if old_order.status not in ['CANCELLED', 'RETURNED']:
                        current_available += old_order.quantity
                except EquipmentOrder.DoesNotExist:
                    pass
            
            # New quantity cannot exceed available + old quantity
            if self.quantity > current_available:
                raise ValidationError({
                    'quantity': (
                        f"Cannot order {self.quantity} units. "
                        f"Only {current_available} units available "
                        f"(current stock: {self.equipment.available_quantity}"
                        + (f" + {current_available - self.equipment.available_quantity} from this order" 
                           if self.pk and current_available > self.equipment.available_quantity else "") +
                        f"). Total inventory: {self.equipment.total_quantity}, "
                        f"allocated to other orders: {total_active_orders}."
                    )
                })
    
    def save(self, *args, **kwargs):
        """Override save to update inventory and create status history."""
        is_new = self.pk is None
        old_status = None
        old_quantity = 0
        
        # For existing orders, get old values
        if not is_new:
            old_order = EquipmentOrder.objects.get(pk=self.pk)
            old_status = old_order.status
            old_quantity = old_order.quantity
            
            # Handle status changes
            if old_status not in ['CANCELLED', 'RETURNED'] and self.status in ['CANCELLED', 'RETURNED']:
                # Order cancelled/returned - restore inventory
                self.equipment.available_quantity += old_quantity
                self.equipment.save()
            elif old_status in ['CANCELLED', 'RETURNED'] and self.status not in ['CANCELLED', 'RETURNED']:
                # Order reactivated - reduce inventory
                self.equipment.available_quantity -= self.quantity
                self.equipment.save()
            elif old_status not in ['CANCELLED', 'RETURNED'] and self.status not in ['CANCELLED', 'RETURNED']:
                # Order quantity changed while active - adjust inventory
                quantity_difference = self.quantity - old_quantity
                self.equipment.available_quantity -= quantity_difference
                self.equipment.save()
        else:
            # New order reduce available quantity
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