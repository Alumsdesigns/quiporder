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
    list_display = ('name', 'total_quantity', 'available_quantity')
    search_fields = ('name',)


@admin.register(EquipmentOrder)
class EquipmentOrderAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'patient', 'quantity', 'status', 'ordered_at')
    list_filter = ('status',)