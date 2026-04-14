from django.shortcuts import render, redirect
from django.db import models
from django.contrib.auth.decorators import login_required
from outings.models import Outing
from complaints.models import Complaint
from admin_panel.models import ActivityLog

# Create your views here.

@login_required
def dashboard(request):
    if not request.user.is_warden:
        return redirect('core:home')
    
    # Dashboard Statistics
    from accounts.models import CustomUser
    from admin_panel.models import Room
    from outings.models import Outing
    from complaints.models import Complaint

    total_students = CustomUser.objects.filter(role__iexact='STUDENT').count()
    
    # Calculate available beds across all rooms
    all_rooms = Room.objects.all()
    total_capacity = all_rooms.aggregate(total=models.Sum('capacity'))['total'] or 0
    total_occupancy = all_rooms.aggregate(total=models.Sum('current_occupancy'))['total'] or 0
    available_beds = total_capacity - total_occupancy

    pending_outings_count = Outing.objects.filter(status='pending').count()
    pending_complaints_count = Complaint.objects.filter(status='pending').count()

    # Detailed lists for review
    pending_outings = Outing.objects.filter(status='pending').order_by('-created_at')[:5]
    pending_complaints = Complaint.objects.filter(status='pending').order_by('-created_at')[:5]
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:5]

    return render(request, 'wardens/dashboard.html', {
        'total_students': total_students,
        'available_beds': available_beds,
        'pending_outings_count': pending_outings_count,
        'pending_complaints_count': pending_complaints_count,
        'pending_outings': pending_outings,
        'pending_complaints': pending_complaints,
        'recent_activities': recent_activities
    })
