"""
URL configuration for quiporder project.

Includes:
- Admin panel
- Authentication (allauth) with custom signup override
- Equipment management
- Home page
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'accounts/signup/',
        TemplateView.as_view(template_name='account/signup_closed.html'),
        name='account_signup'
    ),
    path('accounts/', include('allauth.urls')),
    path('equipment/', include('equipment.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]

handler403 = 'quiporder.views.error_403'
handler404 = 'quiporder.views.error_404'
handler405 = 'quiporder.views.error_405'
handler500 = 'quiporder.views.error_500'
