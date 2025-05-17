from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from admin_panel.models import RoomAllocation

# Create your views here.

@login_required
def dashboard(request):
    if not request.user.is_student:
        return redirect('core:home')
    return render(request, 'students/dashboard.html')

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
