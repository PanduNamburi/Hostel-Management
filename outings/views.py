from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Outing
from .forms import OutingForm

from fees.models import Notification
from attendance.models import Attendance
from datetime import timedelta
from django.db import models
from admin_panel.models import ActivityLog
from fees.models import Notification

@login_required
def outing_list(request):
    # Always show only the logged-in user's outings for students (case-insensitive)
    if hasattr(request.user, 'role') and request.user.role.lower() == 'student':
        outings = Outing.objects.filter(student=request.user)
    else:
        outings = Outing.objects.all()

    paginator = Paginator(outings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'outings/outing_list.html', {
        'page_obj': page_obj,
        'is_warden': hasattr(request.user, 'role') and request.user.role.lower() == 'warden',
        'is_student': hasattr(request.user, 'role') and request.user.role.lower() == 'student'
    })

@login_required
def outing_create(request):
    # Anyone logged in can create an outing request now!
    if request.method == 'POST':
        form = OutingForm(request.POST)
        if form.is_valid():
            outing = form.save(commit=False)
            outing.student = request.user
            outing.save()
            messages.success(request, 'Outing request submitted successfully.')
            return redirect('outings:list')
    else:
        form = OutingForm()

    return render(request, 'outings/outing_form.html', {
        'form': form,
        'title': 'Submit Outing Request'
    })

@login_required
def outing_detail(request, pk):
    outing = get_object_or_404(Outing, pk=pk)
    if hasattr(request.user, 'role') and request.user.role.lower() == 'student' and outing.student != request.user:
        messages.error(request, 'You do not have permission to view this outing request.')
        return redirect('outings:list')

    return render(request, 'outings/outing_detail.html', {
        'outing': outing,
        'is_warden': hasattr(request.user, 'role') and request.user.role.lower() == 'warden'
    })

@login_required
def outing_update(request, pk):
    outing = get_object_or_404(Outing, pk=pk)
    if not (hasattr(request.user, 'role') and request.user.role.lower() == 'student') or outing.student != request.user:
        messages.error(request, 'You do not have permission to update this outing request.')
        return redirect('outings:list')

    if outing.status != 'pending':
        messages.error(request, 'Only pending outing requests can be updated.')
        return redirect('outings:detail', pk=pk)

    if request.method == 'POST':
        form = OutingForm(request.POST, instance=outing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Outing request updated successfully.')
            return redirect('outings:detail', pk=pk)
    else:
        form = OutingForm(instance=outing)

    return render(request, 'outings/outing_form.html', {
        'form': form,
        'title': 'Update Outing Request'
    })

@login_required
def outing_approve(request, pk):
    if not (hasattr(request.user, 'role') and request.user.role.lower() == 'warden'):
        messages.error(request, 'Only wardens can approve outing requests.')
        return redirect('outings:list')

    outing = get_object_or_404(Outing, pk=pk)
    if outing.status != 'pending':
        messages.error(request, 'This outing request has already been processed.')
        return redirect('outings:detail', pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            outing.status = 'approved'
            outing.approved_by = request.user
            messages.success(request, 'Outing request approved successfully.')
        else:
            outing.status = 'rejected'
            outing.rejection_reason = request.POST.get('rejection_reason', '')
            messages.success(request, 'Outing request rejected successfully.')
        
        outing.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action=f"{'Approved' if action == 'approve' else 'Rejected'} Outing",
            details=f"For student {outing.student.username} to {outing.destination}"
        )
        
        # Notify the student
        message_notes = f" Reason: {rejection_reason}" if action == 'reject' and rejection_reason else ""
        Notification.objects.create(
            notification_type=Notification.OUTING_APPROVED if action == 'approve' else Notification.OUTING_REJECTED,
            recipient=outing.student,
            message=f"Your outing request to {outing.destination} has been {'approved' if action == 'approve' else 'rejected'}." + message_notes,
            created_by=request.user
        )
        
        return redirect('outings:detail', pk=pk)

    return render(request, 'outings/outing_approve.html', {
        'outing': outing
    })

@login_required
def outing_return(request, pk):
    outing = get_object_or_404(Outing, pk=pk)
    if outing.student != request.user:
        messages.error(request, 'You can only mark your own outings as returned.')
        return redirect('outings:list')

    if outing.status != 'approved' or outing.actual_return_time:
        messages.error(request, 'This outing cannot be marked as returned.')
        return redirect('outings:detail', pk=pk)

    if request.method == 'POST':
        outing.actual_return_time = timezone.now()
        if outing.actual_return_time > outing.end_time:
            messages.warning(request, 'You have returned after the expected time.')
        else:
            messages.success(request, 'Return time recorded successfully.')
        outing.save()
        return redirect('outings:detail', pk=pk)

    return render(request, 'outings/outing_return.html', {
        'outing': outing
    })

 