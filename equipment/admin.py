from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from .models import Equipment, EquipmentOrder, EquipmentOrderStatusHistory
from django.http import JsonResponse

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
    list_display = [
        'name',
        'category',
        'size',
        'total_quantity',
        'available_quantity',
        'stock_status']
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


class DeletedFilter(admin.SimpleListFilter):
    """
    Custom filter for soft-deleted orders.

    Provides clear Yes/No options instead of confusing date-based filtering.
    Makes it easy to view active orders, deleted orders, or all orders.

    This replaces the default 'deleted_at' filter which showed dates
    instead of clear Active/Deleted options.
    """
    title = 'deleted status'
    parameter_name = 'is_deleted'

    def lookups(self, request, model_admin):
        """
        🔥 Define filter options that appear in sidebar.

        Returns:
            Tuple of (value, display_name) pairs
        """
        return (
            ('active', 'Active Orders'),
            ('deleted', 'Deleted Orders'),
        )

    def queryset(self, request, queryset):
        """
        Filter the queryset based on selected option.

        Args:
            request: HTTP request
            queryset: Current queryset to filter

        Returns:
            Filtered queryset based on selection
        """
        if self.value() == 'active':
            return queryset.filter(deleted_at__isnull=True)
        if self.value() == 'deleted':
            return queryset.filter(deleted_at__isnull=False)
        return queryset


@admin.register(EquipmentOrder)
class EquipmentOrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Equipment Orders.

    Features:
    - Therapist-only 'created_by' selection
    - Read-only timestamps
    - DRAFT status support (doesn't reduce inventory until moved to PENDING)
    - Soft delete support (deleted orders hidden by default)
    - Visual deletion indicators
    - Filter to view deleted orders
    """
    list_display = [
        'get_patient_name',
        'equipment',
        'quantity',
        'status',
        'order_status',
        'created_by',
        'ordered_at'
    ]
    list_filter = [
        'status',
        DeletedFilter,
        'ordered_at',
        'equipment__category'
    ]
    search_fields = [
        'patient__user__username',
        'patient__user__first_name',
        'patient__user__last_name',
        'equipment__name',
        'notes'
    ]
    readonly_fields = ['ordered_at']
    ordering = ['deleted_at', '-ordered_at']

    # Add fieldsets for better form organization
    fieldsets = (
        ('Order Details', {
            'fields': ('patient', 'equipment', 'quantity')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'description': 'Optional notes or special instructions for this order.'
        }),
        ('Status & Tracking', {
            'fields': ('status', 'created_by', 'ordered_at'),
            'description': 'DRAFT orders do not reduce inventory. Change to PENDING to allocate stock.'
        }),
    )

    def get_queryset(self, request):
        """
        Override queryset to hide soft-deleted orders by default.

        Now checks for 'is_deleted' parameter (from DeletedFilter)
        instead of 'deleted_at' parameter.

        Users can view deleted orders by:
        1. Clicking 'Deleted Orders' in the sidebar filter
        2. Clicking 'All' to see everything

        This keeps the main list clean while preserving audit trail.
        """
        qs = super().get_queryset(request)

        if 'is_deleted' not in request.GET:
            return qs.filter(deleted_at__isnull=True)

        return qs

    def order_status(self, obj):
        """
        Display clear status indicator for orders.

        - Column header: "Order Status"
        - Active display: "Active" (green)
        - Deleted display: "Deleted" (red)

        Shows:
        - Green "Active" for active orders
        - Red "Deleted" for soft-deleted orders
        """
        if obj.deleted_at:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">Deleted</span>'
            )
        return format_html(
            '<span style="color: #27ae60; font-weight: bold;">Active</span>'
        )
    order_status.short_description = 'Order Status'
    order_status.admin_order_field = 'deleted_at'

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
            kwargs["queryset"] = db_field.related_model.objects.filter(
                user_type='THERAPIST')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Auto-set created_by to current user if not set."""
        if not obj.created_by:
            obj.created_by = request.user

        obj.save(current_user=request.user)

    def delete_model(self, request, obj):
        """
        Soft delete with user tracking.

        NOTE: Soft delete does NOT return stock to available quantity.
        This preserves audit trail and prevents inventory manipulation.
        Stock can be manually adjusted if needed via Equipment admin.
        """
        obj.delete(current_user=request.user)

    def delete_queryset(self, request, queryset):
        """
        Soft delete multiple objects.

        NOTE: Soft delete does NOT return stock to available quantity.
        This preserves audit trail and prevents inventory manipulation.
        """
        for obj in queryset:
            obj.delete(current_user=request.user)


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
        'changed_by__username',
        'changed_by__first_name',
        'changed_by__last_name'
    ]
    readonly_fields = [
        'order',
        'old_status',
        'new_status',
        'get_changed_by_details',
        'changed_at',
        'notes',
    ]
    ordering = ['-changed_at']

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

        details = f"{full_name} ({user.username}) [ID: {user.id}]"

        if hasattr(user, 'therapistprofile'):
            license_num = user.therapistprofile.license_number
            details += f" [License: {license_num}]"

        return details

    get_changed_by_details.short_description = 'Changed By (Therapist)'

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
        """
        Allow superusers to delete (needed for cascade when deleting orders).
        Regular users cannot delete to preserve audit integrity.
        """
        return request.user.is_superuser
 

    def csrf_debug(request):
        """Debug CSRF - REMOVE BEFORE PRODUCTION"""
        return JsonResponse({
            'csrf_cookie': request.COOKIES.get('csrftoken', 'NOT SET'),
            'csrf_header': request.META.get('HTTP_X_CSRFTOKEN', 'NOT SET'),
            'session': request.session.session_key,
            'user': str(request.user),
        })