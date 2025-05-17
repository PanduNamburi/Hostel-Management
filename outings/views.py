from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Outing
from .forms import OutingForm
from .models import OutingRequest
from fees.models import Notification
from attendance.models import Attendance
from datetime import timedelta
from django.db import models

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
    if request.user.role == 'student' and outing.student != request.user:
        messages.error(request, 'You do not have permission to view this outing request.')
        return redirect('outings:list')

    return render(request, 'outings/outing_detail.html', {
        'outing': outing,
        'is_warden': request.user.role == 'warden'
    })

@login_required
def outing_update(request, pk):
    outing = get_object_or_404(Outing, pk=pk)
    if request.user.role != 'student' or outing.student != request.user:
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
    if request.user.role != 'warden':
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

@login_required
def submit_outing_request(request):
    if request.method == 'POST':
        try:
            # Get form data
            date = request.POST.get('date')
            out_time = request.POST.get('out_time')
            in_time = request.POST.get('in_time')
            reason = request.POST.get('reason')

            # Create outing request
            outing_request = OutingRequest.objects.create(
                student=request.user,
                date=date,
                out_time=out_time,
                in_time=in_time,
                reason=reason,
                status='pending'
            )

            # Create notification
            Notification.objects.create(
                notification_type=Notification.OUTING_REQUESTED,
                outing=outing_request,
                message=f"New outing request from {request.user.get_full_name()} for {date}"
            )

            messages.success(request, 'Your outing request has been submitted successfully!')
            return redirect('outing_status')  # Redirect to status page

        except Exception as e:
            messages.error(request, f'Error submitting outing request: {str(e)}')
            return redirect('submit_outing')

    return render(request, 'outings/submit_outing.html')

@login_required
def outing_status(request):
    # Get all outing requests for the current user
    outing_requests = OutingRequest.objects.filter(student=request.user).order_by('-date', '-out_time')

    # Calculate overall attendance percentage
    attendance_records = Attendance.objects.filter(student=request.user)
    if attendance_records.exists():
        total_percentage = sum([a.attendance_percentage for a in attendance_records])
        overall_attendance_percentage = round(total_percentage / attendance_records.count(), 2)
    else:
        overall_attendance_percentage = 0

    return render(request, 'outings/outing_status.html', {
        'outing_requests': outing_requests,
        'overall_attendance_percentage': overall_attendance_percentage,
    }) 