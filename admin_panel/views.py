from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Room, RoomAllocation
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from outings.models import OutingRequest
from fees.models import FeePayment, Notification
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from .forms import LogActionForm
from .models import ActivityLog

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_admin

def is_admin_or_warden(user):
    return user.is_authenticated and (getattr(user, 'role', None) in ['admin', 'warden'] or getattr(user, 'is_admin', False))

@login_required
def dashboard(request):
    if not request.user.is_admin:
        return redirect('core:home')
    # Fetch the 5 most recent activities
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:5]
    return render(request, 'admin_panel/dashboard.html', {'recent_activities': recent_activities})

@login_required
@user_passes_test(is_admin)
def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'admin_panel/room_list.html', {'rooms': rooms})

@login_required
@user_passes_test(is_admin)
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    allocations = room.allocations.filter(is_active=True)
    return render(request, 'admin_panel/room_detail.html', {
        'room': room,
        'allocations': allocations
    })

@login_required
@user_passes_test(is_admin)
def room_create(request):
    if request.method == 'POST':
        # Handle room creation
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('room_type')
        capacity = request.POST.get('capacity')
        floor = request.POST.get('floor')
        block = request.POST.get('block')
        
        try:
            room = Room.objects.create(
                room_number=room_number,
                room_type=room_type,
                capacity=capacity,
                floor=floor,
                block=block
            )
            messages.success(request, 'Room created successfully!')
            return redirect('admin_panel:room_detail', room_id=room.id)
        except Exception as e:
            messages.error(request, f'Error creating room: {str(e)}')
    
    return render(request, 'admin_panel/room_form.html')

@login_required
@user_passes_test(is_admin)
def room_edit(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        # Handle room update
        room.room_number = request.POST.get('room_number')
        room.room_type = request.POST.get('room_type')
        room.capacity = request.POST.get('capacity')
        room.floor = request.POST.get('floor')
        room.block = request.POST.get('block')
        room.status = request.POST.get('status')
        
        try:
            room.save()
            messages.success(request, 'Room updated successfully!')
            return redirect('admin_panel:room_detail', room_id=room.id)
        except Exception as e:
            messages.error(request, f'Error updating room: {str(e)}')
    
    return render(request, 'admin_panel/room_form.html', {'room': room})

@login_required
@user_passes_test(is_admin)
def allocate_room(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')
        room_id = request.POST.get('room')
        
        try:
            student = User.objects.get(id=student_id)
            room = Room.objects.get(id=room_id)
            
            # Check if room is available
            if room.current_occupancy >= room.capacity:
                messages.error(request, 'Selected room is already full.')
                return redirect('allocate_room')
            
            # Check if student already has a room
            existing_allocation = RoomAllocation.objects.filter(student=student, is_active=True).first()
            if existing_allocation:
                messages.error(request, f'Student already has a room allocated: {existing_allocation.room.room_number}')
                return redirect('allocate_room')
            
            # Create room allocation
            RoomAllocation.objects.create(
                student=student,
                room=room,
                allocated_by=request.user
            )
            
            # Update room occupancy
            room.current_occupancy += 1
            room.save()
            
            messages.success(request, f'Room {room.room_number} allocated to {student.get_full_name() or student.username}')
            return redirect('room_list')
            
        except (User.DoesNotExist, Room.DoesNotExist):
            messages.error(request, 'Invalid student or room selected.')
            return redirect('allocate_room')
    
    # Get available rooms and students
    available_rooms = Room.objects.filter(current_occupancy__lt=models.F('capacity'))
    students = User.objects.filter(role='student')
    
    return render(request, 'admin_panel/allocate_room.html', {
        'rooms': available_rooms,
        'students': students
    })

@login_required
@user_passes_test(is_admin)
def deallocate_room(request, allocation_id):
    allocation = get_object_or_404(RoomAllocation, id=allocation_id)
    
    if request.method == 'POST':
        try:
            # Update allocation
            allocation.is_active = False
            allocation.save()
            
            # Update room occupancy
            room = allocation.room
            room.current_occupancy -= 1
            if room.current_occupancy < room.capacity:
                room.status = 'AVAILABLE'
            room.save()
            
            messages.success(request, 'Room deallocated successfully!')
        except Exception as e:
            messages.error(request, f'Error deallocating room: {str(e)}')
    
    return redirect('admin_panel:room_detail', room_id=allocation.room.id)

@login_required
@user_passes_test(is_admin_or_warden)
def attendance_management(request):
    # Redirect to the attendance app's student list or bulk mark page
    return redirect('attendance:student_list')
    # Or, to bulk mark: return redirect('attendance:mark')

@login_required
@user_passes_test(is_admin_or_warden)
def outing_approval(request):
    if request.method == 'POST':
        outing_id = request.POST.get('outing_id')
        action = request.POST.get('action')
        rejection_reason = request.POST.get('rejection_reason', '')
        outing = get_object_or_404(OutingRequest, id=outing_id, status='pending')
        student_email = outing.student.email
        student_name = outing.student.get_full_name() or outing.student.username
        if action == 'approve':
            outing.status = 'approved'
            outing.approved_by = request.user
            outing.rejection_reason = ''
            messages.success(request, f'Outing request for {student_name} approved.')
            # Send email notification
            send_mail(
                subject='Outing Request Approved',
                message=f"Dear {student_name}, your outing request for {outing.date} has been approved.",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@hostel.com'),
                recipient_list=[student_email],
                fail_silently=True,
            )
        elif action == 'reject':
            outing.status = 'rejected'
            outing.approved_by = request.user
            outing.rejection_reason = rejection_reason
            messages.success(request, f'Outing request for {student_name} rejected.')
            # Send email notification
            send_mail(
                subject='Outing Request Rejected',
                message=f"Dear {student_name}, your outing request for {outing.date} has been rejected. Reason: {rejection_reason}",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@hostel.com'),
                recipient_list=[student_email],
                fail_silently=True,
            )
        outing.save()
        return redirect('admin_panel:outing_approval')

    pending_outings = OutingRequest.objects.filter(status='pending').order_by('-date', '-out_time')
    return render(request, 'admin_panel/outing_approval.html', {
        'pending_outings': pending_outings
    })

@login_required
@user_passes_test(is_admin_or_warden)
def complaints_management(request):
    # Redirect to the complaints app's list page
    return redirect('complaints:list')

@login_required
@user_passes_test(is_admin_or_warden)
def fee_approval(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        action = request.POST.get('action')
        payment = get_object_or_404(FeePayment, id=payment_id, status='pending')
        student_email = payment.fee_record.student.email
        student_name = payment.fee_record.student.get_full_name() or payment.fee_record.student.username
        if action == 'approve':
            payment.status = 'approved'
            messages.success(request, f'Payment of ₹{payment.amount} for {student_name} approved.')
            # Send email notification
            send_mail(
                subject='Fee Payment Approved',
                message=f"Dear {student_name}, your payment of ₹{payment.amount} has been approved.",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@hostel.com'),
                recipient_list=[student_email],
                fail_silently=True,
            )
        elif action == 'reject':
            payment.status = 'rejected'
            messages.success(request, f'Payment of ₹{payment.amount} for {student_name} rejected.')
            # Send email notification
            send_mail(
                subject='Fee Payment Rejected',
                message=f"Dear {student_name}, your payment of ₹{payment.amount} has been rejected.",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@hostel.com'),
                recipient_list=[student_email],
                fail_silently=True,
            )
        payment.save()
        return redirect('admin_panel:fee_approval')

    pending_payments = FeePayment.objects.filter(status='pending').order_by('-payment_date')
    return render(request, 'admin_panel/fee_approval.html', {
        'pending_payments': pending_payments
    })

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'warden'] or u.is_superuser)
def log_activity(request):
    if request.method == 'POST':
        form = LogActionForm(request.POST)
        if form.is_valid():
            action_type = form.cleaned_data['action_type']
            action = form.cleaned_data['action']
            details = form.cleaned_data['details']
            recipient = form.cleaned_data['recipient']

            if action_type == 'activity':
                ActivityLog.objects.create(
                    user=request.user,
                    action=action,
                    details=details
                )
                print(f"Activity logged by {request.user.username}: {action}")
            elif action_type == 'notification':
                if recipient:
                    Notification.objects.create(
                        notification_type=Notification.CUSTOM,
                        message=details,
                        recipient=recipient,
                        created_by=request.user
                    )
                    print(f"Notification created for {recipient.username}")
                else:
                    students = User.objects.filter(role='student')
                    for student in students:
                        Notification.objects.create(
                            notification_type=Notification.CUSTOM,
                            message=details,
                            recipient=student,
                            created_by=request.user
                        )
                        print(f"Notification created for {student.username}")
            return redirect('admin_panel:dashboard')
    else:
        form = LogActionForm()
    return render(request, 'admin_panel/log_activity.html', {'form': form})
