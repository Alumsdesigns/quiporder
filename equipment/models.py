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
from django.db.models import Sum
from django.utils import timezone
from users.models import PatientProfile


class Equipment(models.Model):
    """Equipment catalog with categories."""

    CATEGORY_CHOICES = [
        ("MOBILITY", "Mobility Aids - Wheelchairs, Walkers, Canes"),
        ("ADL", "Activities of Daily Living - Eating, Bathing, Dressing Aids"),
        ("SENSORY", "Sensory Equipment - Weighted Blankets, Fidget Toys"),
    ]
    SIZE_CHOICES = [
        ("SMALL", "Small"),
        ("MEDIUM", "Medium"),
        ("LARGE", "Large"),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="MOBILITY"
    )
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default="MEDIUM")
    total_quantity = models.PositiveIntegerField(
        help_text="Total units owned by facility"
    )
    available_quantity = models.PositiveIntegerField(
        help_text="Units currently available not assigned to patients"
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
        return (
            (self.total_quantity - self.available_quantity) / self.total_quantity
        ) * 100

    # Validation method to ensure available_quantity doesn't exceed total_quantity + added None checks and proper error messages
    def clean(self):
        """Validate Equipment fields comprehensively.
        
        Three-level validation:
        1. Basic: available <= total
        2. Business: total >= allocated orders
        3. Flexible: available can be < (total - allocated) for maintenance
        """
        # Check if fields have values before comparing prevents TypeError
        if self.total_quantity is None:
            raise ValidationError({"total_quantity": "Total quantity is required."})

        if self.available_quantity is None:
            raise ValidationError(
                {"available_quantity": "Available quantity is required."}
            )

        # Now safe to compare both are not None
        if self.available_quantity > self.total_quantity:
            raise ValidationError(
                {
                    "available_quantity": (
                        f"Available quantity ({self.available_quantity}) cannot be more than "
                        f"total quantity ({self.total_quantity}). "
                        f"Please reduce available quantity to {self.total_quantity} or less."
                    )
                }
            )

        # Check against active orders only for existing equipment
        if self.pk:
            active_statuses = ["PENDING", "APPROVED", "IN_TRANSIT", "DELIVERED"]

            # Calculate total of all active orders for this equipment
            total_allocated = (
                EquipmentOrder.objects.filter(
                    equipment=self, 
                    status__in=active_statuses, 
                    deleted_at__isnull=True
                ).aggregate(total=Sum("quantity"))["total"]
                or 0
            )

            # Prevent reducing total_quantity below currently allocated amount
            if self.total_quantity < total_allocated:
                raise ValidationError(
                    {
                        "total_quantity": (
                            f"Cannot reduce total quantity to {self.total_quantity}. "
                            f"Currently {total_allocated} units are allocated to active orders. "
                            f"You must first cancel or return orders before reducing total quantity. "
                            f"Minimum allowed: {total_allocated} units."
                        )
                    }
                )

            # Available_quantity must be consistent with allocations
            # Formula: available = total - allocated
            correct_available = self.total_quantity - total_allocated

            if self.available_quantity > correct_available:
                raise ValidationError(
                    {
                        "available_quantity": (
                            f"Available quantity cannot be set to {self.available_quantity}. "
                            f"With {self.total_quantity} total units and {total_allocated} units allocated to active orders, "
                            f"maximum available is {correct_available} units. "
                            f"(Formula: Available = Total - Allocated = {self.total_quantity} - {total_allocated} = {correct_available})"
                        )
                    }
                )

            # Warn if available_quantity is set lower than mathematically correct
            # But we store it for potential admin warning
            if self.available_quantity < correct_available:
                # This is ALLOWED, admin might be marking some as unavailable for maintenance
                # Just log it or add a note field in future
                pass

    # NEW: Auto-adjust available_quantity when total_quantity increases
    def save(self, *args, **kwargs):
        """Override save to auto-adjust available_quantity when total increases."""
        if self.pk:  # Existing equipment
            old_equipment = Equipment.objects.get(pk=self.pk)
            old_total = old_equipment.total_quantity
            old_available = old_equipment.available_quantity

            # If total_quantity increased, auto-increase available_quantity
            if self.total_quantity > old_total:
                difference = self.total_quantity - old_total
                # Only auto-adjust if available wasn't manually changed
                if self.available_quantity == old_available:
                    self.available_quantity += difference

        super().save(*args, **kwargs)


class EquipmentOrder(models.Model):
    """Orders for equipment assigned to patients."""

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("IN_TRANSIT", "In Transit"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        ("RETURNED", "Returned"),
    ]

    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name="equipment_orders"
    )

    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="orders"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of units to assign to patient",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    ordered_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_orders",
        help_text="Therapist who created this order",
    )

    # Soft delete fields for audit compliance
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this order was soft-deleted null = not deleted",
    )

    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_orders",
        help_text="User who deleted this order",
    )

    class Meta:
        verbose_name = "Equipment Order"
        verbose_name_plural = "Equipment Orders"
        ordering = ["-ordered_at"]

    def __str__(self):
        deleted_marker = " [DELETED]" if self.deleted_at else ""
        return f"{self.equipment.name} → {self.patient.user.get_full_name()} ({self.get_status_display()}){deleted_marker}"

    def clean(self):
        """Validate order before saving - enforce three rules."""
        super().clean()

        # Comprehensive validation of order quantity
        if self.equipment and self.quantity:
            # Calculate total of ALL active orders for this equipment
            active_statuses = ["PENDING", "APPROVED", "IN_TRANSIT", "DELIVERED"]


            total_active_orders = (
                EquipmentOrder.objects.filter(
                    equipment=self.equipment, 
                    status__in=active_statuses,
                    deleted_at__isnull=True,
                )
                .exclude(pk=self.pk)
                .aggregate(total=Sum("quantity"))["total"]
                or 0
            )

            # Add this order's quantity to the total
            total_with_this_order = total_active_orders + self.quantity

            # Total active orders cannot exceed total_quantity
            if total_with_this_order > self.equipment.total_quantity:
                currently_allocated = total_active_orders
                max_can_order = self.equipment.total_quantity - currently_allocated

                raise ValidationError(
                    {
                        "quantity": (
                            f"Cannot order {self.quantity} units. "
                            f"Total inventory is {self.equipment.total_quantity} units. "
                            f"Currently {currently_allocated} units are already allocated to other active orders. "
                            f"Maximum you can order: {max_can_order} units. "
                            f"(Calculation: {self.equipment.total_quantity} total - {currently_allocated} allocated = {max_can_order} available)"
                        )
                    }
                )

            # Check available_quantity both new AND edited orders
            # Calculate how much is truly available for this order
            current_available = self.equipment.available_quantity

            # If editing existing active order, add back its old quantity
            if self.pk:
                try:
                    old_order = EquipmentOrder.objects.get(pk=self.pk)
                    if (
                        old_order.status not in ["CANCELLED", "RETURNED"]
                        and old_order.deleted_at is None
                    ):
                        current_available += old_order.quantity
                except EquipmentOrder.DoesNotExist:
                    pass

            # New quantity cannot exceed available + old quantity
            if self.quantity > current_available:
                raise ValidationError(
                    {
                        "quantity": (
                            f"Cannot order {self.quantity} units. "
                            f"Only {current_available} units are available "
                            f"(Current available stock: {self.equipment.available_quantity}"
                            + (
                                f" + {current_available - self.equipment.available_quantity} from this order being edited"
                                if self.pk
                                and current_available
                                > self.equipment.available_quantity
                                else ""
                            )
                            + f"). Total inventory: {self.equipment.total_quantity} units, "
                            f"already allocated to other orders: {total_active_orders} units."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        """Override save to update inventory and create status history."""
        
        # Extract current_user from kwargs for audit trail
        current_user = kwargs.pop("current_user", None)
        
        is_new = self.pk is None
        old_status = None
        old_quantity = 0
        
        if not is_new:
            old_order = EquipmentOrder.objects.get(pk=self.pk)
            old_status = old_order.status
            old_quantity = old_order.quantity
            
            # Active → Cancelled/Returned
            if old_status not in ['CANCELLED', 'RETURNED'] and self.status in ['CANCELLED', 'RETURNED']:
                # Order cancelled/returned - restore inventory
                self.equipment.available_quantity += old_quantity
                self.equipment.save()
            
            # Cancelled/Returned → Active (REACTIVATION)
            elif old_status in ['CANCELLED', 'RETURNED'] and self.status not in ['CANCELLED', 'RETURNED']:
                # Order reactivated - reduce inventory
                if self.equipment.available_quantity >= self.quantity:
                    self.equipment.available_quantity -= self.quantity
                    self.equipment.save()
                else:
                    # Multi-line error with order ID, equipment, patient
                    raise ValueError(
                        f"Cannot reactivate order #{self.pk}. Insufficient stock.\n"
                        f"Equipment: {self.equipment.name} (ID: {self.equipment.pk})\n"
                        f"Patient: {self.patient.user.get_full_name()}\n"
                        f"Available: {self.equipment.available_quantity} units\n"
                        f"Required: {self.quantity} units\n"
                        f"Shortage: {self.quantity - self.equipment.available_quantity} units\n"
                        f"Action: Increase inventory or reduce order quantity"
                    )
            
            # SCENARIO 3: DRAFT → Active (ACTIVATION) - MISSING IN DOCUMENT 6
            elif old_status == 'DRAFT' and self.status not in ['DRAFT', 'CANCELLED', 'RETURNED']:
                # Moving from DRAFT to active status - reduce inventory
                if self.equipment.available_quantity >= self.quantity:
                    self.equipment.available_quantity -= self.quantity
                    self.equipment.save()
                else:
                    # Multi-line error
                    raise ValueError(
                        f"Cannot activate order #{self.pk} from DRAFT. Insufficient stock.\n"
                        f"Equipment: {self.equipment.name} (ID: {self.equipment.pk})\n"
                        f"Patient: {self.patient.user.get_full_name()}\n"
                        f"Available: {self.equipment.available_quantity} units\n"
                        f"Required: {self.quantity} units\n"
                        f"Shortage: {self.quantity - self.equipment.available_quantity} units\n"
                        f"Action: Increase inventory or reduce order quantity"
                    )
            
            # Active → DRAFT (DEACTIVATION) - MISSING IN DOCUMENT 6
            elif old_status not in ['DRAFT', 'CANCELLED', 'RETURNED'] and self.status == 'DRAFT':
                # Moving from active to DRAFT - restore inventory
                self.equipment.available_quantity += old_quantity
                self.equipment.save()
            
            # Active → Active (QUANTITY CHANGE)
            elif old_status not in ['CANCELLED', 'RETURNED', 'DRAFT'] and self.status not in ['CANCELLED', 'RETURNED', 'DRAFT']:
                # Order quantity changed while active - adjust inventory properly
                quantity_difference = self.quantity - old_quantity
                if quantity_difference != 0:
                    new_available = self.equipment.available_quantity - quantity_difference
                    if new_available < 0:
                        # Multi-line error
                        raise ValueError(
                            f"Cannot increase order #{self.pk} quantity. Insufficient stock.\n"
                            f"Equipment: {self.equipment.name} (ID: {self.equipment.pk})\n"
                            f"Patient: {self.patient.user.get_full_name()}\n"
                            f"Current available: {self.equipment.available_quantity} units\n"
                            f"Additional needed: {abs(quantity_difference)} units\n"
                            f"Old quantity: {old_quantity} units\n"
                            f"New quantity: {self.quantity} units\n"
                            f"Action: Reduce quantity or wait for returns"
                        )
                    self.equipment.available_quantity = new_available
                    self.equipment.save()
        else:
            # NEW ORDER - FIXED FROM DOCUMENT 6
            if self.status not in ['DRAFT', 'CANCELLED', 'RETURNED']:
                if self.equipment.available_quantity >= self.quantity:
                    self.equipment.available_quantity -= self.quantity
                    self.equipment.save()
                else:
                    # ENHANCED ERROR MESSAGE
                    raise ValueError(
                        f"Cannot create order. Insufficient stock.\n"
                        f"Equipment: {self.equipment.name} (ID: {self.equipment.pk})\n"
                        f"Patient: {self.patient.user.get_full_name()}\n"
                        f"Available: {self.equipment.available_quantity} units\n"
                        f"Requested: {self.quantity} units\n"
                        f"Shortage: {self.quantity - self.equipment.available_quantity} units\n"
                        f"Action: Reduce quantity or wait for returns"
                    )
            # If status IS DRAFT/CANCELLED/RETURNED, don't touch inventory (correct)
        
        super().save(*args, **kwargs)
        
        # Create status history entry if status changed
        if is_new or (old_status and old_status != self.status):
            EquipmentOrderStatusHistory.objects.create(
                order=self,
                old_status=old_status if old_status else 'CREATED',
                new_status=self.status,
                changed_by=current_user
            )
        # Soft delete method
    def delete(self, using=None, keep_parents=False, current_user=None):
        """
        Soft delete - mark as deleted instead of removing from database.
        Preserves audit trail and related history.
        """
        self.deleted_at = timezone.now()
        self.deleted_by = current_user

        # Restore inventory if order was active
        if self.status not in ["CANCELLED", "RETURNED", "DRAFT"]:
            self.equipment.available_quantity += self.quantity
            self.equipment.save()

        # self.save() replaced below

        # IMPORTANT: Call save() without args to avoid recursion
        super(EquipmentOrder, self).save()

        # Create history entry for deletion
        EquipmentOrderStatusHistory.objects.create(
            order=self,
            old_status=self.status,
            new_status="DELETED",
            changed_by=current_user,
            notes=f"Order soft-deleted at {self.deleted_at}",
        )

        # Hard delete method (for admin only)
        def hard_delete(self):
            """Actually delete from database admin use only."""
            super().delete()


class EquipmentOrderStatusHistory(models.Model):
    """
    Audit log for equipment order status changes.
    Tracks who changed status, what it changed to, and when.
    """

    order = models.ForeignKey(
        EquipmentOrder, on_delete=models.CASCADE, related_name="status_history"
    )
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who made this status change",
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Optional notes about status change")

    class Meta:
        verbose_name = "Status History"
        verbose_name_plural = "Status Histories"
        ordering = ["-changed_at"]

    def __str__(self):
        changed_by_name = (
            self.changed_by.get_full_name() if self.changed_by else "System"
        )
        return f"{self.order.equipment.name}: {self.old_status} → {self.new_status} by {changed_by_name}"
