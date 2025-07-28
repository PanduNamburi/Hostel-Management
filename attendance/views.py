from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Attendance
from .forms import AttendanceForm, BulkAttendanceForm
from accounts.models import CustomUser
from django.http import HttpResponseForbidden

def is_admin_or_warden(user):
    return hasattr(user, 'role') and user.role.lower() in ['admin', 'warden']

@login_required
def attendance_list(request):
    user = request.user
    if hasattr(user, 'role') and user.role.lower() == 'student':
        attendance = Attendance.objects.filter(student=user)
    else:
        attendance = Attendance.objects.all()

    total_classes = sum(a.total_periods for a in attendance)
    total_present = sum(a.present_periods for a in attendance)
    total_absent = sum(a.absent_periods for a in attendance)
    attendance_percentage = round((total_present / total_classes) * 100, 2) if total_classes > 0 else 0

    paginator = Paginator(attendance, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'attendance/attendance_list.html', {
        'page_obj': page_obj,
        'can_mark_attendance': request.user.role in ['warden', 'admin'],
        'is_student': hasattr(user, 'role') and user.role.lower() == 'student',
        'total_classes': total_classes,
        'total_present': total_present,
        'total_absent': total_absent,
        'attendance_percentage': attendance_percentage,
    })

@login_required
def mark_attendance(request):
    if request.user.role not in ['warden', 'admin']:
        messages.error(request, 'You do not have permission to mark attendance.')
        return redirect('attendance:list')

    students = CustomUser.objects.filter(role='student')
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST, students=students)
        if form.is_valid():
            date = form.cleaned_data['date']
            for student in students:
                is_present = form.cleaned_data[f'student_{student.id}']
                notes = form.cleaned_data[f'notes_{student.id}']
                
                attendance, created = Attendance.objects.update_or_create(
                    student=student,
                    date=date,
                    defaults={
                        'is_present': is_present,
                        'notes': notes,
                        'marked_by': request.user
                    }
                )
            
            messages.success(request, 'Attendance marked successfully.')
            return redirect('attendance:list')
    else:
        form = BulkAttendanceForm(students=students)

    return render(request, 'attendance/mark_attendance.html', {
        'form': form,
        'students': students
    })

@login_required
def attendance_detail(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.user.role == 'student' and attendance.student != request.user:
        messages.error(request, 'You do not have permission to view this attendance record.')
        return redirect('attendance:list')

    return render(request, 'attendance/attendance_detail.html', {
        'attendance': attendance,
        'can_edit': request.user.role in ['warden', 'admin']
    })

@login_required
def attendance_update(request, pk):
    if request.user.role not in ['warden', 'admin']:
        messages.error(request, 'You do not have permission to update attendance.')
        return redirect('attendance:list')

    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.marked_by = request.user
            attendance.save()
            messages.success(request, 'Attendance updated successfully.')
            return redirect('attendance:detail', pk=pk)
    else:
        form = AttendanceForm(instance=attendance)

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'attendance': attendance
    })

@login_required
def student_list(request):
    if not is_admin_or_warden(request.user):
        return HttpResponseForbidden("You do not have permission to view this page.")
    students = CustomUser.objects.filter(role__iexact='student')
    return render(request, 'attendance/student_list.html', {'students': students})

@login_required
def student_attendance_sheet(request, student_id):
    if not is_admin_or_warden(request.user):
        return HttpResponseForbidden("You do not have permission to view this page.")
    student = get_object_or_404(CustomUser, id=student_id, role__iexact='student')
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    return render(request, 'attendance/student_attendance_sheet.html', {
        'student': student,
        'attendance_records': attendance_records,
    })

@login_required
def mark_attendance_for_student(request, student_id):
    if not is_admin_or_warden(request.user):
        return HttpResponseForbidden("You do not have permission to view this page.")
    student = get_object_or_404(CustomUser, id=student_id, role__iexact='student')
    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(student=student, date=today)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            record = form.save(commit=False)
            record.marked_by = request.user
            record.marked_at = timezone.now()
            record.save()
            messages.success(request, "Attendance marked for today.")
            return redirect('attendance:student_attendance_sheet', student_id=student.id)
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'attendance/mark_attendance_for_student.html', {
        'form': form,
        'student': student,
        'today': today,
    }) 