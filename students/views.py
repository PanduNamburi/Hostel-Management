from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from admin_panel.models import RoomAllocation, ActivityLog
from outings.models import OutingRequest
from complaints.models import Complaint
from fees.models import Payment, Notification
from django.db import models

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
    
    # Fetch recent admin/warden activities
    recent_admin_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:5]
    
    # Fetch notifications and mark unread ones as read
    notifications = Notification.objects.filter(
        models.Q(recipient=user) | models.Q(recipient__isnull=True)
    ).order_by('-created_at')
    
    # Mark unread notifications as read before slicing
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    # Now slice the notifications for display
    notifications = notifications[:10]

    # Combine and sort by date if you want a unified list
    recent_activities = sorted(
        list(recent_complaints) + list(recent_outings) + list(recent_payments),
        key=lambda x: x.created_at,
        reverse=True
    )[:5]

    return render(request, 'students/dashboard.html', {
        'recent_activities': recent_activities,
        'notifications': notifications,
        'recent_admin_activities': recent_admin_activities,
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
