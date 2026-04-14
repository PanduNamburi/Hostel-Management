from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from admin_panel.models import RoomAllocation

# Create your views here.

@login_required
def room_details(request):
    try:
        allocation = RoomAllocation.objects.get(student=request.user, is_active=True)
    except RoomAllocation.DoesNotExist:
        allocation = None
    
    context = {
        'allocation': allocation
    }
    return render(request, 'students/room_details.html', context)
