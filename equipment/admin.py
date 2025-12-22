from django.contrib import admin
from .models import Equipment, EquipmentOrder

"""
Admin configuration for the equipment app.

Registers:
- Equipment
- EquipmentOrder

Register models here. Manage equipment in admin panel
Allows staff to manage equipment inventory and orders via Django admin.
"""

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
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
    list_display = ['get_patient_name', 'patient', 'equipment', 'quantity', 'status', 'ordered_at']
    list_filter = ['status', 'ordered_at', 'equipment__category']
    search_fields = ['patient__user__username', 'patient__user__first_name', 'patient__user__last_name', 'equipment__name']
    readonly_fields = ['ordered_at']
    ordering = ['-ordered_at']
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    get_patient_name.short_description = 'Patient'