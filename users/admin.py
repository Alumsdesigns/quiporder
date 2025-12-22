# Register models to appear in admin panel
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
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
    model = CustomUser
    
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'date_of_birth',
        'user_type',
        'is_active',
        'is_staff',
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
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
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

