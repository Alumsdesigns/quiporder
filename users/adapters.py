"""
Custom adapters for django-allauth.

Handles:
- Disabled public signup (admin-only registration)
- Role-based login redirects (therapist → dashboard, patient → patient dashboard)
"""

from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class NoSignupAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter with disabled signup and role-based redirects.

    Features:
    - Blocks public signup (admin-only registration)
    - Redirects users to appropriate dashboard after login based on role
    """

    def is_open_for_signup(self, request):
        """
        Disable public signup.

        Returns:
            False - signup is always disabled for public users
        """
        return False

    def get_login_redirect_url(self, request):
        """
        Redirect users to role-appropriate page after login.

        Redirect logic:
        - Therapists → Therapist dashboard
        - Patients → Patient dashboard
        - Superusers → Therapist dashboard (admin access)
        - Default → Home page (fallback)

        This provides better UX by taking users directly to their workspace.
        """
        user = request.user

        # Therapist redirect
        if user.user_type == 'THERAPIST':
            return reverse('therapist_dashboard')

        # Patient redirect
        elif user.user_type == 'PATIENT':
            return reverse('patient_dashboard')

        # Superuser redirect (treat as therapist)
        elif user.is_superuser:
            return reverse('therapist_dashboard')

        # Fallback to home (shouldn't happen)
        else:
            return '/'
