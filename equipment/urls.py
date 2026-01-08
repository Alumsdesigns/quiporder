"""
Equipment app URL Configuration
Routes for equipment-related views
"""
from django.urls import path
from . import views

urlpatterns = [
    path(
        'dashboard/',
        views.therapist_dashboard,
        name='therapist_dashboard'),
    path(
        'patient/dashboard/',
        views.patient_dashboard,
        name='patient_dashboard'),
    path(
        'list/',
        views.equipment_list,
        name='equipment_list'),
    path(
        'order/create/',
        views.order_create,
        name='order_create'),
    path(
        'order/edit/<int:pk>/',
        views.order_edit,
        name='order_edit'),
    path(
        'order/delete/<int:pk>/',
        views.order_delete,
        name='order_delete'),
        # DELETE BELOW FOR PRODCUTION used to test locally
    path('test-403/', views.test_403, name='test_403'), 
    path('test-405/', views.test_405, name='test_405'),
    path('test-500/', views.test_500, name='test_500'),
]
