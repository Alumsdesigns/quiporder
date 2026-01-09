"""
URL configuration for quiporder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

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
