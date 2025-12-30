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

@login_required
def patient_dashboard(request):
    """Patient dashboard showing their orders only."""
    # Check if user is patient
    if request.user.user_type != 'PATIENT':
        messages.error(request, 'Access denied. Patients only.')
        return redirect('home')
    
    # Get patient's orders only
    try:
        orders = EquipmentOrder.objects.filter(
            patient=request.user.patientprofile,
            deleted_at__isnull=True
        ).select_related('equipment').order_by('-ordered_at')
    except:
        # If patient has no profile yet
        orders = []
        messages.warning(request, 'No patient profile found. Please contact your therapist.')
    
    return render(request, 'equipment/patient_dashboard.html', {'orders': orders})


@login_required
def equipment_list(request):
    """List all equipment inventory (therapists only)."""
    if request.user.user_type != 'THERAPIST':
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('home')
    
    equipment = Equipment.objects.all().order_by('category', 'name')
    return render(request, 'equipment/equipment_list.html', {'equipment': equipment})

@login_required
def order_create(request):
    """Create new equipment order for therapists only."""
    if request.user.user_type != 'THERAPIST':
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('home')
    
    if request.method == 'POST':
        # Get form data
        patient_id = request.POST.get('patient')
        equipment_id = request.POST.get('equipment')
        quantity = request.POST.get('quantity')
        notes = request.POST.get('notes', '') 
        
        # Validate inputs
        if not patient_id or not equipment_id or not quantity:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('order_create')
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messages.error(request, 'Quantity must be greater than zero.')
                return redirect('order_create')
        except ValueError:
            messages.error(request, 'Invalid quantity.')
            return redirect('order_create')
        
        # Check equipment availability
        try:
            equipment = Equipment.objects.get(id=equipment_id)
            if equipment.available_quantity < quantity:
                messages.error(
                    request, 
                    f'Not enough stock. Available: {equipment.available_quantity}'
                )
                return redirect('order_create')
        except Equipment.DoesNotExist:
            messages.error(request, 'Equipment not found.')
            return redirect('order_create')
        
        # Check patient exists
        try:
            patient = PatientProfile.objects.get(id=patient_id)
        except PatientProfile.DoesNotExist:
            messages.error(request, 'Patient not found.')
            return redirect('order_create')
        
        # Create order
        order = EquipmentOrder.objects.create(
            patient=patient,
            equipment=equipment,
            quantity=quantity,
            notes=notes, 
            status='PENDING',
            created_by=request.user
        )
        
        # Save with current user for audit trail
        order.save(current_user=request.user)
        
        messages.success(
            request, 
            f'Order created successfully! {quantity}x {equipment.name} for {patient.user.get_full_name()}'
        )
        return redirect('therapist_dashboard')
    
    # GET request, show form
    patients = PatientProfile.objects.filter(status='ACTIVE').select_related('user')
    equipment = Equipment.objects.filter(available_quantity__gt=0).order_by('name')
    
    context = {
        'patients': patients,
        'equipment': equipment,
    }
    
    return render(request, 'equipment/order_form.html', context)