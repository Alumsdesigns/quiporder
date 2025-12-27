from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

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
    - Therapist-only 'created_by' selection
    - Read-only timestamps
    - DRAFT status support (doesn't reduce inventory until moved to PENDING)
    """
    list_display = ['get_patient_name', 'equipment', 'quantity', 'status', 'created_by', 'ordered_at']
    list_filter = ['status', 'ordered_at', 'equipment__category']
    search_fields = [
        'patient__user__username', 
        'patient__user__first_name', 
        'patient__user__last_name', 
        'equipment__name'
        ]
    readonly_fields = ['ordered_at']
    ordering = ['-ordered_at']

    # Add fieldsets for better form organization
    fieldsets = (
        ('Order Details', {
            'fields': ('patient', 'equipment', 'quantity')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'created_by', 'ordered_at'),
            'description': 'DRAFT orders do not reduce inventory. Change to PENDING to allocate stock.'
        }),
    )
    
    def get_patient_name(self, obj):
        """Display patient's full name cleanly."""
        return obj.patient.user.get_full_name() or obj.patient.user.username
    get_patient_name.short_description = 'Patient Name'


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Restrict 'created_by' to therapist users only.

        Assumes:
        - Therapists have user_type='THERAPIST'
        - Enforces RBAC at UI level
        """
        if db_field.name == "created_by":
            kwargs["queryset"] = db_field.related_model.objects.filter(user_type='THERAPIST')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # Auto-populate created_by with current user
    def save_model(self, request, obj, form, change):
        """Auto-set created_by to current user if not set."""
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EquipmentOrderStatusHistory)
class EquipmentOrderStatusHistoryAdmin(admin.ModelAdmin):
    """
    Read-only audit log for equipment order status changes.

    Purpose:
    - Preserve historical integrity
    - Prevent manual tampering
    - Show complete therapist details (name + ID)
    """

    list_display = [
        'order',
        'old_status',
        'new_status',
        'get_changed_by_details',
        'changed_at',
    ]
    list_filter = ['new_status', 'changed_at']
    search_fields = [
        'order__equipment__name', 
        'order__patient__user__username',
        'changed_by__username',  # Can search by therapist username
        'changed_by__first_name',  # Can search by therapist name
        'changed_by__last_name'
        ]
    readonly_fields = [
        'order',
        'old_status',
        'new_status',
        'get_changed_by_details',  # NEW: Show in detail view too
        'changed_at',
        'notes',
    ]
    ordering = ['-changed_at']

    # Custom method to display therapist details
    def get_changed_by_details(self, obj):
        """
        Display therapist name, username, and ID who made the change.
        
        Format: "Dr. John Smith (jsmith) [ID: 123]"
        Falls back to "System" if no user recorded.
        """
        if not obj.changed_by:
            return format_html('<em>System (Automated)</em>')
        
        user = obj.changed_by
        full_name = user.get_full_name() or user.username
        
        # Build detailed string with name, username, and ID
        details = f"{full_name} ({user.username}) [ID: {user.id}]"
        
        # Add therapist-specific info if available
        if hasattr(user, 'therapistprofile'):
            license_num = user.therapistprofile.license_number
            details += f" [License: {license_num}]"
        
        return details
    
    get_changed_by_details.short_description = 'Changed By (Therapist)'
    
    # Add detail view for individual history entries
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Status Change', {
            'fields': ('old_status', 'new_status', 'changed_at')
        }),
        ('Change Attribution', {
            'fields': ('get_changed_by_details', 'notes'),
            'description': 'User who made this status change and optional notes.'
        }),
    )

    def has_add_permission(self, request):
        """Disallow manual creation of audit records."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disallow edits to audit history."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disallow deletion of audit history."""
        return False
