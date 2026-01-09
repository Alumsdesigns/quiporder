from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.utils.html import format_html
from .models import CustomUser, TherapistProfile, PatientProfile
from django.contrib import messages

"""
Admin configuration for the 'users' app.

Registers:
- CustomUser
- TherapistProfile
- PatientProfile
- Hide modals we don't use from admin panel

Allows managing users and related profiles via the Django admin panel.
"""

try:
    admin.site.unregister(Site)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

try:
    from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
    admin.site.unregister(SocialAccount)
    admin.site.unregister(SocialApp)
    admin.site.unregister(SocialToken)
except (ImportError, admin.sites.NotRegistered):
    pass


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom admin for user management with role restrictions."""
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

    list_filter = ('user_type', 'is_staff', 'is_active', 'is_superuser')

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
                'is_superuser',
                'groups',
                'user_permissions',
            ),
            'description': (
                '<strong style="color: #e74c3c;">SECURITY WARNING:</strong> '
                'Patient users cannot be granted staff or superuser privileges. '
                'Only THERAPIST users should have elevated permissions.'
            ),
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

    def save_model(self, request, obj, form, change):
        """
        Override save to enforce business rules:
        - PATIENT users can NEVER be superusers
        - PATIENT users can NEVER be staff

        Stores corrections in request for message display.
        """
        user_type = form.cleaned_data.get('user_type') or obj.user_type
        is_staff = form.cleaned_data.get('is_staff', False)
        is_superuser = form.cleaned_data.get('is_superuser', False)

        request._security_corrections = []

        if user_type == 'PATIENT':
            if is_superuser:
                obj.is_superuser = False
                request._security_corrections.append('Superuser')

            if is_staff:
                obj.is_staff = False
                request._security_corrections.append('Staff')
        else:
            if obj.is_superuser and user_type != 'THERAPIST':
                request._therapist_warning = True

        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        """Customize messages after adding user."""
        from django.contrib import messages

        storage = messages.get_messages(request)
        list(storage)

        if hasattr(
                request, '_security_corrections') and request._security_corrections:
            messages.warning(
                request,
                f'User "{obj.username}" created with security restrictions. '
                f'{" and ".join(request._security_corrections)} privileges were blocked '
                f'because patient users cannot have elevated permissions.'
            )
        else:
            messages.success(
                request, f'✓ User "{
                    obj.username}" was created successfully.')

        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        """Customize messages after changing user."""
        from django.contrib import messages

        storage = messages.get_messages(request)
        list(storage)

        if hasattr(
                request, '_security_corrections') and request._security_corrections:
            messages.error(
                request,
                f'SECURITY: Cannot grant {
                    " or ".join(
                        request._security_corrections)} '
                f'to patient user "{
                    obj.username}". User saved WITHOUT these privileges.'
            )
        else:
            messages.success(
                request, f'✓ User "{
                    obj.username}" was saved successfully.')

        return super().response_change(request, obj)

    def get_fieldsets(self, request, obj=None):
        """
        Dynamically modify fieldsets based on user type.
        Remove staff/superuser options for PATIENT users to prevent UI confusion.
        """
        fieldsets = super().get_fieldsets(request, obj)

        if obj and obj.user_type == 'PATIENT':
            fieldsets = list(fieldsets)
            for i, (name, options) in enumerate(fieldsets):
                if name == 'Permissions':
                    fields = list(options.get('fields', ()))
                    if 'is_staff' in fields:
                        fields.remove('is_staff')
                    if 'is_superuser' in fields:
                        fields.remove('is_superuser')

                    fieldsets[i] = (name, {
                        **options,
                        'fields': tuple(fields),
                        'description': (
                            '<strong style="color: #e74c3c;">SECURITY:</strong> '
                            'Patient users cannot be granted staff or superuser privileges. '
                            'These options are hidden for patient accounts.'
                        ),
                    })
                    break

        return fieldsets


@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    """Admin interface for therapist profiles with user type validation."""

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

    list_filter = ('status',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Limit user dropdown to only show THERAPIST users.
        Prevents assigning patient users to therapist profiles.
        """
        if db_field.name == "user":
            kwargs["queryset"] = CustomUser.objects.filter(
                user_type='THERAPIST')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Validate that only THERAPIST users can have TherapistProfile.
        Backup validation in case dropdown is bypassed.
        """
        if obj.user.user_type != 'THERAPIST':
            messages.error(
                request,
                f'Cannot create TherapistProfile for {
                    obj.user.get_user_type_display()} '
                f'user "{obj.user.username}". Only THERAPIST users allowed.'
            )
            return

            super().save_model(request, obj, form, change)


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

    list_filter = ('status',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Limit dropdowns to correct user types.
        - user: Only PATIENT users
        - assigned_therapist: Only TherapistProfiles
        """
        if db_field.name == "user":
            kwargs["queryset"] = CustomUser.objects.filter(user_type='PATIENT')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Validate that only PATIENT users can have PatientProfile.
        """
        if obj.user.user_type != 'PATIENT':
            messages.error(
                request,
                f'Cannot create PatientProfile for {
                    obj.user.get_user_type_display()} '
                f'user "{obj.user.username}". Only PATIENT users allowed.'
            )
            return

        super().save_model(request, obj, form, change)
