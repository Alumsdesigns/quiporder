from django.contrib import admin

# Register your models here. Manage equipment in admin panel

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_quantity', 'available_quantity')
    search_fields = ('name',)


@admin.register(EquipmentOrder)
class EquipmentOrderAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'patient', 'quantity', 'status', 'ordered_at')
    list_filter = ('status',)