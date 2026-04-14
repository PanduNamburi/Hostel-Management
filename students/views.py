from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from admin_panel.models import RoomAllocation, ActivityLog
from outings.models import Outing
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
    recent_outings = Outing.objects.filter(student=user).order_by('-created_at')[:5]
    recent_payments = Payment.objects.filter(student=user).order_by('-created_at')[:5]
    
    # Fetch recent admin/warden activities for announcements (exclude private actions)
    recent_admin_activities = ActivityLog.objects.exclude(
        models.Q(action__icontains='Outing') | models.Q(action__icontains='Complaint')
    ).select_related('user').order_by('-timestamp')[:5]
    
    # Fetch personal notifications (strictly for this user)
    personal_notifications = Notification.objects.filter(
        recipient=user
    ).order_by('-created_at')
    
    # Fetch global announcements (broadcasts where recipient is null)
    broadcast_notifications_qs = Notification.objects.filter(
        recipient__isnull=True
    ).order_by('-created_at')
    
    # Mark unread personal notifications as read
    personal_notifications.filter(is_read=False).update(is_read=True)
    
    # Limit for display
    notifications = personal_notifications[:10]
    broadcast_notifications = broadcast_notifications_qs[:10]

    # Combine and sort by date if you want a unified list
    recent_activities = sorted(
        list(recent_complaints) + list(recent_outings) + list(recent_payments),
        key=lambda x: x.created_at,
        reverse=True
    )[:5]

    return render(request, 'students/dashboard.html', {
        'recent_activities': recent_activities,
        'notifications': notifications,
        'broadcast_notifications': broadcast_notifications,
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
