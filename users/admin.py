from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, TherapistProfile, PatientProfile

"""
Admin configuration for the 'users' app.

Registers:
- CustomUser
- TherapistProfile
- PatientProfile

Allows managing users and related profiles via the Django admin panel.
"""


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom user admin with enhanced role display."""
    model = CustomUser

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'date_of_birth',
        'get_role_display',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    list_filter = ('user_type', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': (
                'username',
                'password',
                'first_name',
                'last_name',
                'email',
                'date_of_birth',
                'user_type',
                )}),
        ('Permissions', {
            'fields': (
                'is_staff',
                'is_active',
                'groups',
                'user_permissions',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'first_name',
                'last_name',
                'email',
                'date_of_birth',
                'password1',
                'password2',
                'user_type',
                'is_staff',
                'is_active',
            )}
         ),
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'user_type'
    )

    ordering = ('username',)

    def get_role_display(self, obj):
        """Display user role in admin list."""
        if obj.user_type:
            return obj.get_user_type_display()
        elif obj.is_superuser:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">System Administrator</span>'
            )
        else:
            return '-'

    get_role_display.short_description = 'Role'
    get_role_display.admin_order_field = 'user_type'


@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    """Admin interface for therapist profiles."""

    list_display = (
        'user',
        'license_number',
        'max_caseload',
        'status'
    )
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'license_number',
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """Admin interface for patient profiles."""

    list_display = (
        'user',
        'assigned_therapist',
        'medical_record_number',
        'status',
        'admission_date',
    )

    readonly_fields = ('admission_date',)

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'medical_record_number',
        'assigned_therapist__user__username',
    )
