"""
Views for equipment management.

Handles:
- Therapist dashboard with statistics and recent orders
- Patient dashboard with order history
- Equipment list
- Order CRUD operations (create, edit, delete)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Equipment, EquipmentOrder
from users.models import PatientProfile


@login_required
def therapist_dashboard(request):
    """
    Therapist dashboard showing overview statistics and recent orders.

    Access: Therapists and superusers only

    Features:
    - System statistics (equipment, orders, patients)
    - Recent orders table with edit/delete actions
    - 24-hour edit window indicator
    """
    if request.user.user_type != 'THERAPIST' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('home')

    total_equipment = Equipment.objects.count()
    total_orders = EquipmentOrder.objects.filter(
        deleted_at__isnull=True).count()
    pending_orders = EquipmentOrder.objects.filter(
        status='PENDING',
        deleted_at__isnull=True
    ).count()
    active_patients = PatientProfile.objects.filter(status='ACTIVE').count()

    recent_orders = EquipmentOrder.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'patient__user',
        'equipment',
        'created_by'
    ).order_by('-ordered_at')[:10]

    for order in recent_orders:
        time_since_order = timezone.now() - order.ordered_at
        order.can_edit = time_since_order < timedelta(hours=24)

    context = {
        'total_equipment': total_equipment,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'active_patients': active_patients,
        'recent_orders': recent_orders,
    }

    return render(request, 'equipment/therapist_dashboard.html', context)


@login_required
def patient_dashboard(request):
    """
    Patient dashboard showing their orders only.

    Access: Patients only
    Read-only view of personal order history.
    """
    if request.user.user_type != 'PATIENT':
        messages.error(request, 'Access denied. Patients only.')
        return redirect('home')

    try:
        orders = EquipmentOrder.objects.filter(
            patient=request.user.patientprofile,
            deleted_at__isnull=True
        ).select_related('equipment').order_by('-ordered_at')
    except BaseException:
        orders = []
        messages.warning(
            request,
            'No patient profile found. Please contact your therapist.')

    return render(request,
                  'equipment/patient_dashboard.html',
                  {'orders': orders})


@login_required
def equipment_list(request):
    """
    List all equipment inventory.

    Access: Therapists and superusers only
    Shows all equipment with availability status.
    """
    if request.user.user_type != 'THERAPIST' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('home')

    equipment = Equipment.objects.all().order_by('category', 'name')
    return render(request,
                  'equipment/equipment_list.html',
                  {'equipment': equipment})


@login_required
def order_create(request):
    """
    Create equipment order for patient.

    Access: Therapists and superusers only
    Validates: Stock availability before creating order
    """
    if request.user.user_type != 'THERAPIST' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('home')

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        equipment_id = request.POST.get('equipment')
        quantity = request.POST.get('quantity')
        notes = request.POST.get('notes', '')

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

        try:
            equipment = Equipment.objects.get(id=equipment_id)
            if equipment.available_quantity < quantity:
                messages.error(
                    request, f'Not enough stock. Available: {
                        equipment.available_quantity}')
                return redirect('order_create')
        except Equipment.DoesNotExist:
            messages.error(request, 'Equipment not found.')
            return redirect('order_create')

        try:
            patient = PatientProfile.objects.get(id=patient_id)
        except PatientProfile.DoesNotExist:
            messages.error(request, 'Patient not found.')
            return redirect('order_create')

        order = EquipmentOrder.objects.create(
            patient=patient,
            equipment=equipment,
            quantity=quantity,
            notes=notes,
            status='PENDING',
            created_by=request.user
        )

        order.save(current_user=request.user)

        messages.success(
            request, f'Order created successfully! {quantity}x {
                equipment.name} for {
                patient.user.get_full_name()}')
        return redirect('therapist_dashboard')

    patients = PatientProfile.objects.filter(
        status='ACTIVE').select_related('user')
    equipment = Equipment.objects.filter(
        available_quantity__gt=0).order_by('name')

    context = {
        'patients': patients,
        'equipment': equipment,
        'is_edit': False,
    }

    return render(request, 'equipment/order_form.html', context)

@login_required
def order_edit(request, pk):
    """
    Edit equipment order within 24 hours.

    Access: Therapists and superusers only
    Restriction: Only order creator can edit
    Time window: 24 hours from creation
    """
    order = get_object_or_404(EquipmentOrder, pk=pk, deleted_at__isnull=True)

    if request.user.user_type != 'THERAPIST' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('home')

    if order.created_by != request.user:
        messages.error(request, 'You can only edit your own orders.')
        return redirect('therapist_dashboard')

    time_diff = timezone.now() - order.ordered_at
    if time_diff > timedelta(hours=24):
        messages.error(
            request,
            'Orders can only be edited within 24 hours of creation.')
        return redirect('therapist_dashboard')

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        equipment_id = request.POST.get('equipment')
        quantity_str = request.POST.get('quantity')
        notes = request.POST.get('notes', '')

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                messages.error(request, 'Quantity must be greater than zero.')
                return redirect('order_edit', pk=pk)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid quantity.')
            return redirect('order_edit', pk=pk)

        try:
            patient = PatientProfile.objects.get(pk=patient_id)
            equipment = Equipment.objects.get(pk=equipment_id)
        except (PatientProfile.DoesNotExist, Equipment.DoesNotExist):
            messages.error(request, 'Invalid patient or equipment selected.')
            return redirect('order_edit', pk=pk)

        if order.equipment != equipment or quantity > order.quantity:
            available = equipment.available_quantity
            if order.equipment == equipment:
                available += order.quantity

            if quantity > available:
                messages.error(
                    request, f'Insufficient stock. Only {available} {
                        equipment.name} available.')
                return redirect('order_edit', pk=pk)

        if order.equipment == equipment:
            difference = quantity - order.quantity
            order.equipment.available_quantity -= difference
            order.equipment.save()
        else:
            order.equipment.available_quantity += order.quantity
            order.equipment.save()
            equipment.available_quantity -= quantity
            equipment.save()

        order.patient = patient
        order.equipment = equipment
        order.quantity = quantity
        order.notes = notes
        order.save()

        messages.success(request, 'Order updated successfully!')
        return redirect('therapist_dashboard')

    patients = PatientProfile.objects.filter(
        status='ACTIVE').select_related('user')
    equipment_list = Equipment.objects.all().order_by('name')

    context = {
        'order': order,
        'patients': patients,
        'equipment': equipment_list,
        'is_edit': True,
    }

    return render(request, 'equipment/order_form.html', context)


@login_required
def order_delete(request, pk):
    """
    Soft delete equipment order within 24 hours.

    Access: Therapists and superusers only
    Restriction: Only order creator can delete
    Time window: 24 hours from creation
    Effect: Marks order as deleted (preserves audit trail)
    """
    order = get_object_or_404(EquipmentOrder, pk=pk, deleted_at__isnull=True)

    if request.user.user_type != 'THERAPIST' and not request.user.is_superuser:
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('home')

    if order.created_by != request.user:
        messages.error(request, 'You can only delete your own orders.')
        return redirect('therapist_dashboard')

    time_diff = timezone.now() - order.ordered_at
    if time_diff > timedelta(hours=24):
        messages.error(
            request,
            'Orders can only be deleted within 24 hours of creation.')
        return redirect('therapist_dashboard')

    if request.method == 'POST':
        order.delete(current_user=request.user)
        messages.success(request, 'Order deleted successfully.')
        return redirect('therapist_dashboard')

    context = {'order': order}
    return render(request, 'equipment/order_confirm_delete.html', context)
