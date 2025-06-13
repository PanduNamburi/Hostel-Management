from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from admin_panel.models import RoomAllocation
from outings.models import OutingRequest
from complaints.models import Complaint
from fees.models import Payment

# Create your views here.

@login_required
def dashboard(request):
    if not request.user.is_student:
        return redirect('core:home')
    user = request.user

    # Fetch recent activities for the logged-in student
    recent_complaints = Complaint.objects.filter(created_by=user).order_by('-created_at')[:5]
    recent_outings = OutingRequest.objects.filter(student=user).order_by('-created_at')[:5]
    recent_payments = Payment.objects.filter(student=user).order_by('-created_at')[:5]

    # Combine and sort by date if you want a unified list
    recent_activities = sorted(
        list(recent_complaints) + list(recent_outings) + list(recent_payments),
        key=lambda x: x.created_at,
        reverse=True
    )[:5]

    return render(request, 'students/dashboard.html', {
        'recent_activities': recent_activities,
    })

@login_required
def room_details(request):
    if not request.user.is_student:
        return redirect('core:home')
    
    # Get the student's active room allocation
    allocation = RoomAllocation.objects.filter(
        student=request.user,
        is_active=True
    ).first()
    
    return render(request, 'students/room_details.html', {
        'allocation': allocation
    })
