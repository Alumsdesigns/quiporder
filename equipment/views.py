# Create your views here.
#  Show equipment list, create orders, etc.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Equipment, EquipmentOrder
from users.models import PatientProfile

@login_required
def therapist_dashboard(request):
    """Therapist dashboard showing overview statistics."""
    # Check if user is therapist
    if request.user.user_type != 'THERAPIST':
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('home')
    
    # Get statistics
    context = {
        'total_equipment': Equipment.objects.count(),
        'total_orders': EquipmentOrder.objects.filter(deleted_at__isnull=True).count(),
        'pending_orders': EquipmentOrder.objects.filter(
            status='PENDING', 
            deleted_at__isnull=True
        ).count(),
        'active_patients': PatientProfile.objects.filter(status='ACTIVE').count(),
    }
    
    return render(request, 'equipment/therapist_dashboard.html', context)