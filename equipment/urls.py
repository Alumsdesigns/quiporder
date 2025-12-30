"""
Equipment app URL Configuration
Routes for equipment-related views
"""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.therapist_dashboard, name='therapist_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    #  path('list/', views.equipment_list, name='equipment_list'),
    #  path('order/create/', views.order_create, name='order_create'),
]