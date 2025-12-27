from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Equipment, EquipmentOrder, EquipmentOrderStatusHistory

User = get_user_model()

"""
Admin configuration for the equipment app.

Registers:
- Equipment
- EquipmentOrder
- EquipmentOrderStatusHistory

Register models here. Manage equipment in admin panel.
Preserves audit integrity for order status changes.
Allows staff to manage equipment inventory and orders via Django admin.
"""

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Equipment inventory.

    Focus:
    - Clear stock visibility
    - Safe editing of quantities (business rules enforced in models)
    """
    list_display = ['name', 'category', 'size', 'total_quantity', 'available_quantity', 'stock_status']
    list_filter = ['category', 'size']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']

    def stock_status(self, obj):
        """Show visual indicator of stock level."""
        if obj.available_quantity == 0:
            return "Out of Stock"
        elif obj.available_quantity < obj.total_quantity * 0.3:
            return "Low Stock"
        else:
            return "In Stock"
    stock_status.short_description = 'Status'


@admin.register(EquipmentOrder)
class EquipmentOrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Equipment Orders.

    Improvements over default:
    - No duplicate patient columns
    - Therapist-only 'created_by' selection
    - Read-only timestamps
    """
    list_display = ['get_patient_name', 'equipment', 'quantity', 'status', 'ordered_at']
    list_filter = ['status', 'ordered_at', 'equipment__category']
    search_fields = [
        'patient__user__username', 
        'patient__user__first_name', 
        'patient__user__last_name', 
        'equipment__name'
        ]
    readonly_fields = ['ordered_at']
    ordering = ['-ordered_at']
    
    def get_patient_name(self, obj):
        """Display patient's full name cleanly."""
        return obj.patient.user.get_full_name() or obj.patient.user.username
    get_patient_name.short_description = 'Patient Name'


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Restrict 'created_by' to therapist users only.

        Assumes:
        - Therapists are staff users
        - Or belong to a 'Therapist' group
        Adjust the queryset if your role model differs.
        """
        if db_field.name == "created_by":
            kwargs["queryset"] = db_field.related_model.objects.filter(user_type='THERAPIST')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(EquipmentOrderStatusHistory)
class EquipmentOrderStatusHistoryAdmin(admin.ModelAdmin):
    """
    Read-only audit log for equipment order status changes.

    Purpose:
    - Preserve historical integrity
    - Prevent manual tampering
    """

    list_display = [
        'order',
        'old_status',
        'new_status',
        'changed_by',
        'changed_at',
    ]
    list_filter = ['new_status', 'changed_at']
    search_fields = ['order__equipment__name', 'order__patient__user__username']
    readonly_fields = [
        'order',
        'old_status',
        'new_status',
        'changed_by',
        'changed_at',
        'notes',
    ]
    ordering = ['-changed_at']

    def has_add_permission(self, request):
        """Disallow manual creation of audit records."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disallow edits to audit history."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disallow deletion of audit history."""
        return False
