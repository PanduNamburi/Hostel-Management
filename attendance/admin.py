from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'total_periods', 'absent_periods', 'present_periods', 'attendance_percentage', 'marked_by', 'marked_at', 'notes')
    list_filter = ('date', 'marked_by')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'notes')
    ordering = ('-date', '-marked_at')
    readonly_fields = ('marked_at', 'present_periods', 'attendance_percentage')
    date_hierarchy = 'date' 